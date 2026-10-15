"""P1 domain workflow & specialist: ``ResearchWorkflow``, ``run_research``, ``verify_research``, and ``RESEARCH_SPECIALIST``."""

from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.researcher_agent import (
    ResearcherAgent,
    make_researcher_agent,
)
from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.graphs.research_graph import (
    ResearchGraph,
    build_research_graph,
)
from agentlab.nodes.claim_check_node import cap_claims, check_claims, unsupported_count
from agentlab.nodes.research_node import read_research_run
from agentlab.nodes.source_route_node import Decide
from agentlab.schemas.input.research_input_schema import ResearchInput, ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ClaimVerdict,
    ResearchPlan,
    ResearchReport,
)
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
)
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals
from agentlab.workflows.specialist_workflow import (
    SpecialistSpec,
    Workflow,
    WorkflowOverallState,
)

DEFAULT_RESEARCH_DESCRIPTION = (
    "Plans, routes across web/academic/corpus sources, researches sub-questions in "
    "parallel, and verifies every claim against the source documents read."
)


def verify_research(
    state: dict[str, Any],
    options: ResearchOptions | None = None,
) -> ResearchReport | None:
    """Check the agent's draft against the documents its tools returned: the report, or None."""
    run = read_research_run(state)
    if run.draft is None:
        return None
    report = check_claims(run.draft, run.documents)
    if options is not None:
        max_claims = DEPTH_BUDGETS[options.depth].claims
        if len(report.claims) > max_claims:
            report, _ = cap_claims(report, max_claims)
    return report


def render_research_report(report: ResearchReport) -> str:
    """Format a verified ``ResearchReport`` as concise markdown for a coordinator or tool caller."""
    lines = [
        f"### Research Summary (Confidence: {report.confidence:.2f})",
        report.summary,
    ]
    if report.claims:
        lines.append("\n**Verified Claims:**")
        for claim in report.claims:
            lines.append(f"- [{claim.status.upper()}] {claim.text}")
    return "\n".join(lines)


def make_research_graph(
    agent: ResearcherAgent | CompiledStateGraph | Any = None,
    *,
    options: ResearchOptions | None = None,
    plan_chain: Runnable[Any, ResearchPlan] | None = None,
    route_decide: Decide | None = None,
    decide: Decide | None = None,
    verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
) -> ResearchGraph:
    """Compile the research graph around an injected or default researcher agent."""
    resolved_agent = (
        agent if agent is not None else make_researcher_agent(options=options)
    )
    return build_research_graph(
        resolved_agent,
        plan_chain=plan_chain,
        decide=decide,
        verdict_chain=verdict_chain,
        route_decide=route_decide,
        checkpointer=checkpointer,
    )


class ResearchWorkflowState(WorkflowOverallState[ResearchReport]):
    """Overall state for the Research workflow graph."""

    topic: str
    options: ResearchOptions | None


