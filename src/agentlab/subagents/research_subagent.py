"""P1's boundary: ``run_research`` returns the specialist envelope; the subagent spec serves coordinators."""

from typing import Any

from deepagents import SubAgent
from langchain_core.runnables import Runnable

from agentlab.graphs.research_graph import build_research_graph
from agentlab.nodes.claim_check_node import check_claims, unsupported_count
from agentlab.prompts.subagents_prompt import RESEARCHER_SUBAGENT_PROMPT
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ResearchDraft,
    ResearchFindings,
    ResearchReport,
)
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
)
from agentlab.tools.read_page_tool import pages_read
from agentlab.tools.web_search_tool import make_web_search_tool
from agentlab.utils.failure_util import failure_kind, failure_reason

RESEARCH_SPECIALIST = "research"
RESEARCHER_SUBAGENT_NAME = "researcher"


def verify_research(state: dict[str, Any]) -> ResearchReport | None:
    """Check the agent's draft against the pages it read: the checked report, or ``None``.

    Status and confidence come from this check, never from the model. Callers that run the
    agent themselves (the apps, with their approval loops) pass its final state here.
    """
    draft: ResearchDraft | None = state.get("structured_response")
    if draft is None:
        return None
    return check_claims(draft, pages_read(state.get("messages", [])))


def run_research(
    agent: Runnable,
    topic: str,
    options: ResearchOptions | None = None,
    *,
    plan_chain: Runnable | None = None,
) -> SpecialistResult[ResearchReport]:
    """Research ``topic`` through the research graph and return the specialist envelope.

    Build the agent with the same ``options`` (``make_web_researcher_agent(options=...)``): the
    agent holds the per-run search and read budgets, and the graph holds the plan and the claim
    cap. Without ``options`` it is one run on the topic, no plan and no cap. With them, the
    planner splits the topic into sub-questions (R1 topic 2), researched in parallel, each on its
    own run, so every claim is checked against the pages its own run read
    (``graphs/research_graph.py``).
    """
    graph = build_research_graph(agent, plan_chain=plan_chain)
    try:
        state = graph.invoke({"topic": topic, "options": options})
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="failed",
            reason=failure_reason(error),
        )
    problems = list(state.get("problems", []))
    report: ResearchReport | None = state.get("report")
    if report is None:
        waiting = any("waiting for approval" in problem for problem in problems)
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
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
        specialist=RESEARCH_SPECIALIST,
        status="partial" if problems else "ok",
        reason=" ".join(problems),
        output=report,
        provenance=[
            Provenance(kind="web", ref=source.url, title=source.title)
            for source in report.sources
        ],
    )


def make_researcher_subagent() -> SubAgent:
    """Build the researcher spec.

    DeepAgents compiles the spec into a child agent with its own context window,
    so each sub-question is researched without cluttering the parent's conversation.
    """
    return {
        "name": RESEARCHER_SUBAGENT_NAME,
        "description": (
            "Researches one specific sub-question using web_search and "
            "returns structured findings with sources. Delegate a single, "
            "narrow sub-question at a time, not the whole topic."
        ),
        "system_prompt": RESEARCHER_SUBAGENT_PROMPT,
        "tools": [make_web_search_tool()],
        "response_format": ResearchFindings,
    }
