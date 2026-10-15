"""Shared plumbing every subagent adapter needs: read the coordinator's delegated task,
run it on its own isolated thread, and hand back a single final-answer ``AIMessage``.

What varies per subagent — how the task text maps to the underlying graph or agent's
own input shape, and how its result becomes the final answer text — is the actual
translation contract a subagent adapter exists to own, and stays in ``subagents/*.py``.
"""

import uuid
from collections.abc import Callable, Mapping
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda

from agentlab.schemas.output.specialist_output_schema import SpecialistResult
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


def pending_approvals(state: Mapping[str, Any]) -> str:
    """Name the actions a finished ``invoke`` left waiting for approval, or ``""``.

    A graph that pauses returns normally with an ``__interrupt__`` entry. A boundary that
    ignores it silently drops the pending work, so every specialist boundary checks here.
    """
    names: list[str] = []
    for pending in state.get("__interrupt__", []):
        value = pending.value if isinstance(pending.value, dict) else {}
        requests = value.get("action_requests") or [
            {"name": value.get("action_required", "an action")},
        ]
        names.extend(str(request.get("name", "an action")) for request in requests)
    return ", ".join(names)


def specialist_subagent(
    name: str,
    description: str,
    run: Callable[[str], SpecialistResult[Any]],
    *,
    render: Callable[[Any], str] | None = None,
) -> CompiledSubAgent:
    """A specialist's ``run_*`` boundary as a ``CompiledSubAgent`` a coordinator delegates to.

    The coordinator's task text goes to ``run``; its envelope comes back as one final-answer
    message (``SpecialistResult.to_text``, with ``render`` for the output), so the coordinator
    sees the status, the reason, and the sources too. What differs per specialist (which graph
    or agent ``run`` closes over, and how its output reads) stays in ``subagents/``.
    """

    def delegate(state: dict[str, Any]) -> dict[str, Any]:
        return to_subagent_reply(
            run(task_text_from_state(state)).to_text(render=render)
        )

    return {
        "name": name,
        "description": description,
        "runnable": RunnableLambda(delegate),
    }
