"""P3 subagent adapter over ``workflows/code_review_workflow.py`` (ADR-0033)."""

from typing import Any

from deepagents import CompiledSubAgent

from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.graphs.code_review_parentgraph import build_code_review_graph
from agentlab.utils.subagent_util import specialist_subagent
from agentlab.workflows.code_review_workflow import (
    CODE_REVIEW_SPECIALIST,
    CODE_REVIEW_SPECIALIST_SPEC,
    DEFAULT_CODE_REVIEW_DESCRIPTION,
    render_outcome,
    run_code_review,
)

DEFAULT_CODE_REVIEW_NAME = "code_review_subagent"


def make_code_review_subagent(
    graph: Any = None,
    *,
    name: str = DEFAULT_CODE_REVIEW_NAME,
    description: str = DEFAULT_CODE_REVIEW_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap the compiled review pipeline as a ``CompiledSubAgent``."""
    review_graph = (
        graph
        if graph is not None
        else build_code_review_graph(
            checkpointer=get_sqlite_checkpointer(checkpoint_db_path(DELEGATIONS_APP))
        )
    )

    return specialist_subagent(
        name,
        description,
        lambda task: run_code_review(review_graph, task),
        render=render_outcome,
    )


__all__ = [
    "CODE_REVIEW_SPECIALIST",
    "CODE_REVIEW_SPECIALIST_SPEC",
    "DEFAULT_CODE_REVIEW_DESCRIPTION",
    "DEFAULT_CODE_REVIEW_NAME",
    "make_code_review_subagent",
    "render_outcome",
    "run_code_review",
]