class ResearchWorkflow(Workflow[ResearchInput, ResearchReport]):
    """Active Rung-2 Research domain workflow wrapping ``ResearchGraph``."""

    spec = SpecialistSpec(
        name="research",
        description=DEFAULT_RESEARCH_DESCRIPTION,
        input_schema=ResearchInput,
        report_schema=ResearchReport,
    )

    def __init__(
        self,
        agent: ResearcherAgent | CompiledStateGraph | Any = None,
        *,
        graph: ResearchGraph | CompiledStateGraph | Any = None,
        options: ResearchOptions | None = None,
        plan_chain: Runnable[Any, ResearchPlan] | None = None,
        route_decide: Decide | None = None,
        decide: Decide | None = None,
        verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
    ) -> None:
        self.options = options
        self.checkpointer = checkpointer
        self._agent = agent
        self._graph = graph
        self._plan_chain = plan_chain
        self._route_decide = route_decide
        self._decide = decide
        self._verdict_chain = verdict_chain
        self._research_graph: CompiledStateGraph | None = None

    @property
    def research_graph(self) -> CompiledStateGraph:
        if self._research_graph is None:
            if self._graph is not None:
                self._research_graph = self._graph
            elif self._agent is not None:
                is_graph = getattr(self._agent, "_is_research_graph", False) or (
                    hasattr(self._agent, "nodes")
                    and isinstance(getattr(self._agent, "nodes", None), dict)
                    and "plan" in self._agent.nodes
                    and "check" in self._agent.nodes
                )
                if is_graph:
                    self._research_graph = self._agent
                else:
                    self._research_graph = make_research_graph(
                        agent=self._agent,
                        options=self.options,
                        plan_chain=self._plan_chain,
                        route_decide=self._route_decide,
                        decide=self._decide,
                        verdict_chain=self._verdict_chain,
                        checkpointer=self.checkpointer,
                    )
            else:
                self._research_graph = make_research_graph(
                    options=self.options,
                    plan_chain=self._plan_chain,
                    route_decide=self._route_decide,
                    decide=self._decide,
                    verdict_chain=self._verdict_chain,
                    checkpointer=self.checkpointer,
                )
        return self._research_graph

    def render(self, report: ResearchReport) -> str:
        return render_research_report(report)

    def build_graph(self) -> CompiledStateGraph:
        def _research_step(
            state: ResearchWorkflowState,
            config: RunnableConfig | None = None,
        ) -> dict[str, Any]:
            resolved_options = state.get("options") or self.options
            active_checkpointer = self.checkpointer or getattr(
                self.research_graph, "checkpointer", None
            )
            invoke_config = config or (
                new_delegation_config() if active_checkpointer is not None else None
            )
            sub_state: dict[str, Any] = (
                self.research_graph.invoke(
                    {"topic": state["topic"], "options": resolved_options},
                    config=invoke_config,
                )
                if invoke_config is not None
                else self.research_graph.invoke(
                    {"topic": state["topic"], "options": resolved_options}
                )
            )

            problems = list(sub_state.get("problems", []))
            if waiting_in_graph := pending_approvals(sub_state):
                approval_msg = f"Stopped before finishing: waiting for approval of {waiting_in_graph}."
                if not any("waiting for approval" in problem for problem in problems):
                    problems.append(approval_msg)

            report: ResearchReport | None = sub_state.get("report")
            if report is None:
                return {
                    "report": None,
                    "problems": problems,
                    "provenance": [],
                }

            unsupported = unsupported_count(report)
            if not report.claims:
                problems.append("The report has no claims.")
            elif unsupported:
                problems.append(
                    f"{unsupported} of {len(report.claims)} claims are not supported by the "
                    "pages the agent read."
                )

            provenance = [
                Provenance(
                    kind=report.citation_kinds.get(citation.url, "web"),
                    ref=citation.url,
                    title=citation.title,
                )
                for citation in report.citations
            ]
            return {
                "report": report,
                "problems": problems,
                "provenance": provenance,
            }

        graph = StateGraph(ResearchWorkflowState)
        graph.add_node("research_step", _research_step)
        graph.add_node("pack_result", self.pack_node)
        graph.add_edge(START, "research_step")
        graph.add_edge("research_step", "pack_result")
        graph.add_edge("pack_result", END)
        return graph.compile(checkpointer=self.checkpointer)


def run_research(
    engine: ResearchGraph | ResearcherAgent | CompiledStateGraph | Any,
    topic: str,
    options: ResearchOptions | None = None,
    *,
    plan_chain: Runnable[Any, ResearchPlan] | None = None,
    route_decide: Decide | None = None,
    decide: Decide | None = None,
    verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
    config: RunnableConfig | None = None,
) -> SpecialistResult[ResearchReport]:
    """Research ``topic`` through the research workflow and return the specialist envelope."""
    is_graph = getattr(engine, "_is_research_graph", False) or (
        hasattr(engine, "nodes")
        and isinstance(getattr(engine, "nodes", None), dict)
        and "plan" in engine.nodes
        and "check" in engine.nodes
    )
    if is_graph:
        workflow = ResearchWorkflow(
            graph=engine,
            options=options,
            plan_chain=plan_chain,
            route_decide=route_decide,
            decide=decide,
            verdict_chain=verdict_chain,
            checkpointer=checkpointer,
        )
    else:
        workflow = ResearchWorkflow(
            agent=engine,
            options=options,
            plan_chain=plan_chain,
            route_decide=route_decide,
            decide=decide,
            verdict_chain=verdict_chain,
            checkpointer=checkpointer,
        )
    return workflow.run(topic=topic, options=options)


def make_research_specialist(
    engine: ResearchGraph | ResearcherAgent | CompiledStateGraph | Any = None,
    *,
    options: ResearchOptions | None = None,
) -> ResearchWorkflow:
    """Create a Research Workflow bound to an engine or lazy default."""
    if engine is None:
        return ResearchWorkflow(options=options)
    is_graph = getattr(engine, "_is_research_graph", False) or (
        hasattr(engine, "nodes")
        and isinstance(getattr(engine, "nodes", None), dict)
        and "plan" in engine.nodes
        and "check" in engine.nodes
    )
    if is_graph:
        return ResearchWorkflow(graph=engine, options=options)
    return ResearchWorkflow(agent=engine, options=options)


RESEARCH_SPECIALIST = make_research_specialist()
research_workflow = RESEARCH_SPECIALIST
