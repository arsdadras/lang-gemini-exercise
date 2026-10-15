"""P1 domain workflow & specialist: ``ResearchWorkflow``, ``run_research``, ``verify_research``, and ``RESEARCH_SPECIALIST``."""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.researcher_agent import ResearcherAgent
from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.graphs.research_graph import (
    DEFAULT_RESEARCH_DESCRIPTION,
    RESEARCH_SPEC,
    ResearchGraph,
    make_research_graph,
)
from agentlab.nodes.claim_check_node import cap_claims, check_claims
from agentlab.nodes.research_node import read_research_run
from agentlab.nodes.source_route_node import Decide
from agentlab.schemas.input.research_input_schema import ResearchInput, ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ClaimVerdict,
    ResearchPlan,
    ResearchReport,
)
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.workflows.specialist_workflow import Workflow

__all__ = [
    "DEFAULT_RESEARCH_DESCRIPTION",
    "RESEARCH_SPECIALIST",
    "ResearchWorkflow",
    "make_research_graph",
    "make_research_specialist",
    "render_research_report",
    "research_workflow",
    "run_research",
    "verify_research",
]


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


class ResearchWorkflow(Workflow[ResearchInput, ResearchReport]):
    """Active Rung-2 Research domain workflow wrapping ``ResearchGraph`` as a Runnable facade."""

    spec = RESEARCH_SPEC

    def __init__(
        self,
        graph: ResearchGraph | CompiledStateGraph | Any | None = None,
        *,
        options: ResearchOptions | None = None,
    ) -> None:
        super().__init__(graph)
        self.options = options

    def build_default_graph(self) -> CompiledStateGraph:
        return make_research_graph(options=self.options)

    @classmethod
    def from_graph(
        cls,
        graph: ResearchGraph | CompiledStateGraph | Any,
        *,
        options: ResearchOptions | None = None,
    ) -> ResearchWorkflow:
        """Create a ResearchWorkflow directly wrapping an existing compiled ResearchGraph."""
        return cls(graph=graph, options=options)

    @classmethod
    def from_agent(
        cls,
        agent: ResearcherAgent | CompiledStateGraph | Any = None,
        *,
        options: ResearchOptions | None = None,
        plan_chain: Runnable[Any, ResearchPlan] | None = None,
        route_decide: Decide | None = None,
        decide: Decide | None = None,
        verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
        checkpointer: BaseCheckpointSaver | None = None,
    ) -> ResearchWorkflow:
        """Create a ResearchWorkflow by compiling a ResearchGraph around the given agent."""
        graph = make_research_graph(
            agent=agent,
            options=options,
            plan_chain=plan_chain,
            route_decide=route_decide,
            decide=decide,
            verdict_chain=verdict_chain,
            checkpointer=checkpointer,
        )
        return cls(graph=graph, options=options)

    def render(self, report: ResearchReport) -> str:
        return render_research_report(report)


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
    if getattr(engine, "_is_research_graph", False):
        workflow = ResearchWorkflow.from_graph(engine, options=options)
    else:
        workflow = ResearchWorkflow.from_agent(
            agent=engine,
            options=options,
            plan_chain=plan_chain,
            route_decide=route_decide,
            decide=decide,
            verdict_chain=verdict_chain,
            checkpointer=checkpointer,
        )
    return workflow.invoke(
        {"topic": topic, "options": options},
        config=config,
    )["result"]


def make_research_specialist(
    engine: ResearchGraph | ResearcherAgent | CompiledStateGraph | Any = None,
    *,
    options: ResearchOptions | None = None,
) -> ResearchWorkflow:
    """Create a Research Workflow bound to an engine or lazy default."""
    if engine is None:
        return ResearchWorkflow(options=options)
    if getattr(engine, "_is_research_graph", False):
        return ResearchWorkflow.from_graph(engine, options=options)
    return ResearchWorkflow.from_agent(engine, options=options)


RESEARCH_SPECIALIST = make_research_specialist()
research_workflow = RESEARCH_SPECIALIST
