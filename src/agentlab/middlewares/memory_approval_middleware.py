"""Conditional approval for P5 memory writes: adding a fact is free, changing or removing one is not.

The decision is made in code from the tool call itself, never by the model: each
filesystem tool gets a ``when`` predicate that tells ``HumanInTheLoopMiddleware``
whether this particular call needs a human. Pass the result to
``create_deep_agent(interrupt_on=...)`` instead of adding a middleware yourself:
DeepAgents also applies ``interrupt_on`` to its general-purpose subagent, so a
write delegated through ``task`` can't skip the gate.
"""

from collections.abc import Callable
from typing import Any

from deepagents.backends import BackendProtocol
from deepagents.backends.utils import validate_path
from langchain.agents.middleware import InterruptOnConfig
from langchain.agents.middleware.human_in_the_loop import DecisionType
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolCall

from agentlab.configs.personal_assistant_config import MEMORIES_ROUTE_PREFIX

# The CLI approval loop offers approve or reject-with-reason; "edit" is in the backlog.
MEMORY_APPROVAL_DECISIONS: tuple[DecisionType, ...] = ("approve", "reject")


def _normalize(raw_path: Any) -> str | None:
    """Canonical form of a tool's path argument, so ``/memories/./x.md`` can't dodge a rule.

    ``None`` for a path the tool itself would reject before touching storage.
    """
    if not isinstance(raw_path, str):
        return None
    try:
        return validate_path(raw_path)
    except ValueError:
        return None


def _is_memory_file(path: str | None) -> bool:
    return path is not None and path.startswith(MEMORIES_ROUTE_PREFIX)


def _file_exists(backend: BackendProtocol, path: str) -> bool:
    """Whether ``path`` is already stored. A listing that fails counts as existing: fail closed."""
    listing = backend.ls(path.rsplit("/", 1)[0] + "/")
    if listing.error:
        return True
    return any(entry.get("path") == path for entry in listing.entries or [])


def _overwrites_stored_memory(backend: BackendProtocol) -> Callable[[ToolCallRequest], bool]:
    def when(request: ToolCallRequest) -> bool:
        path = _normalize(request.tool_call.get("args", {}).get("file_path"))
        return _is_memory_file(path) and _file_exists(backend, path)

    return when


def _keeps_every_line(old: str, new: str) -> bool:
    """Whether each line of ``old`` is still in ``new``, in the same order.

    New lines may be inserted anywhere in between. ``line in remaining`` advances the
    shared iterator past the match, so a later line can't match an earlier position.
    """
    remaining = iter(new.splitlines())
    return all(line in remaining for line in old.splitlines())


def _edit_removes_stored_text(request: ToolCallRequest) -> bool:
    """An edit is additive only when nothing it replaces is lost.

    That holds when the new text contains the old text whole (appending), or keeps
    every old line in order (inserting lines, e.g. a bullet in the middle of a section).
    """
    args = request.tool_call.get("args", {})
    if not _is_memory_file(_normalize(args.get("file_path"))):
        return False
    old, new = args.get("old_string"), args.get("new_string")
    if not (isinstance(old, str) and isinstance(new, str) and old):
        return True
    return not (old in new or _keeps_every_line(old, new))


def _deletes_memory(request: ToolCallRequest) -> bool:
    """Deleting anything under ``/memories/``, or a parent directory of it such as ``/``."""
    raw_path = request.tool_call.get("args", {}).get("file_path")
    if not isinstance(raw_path, str):
        return True
    path = _normalize(raw_path)
    if path is None:
        return False
    return path.startswith(MEMORIES_ROUTE_PREFIX) or MEMORIES_ROUTE_PREFIX.startswith(path.rstrip("/") + "/")


def _describe(reason: str) -> Callable[[ToolCall, Any, Any], str]:
    def description(tool_call: ToolCall, _state: Any, _runtime: Any) -> str:
        return f"{reason}\n\nTool: {tool_call['name']}\nArgs: {tool_call['args']}"

    return description


def make_memory_interrupt_on(backend: BackendProtocol) -> dict[str, InterruptOnConfig]:
    """Approval rules for the assistant's memory tools.

    Args:
        backend: The agent's own backend, used to check whether a write would
            replace a file that is already stored.
    """
    return {
        "write_file": InterruptOnConfig(
            allowed_decisions=list(MEMORY_APPROVAL_DECISIONS),
            when=_overwrites_stored_memory(backend),
            description=_describe("Overwrite a stored memory file (its current content is replaced)."),
        ),
        "edit_file": InterruptOnConfig(
            allowed_decisions=list(MEMORY_APPROVAL_DECISIONS),
            when=_edit_removes_stored_text,
            description=_describe("Change or remove text in stored memory."),
        ),
        "delete": InterruptOnConfig(
            allowed_decisions=list(MEMORY_APPROVAL_DECISIONS),
            when=_deletes_memory,
            description=_describe("Delete stored memory."),
        ),
    }
