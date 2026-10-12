"""P3 subagent adapter over ``workflows/code_review_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.workflows.code_review_workflow import (
    CODE_REVIEW_SPECIALIST,
    DEFAULT_CODE_REVIEW_DESCRIPTION,
)

DEFAULT_CODE_REVIEW_NAME = "code_review_subagent"


def make_code_review_subagent(
    graph: CompiledStateGraph | None = None,
    *,
    name: str = DEFAULT_CODE_REVIEW_NAME,
    description: str = DEFAULT_CODE_REVIEW_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap the compiled review pipeline as a ``CompiledSubAgent``."""
    return CODE_REVIEW_SPECIALIST.as_subagent(
        graph,
        name=name,
        description=description,
    )
