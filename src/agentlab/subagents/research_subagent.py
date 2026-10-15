"""P1 subagent adapter over ``workflows/research_workflow.py`` (ADR-0033)."""

from typing import Any

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.workflows.research_workflow import (
    DEFAULT_RESEARCH_DESCRIPTION,
    ResearchWorkflow,
)

RESEARCHER_SUBAGENT_NAME = "researcher"


def make_researcher_subagent(
    agent: Any = None,
    *,
    graph: CompiledStateGraph | None = None,
    options: ResearchOptions | None = None,
    name: str = RESEARCHER_SUBAGENT_NAME,
    description: str = DEFAULT_RESEARCH_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap P1's ``run_research`` workflow as a ``CompiledSubAgent`` for coordinators.

    Delegated research runs execute the full R1 plan -> route -> research -> claim-check
    workflow and return the verified ``ResearchReport`` envelope as text.
    """
    if graph is not None:
        workflow = ResearchWorkflow.from_graph(graph, options=options)
    elif agent is not None:
        workflow = ResearchWorkflow.from_agent(agent=agent, options=options)
    else:
        workflow = ResearchWorkflow(options=options)
    return workflow.as_subagent(name=name, description=description)
