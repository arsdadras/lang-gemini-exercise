"""P1's boundary: ``run_research`` returns the specialist envelope; the subagent spec serves coordinators."""

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from deepagents import SubAgent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.nodes.claim_check_node import check_claims, unsupported_count
from agentlab.nodes.research_plan_node import plan_research
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


def _research_one(agent: Runnable, question: str) -> dict[str, Any] | Exception:
    """One run of the agent on ``question``: its final state, or the external failure it hit."""
    try:
        return agent.invoke(
            {"messages": [HumanMessage(content=question)]},
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return error


def _merge(
    topic: str, drafts: list[ResearchDraft], max_claims: int | None
) -> ResearchDraft:
    """One draft from the sub-question drafts: claims concatenated and capped, sources deduped."""
    claims = [claim for draft in drafts for claim in draft.claims]
    sources = {source.url: source for draft in drafts for source in draft.sources}
    return ResearchDraft(
        topic=topic,
        summary=" ".join(draft.summary for draft in drafts),
        claims=claims if max_claims is None else claims[:max_claims],
        sources=list(sources.values()),
    )


def run_research(
    agent: Runnable,
    topic: str,
    options: ResearchOptions | None = None,
    *,
    plan_chain: Runnable | None = None,
) -> SpecialistResult[ResearchReport]:
    """Research ``topic`` with an injected P1 agent on fresh threads.

    Build the agent with the same ``options`` (``make_web_researcher_agent(options=...)``): the
    agent holds the per-run search and read budgets, and this boundary holds the plan and the
    claim cap. Without ``options`` it is one run on the topic, no plan and no cap. With them, the
    planner splits the topic into sub-questions (R1 topic 2), researched in parallel, each on its
    own run, so every claim is checked against the pages its own run read.
    """
    try:
        questions = (
            [topic]
            if options is None
            else plan_research(topic, options, plan_chain=plan_chain)
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="failed",
            reason=failure_reason(error),
        )
    if len(questions) == 1:
        outcomes = [_research_one(agent, questions[0])]
    else:
        with ThreadPoolExecutor(max_workers=len(questions)) as pool:
            outcomes = list(pool.map(lambda q: _research_one(agent, q), questions))

    drafts: list[ResearchDraft] = []
    pages: dict[str, str] = {}
    problems: list[str] = []
    for question, outcome in zip(questions, outcomes, strict=True):
        label = f"'{question}': " if len(questions) > 1 else ""
        if isinstance(outcome, Exception):
            problems.append(label + failure_reason(outcome))
        elif waiting := pending_approvals(outcome):
            problems.append(
                f"{label}Stopped before finishing: waiting for approval of {waiting}."
            )
        elif (draft := outcome.get("structured_response")) is None:
            problems.append(label + "No report was produced.")
        else:
            drafts.append(draft)
            pages.update(pages_read(outcome.get("messages", [])))
    if not drafts:
        waiting = any("waiting for approval" in problem for problem in problems)
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="partial" if waiting else "failed",
            reason=" ".join(problems),
        )

    max_claims = None if options is None else DEPTH_BUDGETS[options.depth].claims
    total_claims = sum(len(draft.claims) for draft in drafts)
    if max_claims is not None and total_claims > max_claims:
        problems.append(
            f"{total_claims - max_claims} claims over the cap of {max_claims} were dropped."
        )
    try:
        report = check_claims(_merge(topic, drafts, max_claims), pages)
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[ResearchReport](
            specialist=RESEARCH_SPECIALIST,
            status="failed",
            reason=failure_reason(error),
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
