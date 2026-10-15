"""P1 subagent adapter over ``workflows/research_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.workflows.research_workflow import (
    DEFAULT_RESEARCH_DESCRIPTION,
    ResearchWorkflow,
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
    is_graph = bool(
        target_engine is not None
        and (
            getattr(target_engine, "_is_research_graph", False)
            or (
                hasattr(target_engine, "nodes")
                and isinstance(getattr(target_engine, "nodes", None), dict)
                and "plan" in getattr(target_engine, "nodes", {})
                and "check" in getattr(target_engine, "nodes", {})
            )
        )
    )
    workflow = ResearchWorkflow(
        graph=target_engine if is_graph else None,
        agent=target_engine if not is_graph and target_engine is not None else None,
        options=options,
    )
    return workflow.as_subagent(name=name, description=description)
