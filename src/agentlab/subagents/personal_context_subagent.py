"""P5 subagent adapter over ``workflows/personal_context_workflow.py`` (ADR-0033)."""

from deepagents import CompiledSubAgent
from langgraph.store.base import BaseStore

from agentlab.workflows.personal_context_workflow import (
    DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
    PersonalContextWorkflow,
)

DEFAULT_PERSONAL_CONTEXT_SUBAGENT_NAME = "personal_context_subagent"


def make_personal_context_subagent(
    store: BaseStore | None = None,
    *,
    name: str = DEFAULT_PERSONAL_CONTEXT_SUBAGENT_NAME,
    description: str = DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap P5's ``run_personal_context`` workflow as a ``CompiledSubAgent``."""
    return PersonalContextWorkflow(store).as_subagent(
        name=name,
        description=description,
    )
