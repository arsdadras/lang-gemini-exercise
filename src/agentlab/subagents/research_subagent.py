"""P1 subagent adapter over ``workflows/research_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.workflows.research_workflow import (
    DEFAULT_RESEARCH_DESCRIPTION,
    RESEARCH_SPECIALIST,
    make_research_graph,
)

RESEARCHER_SUBAGENT_NAME = "researcher"


def make_researcher_subagent(
    graph: CompiledStateGraph | None = None,
    *,
    agent: CompiledStateGraph | None = None,
    options: ResearchOptions | None = None,
    name: str = RESEARCHER_SUBAGENT_NAME,
    description: str = DEFAULT_RESEARCH_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap P1's ``run_research`` workflow as a ``CompiledSubAgent`` for coordinators.

    Delegated research runs execute the full R1 plan -> route -> research -> claim-check
    workflow and return the verified ``ResearchReport`` envelope as text.
    """
    target_engine = graph if graph is not None else agent
    resolved_engine = (
        target_engine
        if target_engine is not None
        else (make_research_graph(options=options) if options is not None else None)
    )
    return RESEARCH_SPECIALIST.as_subagent(
        resolved_engine,
        name=name,
        description=description,
        options=options,
    )
