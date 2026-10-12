"""P1 domain workflow & specialist: ``run_research``, ``verify_research``, and ``RESEARCH_SPECIALIST``."""

from typing import Any

from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.researcher_agent import make_researcher_agent
from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.graphs.research_graph import build_research_graph
from agentlab.nodes.claim_check_node import cap_claims, check_claims, unsupported_count
from agentlab.nodes.research_node import read_research_run
from agentlab.nodes.source_route_node import Decide
from agentlab.schemas.input.research_input_schema import ResearchInput, ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ResearchPlan,
    ResearchReport,
)
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
)
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals
from agentlab.workflows.specialist_workflow import Specialist

DEFAULT_RESEARCH_DESCRIPTION = (
    "Plans, routes across web/academic/corpus sources, researches sub-questions in "
    "parallel, and verifies every claim against the source documents read."
)


def verify_research(
    state: dict[str, Any],
    options: ResearchOptions | None = None,
) -> ResearchReport | None:
    """Check the agent's draft against the documents its tools returned: the report, or None.

    Status and confidence come from this check, never from the model. Callers that run the
    agent themselves (the apps, with their approval loops) pass its final state here; when
    ``options`` are given, the depth's claim cap is enforced by evidence just as in the graph.
    """
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


def run_research(
    agent: CompiledStateGraph,
    topic: str,
    options: ResearchOptions | None = None,
    *,
    plan_chain: Runnable[Any, ResearchPlan] | None = None,
    route_decide: Decide | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
    config: RunnableConfig | None = None,
) -> SpecialistResult[ResearchReport]:
    """Research ``topic`` through the research graph and return the specialist envelope.

    Build the agent with the same ``options`` (``make_researcher_agent(options=...)``): the
    agent holds the per-run search and read budgets, and the graph holds the plan and the claim
    cap. Without ``options`` it is one run on the topic, no plan and no cap. With them, the
    planner splits the topic into sub-questions (R1 topic 2), the router picks each one's sources
    (R1 topic 3), and each is researched on its own run, in parallel, so every claim is checked
    against the documents its own run's tools returned (``graphs/research_graph.py``).
    """
    graph = build_research_graph(
        agent,
        plan_chain=plan_chain,
        route_decide=route_decide,
        checkpointer=checkpointer,
    )
    invoke_config = config or (
        new_delegation_config() if checkpointer is not None else None
    )
    try:
        state = (
            graph.invoke(
                {"topic": topic, "options": options},
                config=invoke_config,
            )
            if invoke_config is not None
            else graph.invoke({"topic": topic, "options": options})
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[ResearchReport](
            specialist="research",
            status="failed",
            reason=failure_reason(error),
        )
    problems = list(state.get("problems", []))
    if waiting_in_graph := pending_approvals(state):
        approval_msg = (
            f"Stopped before finishing: waiting for approval of {waiting_in_graph}."
        )
        if not any("waiting for approval" in problem for problem in problems):
            problems.append(approval_msg)
    report: ResearchReport | None = state.get("report")
    if report is None:
        waiting = any("waiting for approval" in problem for problem in problems)
        return SpecialistResult[ResearchReport](
            specialist="research",
            status="partial" if waiting else "failed",
            reason=" ".join(problems),
        )
    unsupported = unsupported_count(report)
    if not report.claims:
        problems.append("The report has no claims.")
    elif unsupported:
        problems.append(
            f"{unsupported} of {len(report.claims)} claims are not supported by the "
            "pages the agent read."
        )
    return SpecialistResult[ResearchReport](
        specialist="research",
        status="partial" if problems else "ok",
        reason=" ".join(problems),
        output=report,
        provenance=[
            Provenance(
                kind=report.citation_kinds.get(citation.url, "web"),
                ref=citation.url,
                title=citation.title,
            )
            for citation in report.citations
        ],
    )


RESEARCH_SPECIALIST = Specialist[ResearchInput, ResearchReport](
    name="research",
    description=DEFAULT_RESEARCH_DESCRIPTION,
    input_schema=ResearchInput,
    report_schema=ResearchReport,
    run=run_research,
    render=render_research_report,
    default_target=make_researcher_agent,
)
