"""P5 subagent adapter over ``workflows/personal_context_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.store.base import BaseStore

from agentlab.tools.user_context_tool import (
    PERSONAL_CONTEXT_SPECIALIST,
    render_personal_context,
)
from agentlab.utils.subagent_util import specialist_subagent
from agentlab.workflows.personal_context_workflow import (
    DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
    PERSONAL_CONTEXT_SPECIALIST_SPEC,
    run_personal_context,
)

DEFAULT_PERSONAL_CONTEXT_SUBAGENT_NAME = "personal_context_subagent"


def make_personal_context_subagent(
    store: BaseStore | None = None,
    *,
    name: str = DEFAULT_PERSONAL_CONTEXT_SUBAGENT_NAME,
    description: str = DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap P5's ``run_personal_context`` workflow as a ``CompiledSubAgent``."""
    return specialist_subagent(
        name,
        description,
        lambda user_id: run_personal_context(user_id.strip(), store=store),
        render=render_personal_context,
    )


__all__ = [
    "DEFAULT_PERSONAL_CONTEXT_DESCRIPTION",
    "DEFAULT_PERSONAL_CONTEXT_SUBAGENT_NAME",
    "PERSONAL_CONTEXT_SPECIALIST",
    "PERSONAL_CONTEXT_SPECIALIST_SPEC",
    "make_personal_context_subagent",
    "render_personal_context",
    "run_personal_context",
]
