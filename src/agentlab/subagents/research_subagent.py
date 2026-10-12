"""P1 subagent adapter over ``workflows/research_workflow.py`` (ADR-0033)."""

from typing import Any

from deepagents import CompiledSubAgent

from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.utils.subagent_util import specialist_subagent
from agentlab.workflows.research_workflow import (
    DEFAULT_RESEARCH_DESCRIPTION,
    RESEARCH_SPECIALIST,
    RESEARCH_SPECIALIST_SPEC,
    render_research_report,
    run_research,
    verify_research,
)

RESEARCHER_SUBAGENT_NAME = "researcher"


def make_researcher_subagent(
    agent: Any = None,
    *,
    options: ResearchOptions | None = None,
    name: str = RESEARCHER_SUBAGENT_NAME,
    description: str = DEFAULT_RESEARCH_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap P1's ``run_research`` workflow as a ``CompiledSubAgent`` for coordinators.

    Delegated research runs execute the full R1 plan -> route -> research -> claim-check
    workflow and return the verified ``ResearchReport`` envelope as text.
    """
    return specialist_subagent(
        name,
        description,
        lambda task: run_research(task, options, agent=agent),
        render=render_research_report,
    )


__all__ = [
    "RESEARCHER_SUBAGENT_NAME",
    "RESEARCH_SPECIALIST",
    "RESEARCH_SPECIALIST_SPEC",
    "make_researcher_subagent",
    "render_research_report",
    "run_research",
    "verify_research",
]
