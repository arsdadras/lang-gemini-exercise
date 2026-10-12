"""P1 subagent adapter over ``workflows/research_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.researcher_agent import make_researcher_agent
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.workflows.research_workflow import (
    DEFAULT_RESEARCH_DESCRIPTION,
    RESEARCH_SPECIALIST,
)

RESEARCHER_SUBAGENT_NAME = "researcher"


def make_researcher_subagent(
    agent: CompiledStateGraph | None = None,
    *,
    options: ResearchOptions | None = None,
    name: str = RESEARCHER_SUBAGENT_NAME,
    description: str = DEFAULT_RESEARCH_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap P1's ``run_research`` workflow as a ``CompiledSubAgent`` for coordinators.

    Delegated research runs execute the full R1 plan -> route -> research -> claim-check
    workflow and return the verified ``ResearchReport`` envelope as text.
    """
    resolved_agent = (
        agent if agent is not None else make_researcher_agent(options=options)
    )
    return RESEARCH_SPECIALIST.as_subagent(
        resolved_agent,
        name=name,
        description=description,
        options=options,
    )
