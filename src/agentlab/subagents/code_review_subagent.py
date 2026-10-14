"""P3 subagent adapter over ``workflows/code_review_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.workflows.code_review_workflow import (
    DEFAULT_CODE_REVIEW_DESCRIPTION,
    make_code_review_specialist,
)

DEFAULT_CODE_REVIEW_NAME = "code_review_subagent"


def make_code_review_subagent(
    graph: CompiledStateGraph | None = None,
    *,
    name: str = DEFAULT_CODE_REVIEW_NAME,
    description: str = DEFAULT_CODE_REVIEW_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap the compiled review pipeline as a ``CompiledSubAgent``."""
    specialist = make_code_review_specialist(graph)
    return specialist.as_subagent(
        name=name,
        description=description,
    )
