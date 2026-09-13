"""Shared plumbing every subagent adapter needs: read the coordinator's delegated task,
run it on its own isolated thread, and hand back a single final-answer ``AIMessage``.

What varies per subagent — how the task text maps to the underlying graph or agent's
own input shape, and how its result becomes the final answer text — is the actual
translation contract a subagent adapter exists to own, and stays in ``subagents/*.py``.
"""

import uuid
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from agentlab.utils.get_text_util import get_text


def task_text_from_state(state: dict[str, Any]) -> str:
    """Read the coordinator's delegated task as plain text."""
    return get_text(state["messages"][-1])


def new_delegation_config() -> RunnableConfig:
    """A fresh, isolated thread id: each delegation is a one-shot call, never resumed."""
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


def to_subagent_reply(content: str) -> dict[str, Any]:
    """Wrap a final answer as the single ``AIMessage`` a ``CompiledSubAgent`` must return."""
    return {"messages": [AIMessage(content=content)]}
