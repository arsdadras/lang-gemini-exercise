"""P1's boundary: ``run_research`` returns the specialist envelope; the subagent spec serves coordinators."""

from typing import Any

from deepagents import SubAgent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from agentlab.nodes.claim_check_node import check_claims, unsupported_count
from agentlab.prompts.subagents_prompt import RESEARCHER_SUBAGENT_PROMPT
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
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals

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


def run_research(agent: Runnable, topic: str) -> SpecialistResult[ResearchReport]:
    """Research ``topic`` with an injected P1 agent (``make_web_researcher_agent``) on a fresh thread."""
    try:
        state = agent.invoke(
            {"messages": [HumanMessage(content=topic)]},
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="failed",
            reason=failure_reason(error),
        )
    if waiting := pending_approvals(state):
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="partial",
            reason=f"Stopped before finishing: waiting for approval of {waiting}.",
        )
    try:
        report = verify_research(state)
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="failed",
            reason=failure_reason(error),
        )
    if report is None:
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="failed",
            reason="No report was produced.",
        )
    unsupported = unsupported_count(report)
    if not report.claims:
        status, reason = "partial", "The report has no claims."
    elif unsupported:
        status = "partial"
        reason = (
            f"{unsupported} of {len(report.claims)} claims are not supported by the "
            "pages the agent read."
        )
    else:
        status, reason = "ok", ""
    return SpecialistResult[ResearchReport](
        specialist=RESEARCH_SPECIALIST,
        status=status,
        reason=reason,
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
