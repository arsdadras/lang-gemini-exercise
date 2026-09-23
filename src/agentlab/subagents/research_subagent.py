"""P1's boundary: ``run_research`` returns the specialist envelope; the subagent spec serves coordinators."""

from deepagents import SubAgent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from agentlab.prompts.subagents_prompt import RESEARCHER_SUBAGENT_PROMPT
from agentlab.schemas.output.research_output_schema import (
    ResearchFindings,
    ResearchReport,
)
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
)
from agentlab.tools.web_search_tool import make_web_search_tool
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals

RESEARCH_SPECIALIST = "research"
RESEARCHER_SUBAGENT_NAME = "researcher"


def run_research(agent: Runnable, topic: str) -> SpecialistResult[ResearchReport]:
    """Research ``topic`` with an injected P1 agent (``make_web_researcher_agent``) on a fresh thread."""
    state = agent.invoke(
        {"messages": [HumanMessage(content=topic)]},
        config=new_delegation_config(),
    )
    if waiting := pending_approvals(state):
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="partial",
            reason=f"Stopped before finishing: waiting for approval of {waiting}.",
        )
    report: ResearchReport | None = state.get("structured_response")
    if report is None:
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="failed",
            reason="No report was produced.",
        )
    return SpecialistResult[ResearchReport](
        specialist=RESEARCH_SPECIALIST,
        status="ok" if report.sources else "partial",
        reason="" if report.sources else "The report cites no sources.",
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
