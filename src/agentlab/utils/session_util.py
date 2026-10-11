"""CLI session resolution: map an app's mode argument to an agent and a thread id.

Modes:
- ``default`` (or no argument): the app's default thread id.
- ``new``: a fresh unique thread id.
- ``secret``: a fresh thread on an in-memory checkpointer (nothing written to disk).
- ``resume``: the most recently checkpointed thread.
- ``step[N]``: the N-th most recent thread (``step[0]`` is the latest).
- ``list`` / ``history``: print recent threads.
- anything else: used verbatim as the thread id.
"""

import functools
import re
import sys
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from agentlab.configs.paths_config import checkpoint_db_path
from agentlab.data.sqlite_db_data import get_recent_threads

AgentFactory = Callable[[BaseCheckpointSaver | None], Any]
"""Builds an app's agent. Gets ``None`` in persistent modes (the factory uses its
durable default) and an ``InMemorySaver`` in secret mode."""

_STEP_RE = re.compile(r"^step\[?(\d+)\]?$", re.IGNORECASE)


@dataclass(frozen=True)
class ResolvedSession:
    """The agent and thread an app should run."""

    agent: Any
    thread_id: str
    mode_name: str
    is_secret: bool = False

    @property
    def config(self) -> RunnableConfig:
        """LangGraph invocation config for this session's thread."""
        return {"configurable": {"thread_id": self.thread_id}}


def format_session_list(
    threads: list[str],
    *,
    cli_command_hint: str = "step[<index>]",
) -> str:
    """Render recorded thread ids, most recent first."""
    if not threads:
        return "No recorded sessions found in database."
    lines = ["=" * 60, "Recorded Sessions (0-indexed, most recent first):"]
    lines.extend(
        f"  step[{i}]: {thread_id}{' (latest)' if i == 0 else ''}"
        for i, thread_id in enumerate(threads)
    )
    lines.extend(["=" * 60, f"To resume: {cli_command_hint}"])
    return "\n".join(lines)


def _fail(message: str, error: type[Exception], handle_cli_exit: bool) -> None:
    print(message)
    if handle_cli_exit:
        sys.exit(1)
    raise error(message)


def _resolve_thread(
    arg: str,
    *,
    default_thread_id: str,
    app_name: str,
    get_threads_fn: Callable[..., list[str]],
    handle_cli_exit: bool,
) -> tuple[str, str]:
    """Return ``(thread_id, mode_name)`` for every persistent mode."""
    mode = arg.lower()
    if not arg or mode == "default":
        return default_thread_id, "default"
    if mode == "new":
        return f"{app_name}_{uuid.uuid4().hex[:6]}", "new"
    if mode == "resume":
        threads = get_threads_fn()
        if threads:
            return threads[0], f"resume ({threads[0]})"
        print("[Notice] No previous sessions found in database. Using default.")
        return default_thread_id, "default (no prior sessions)"
    if step := _STEP_RE.match(arg):
        index = int(step.group(1))
        threads = get_threads_fn()
        if not threads:
            _fail(
                "[Error] No recorded sessions found in database.",
                ValueError,
                handle_cli_exit,
            )
        if not 0 <= index < len(threads):
            recent = "\n".join(f"  step[{i}]: {t}" for i, t in enumerate(threads[:5]))
            _fail(
                f"[Error] Index {index} out of range. Available: step[0] to "
                f"step[{len(threads) - 1}].\nRecent sessions:\n{recent}",
                IndexError,
                handle_cli_exit,
            )
        return threads[index], f"step[{index}] ({threads[index]})"
    return arg, f"custom ({arg})"


def resolve_session(
    raw_arg: str | None,
    *,
    default_thread_id: str,
    agent_factory: AgentFactory,
    app_name: str,
    get_threads_fn: Callable[..., list[str]] | None = None,
    cli_command_hint: str | None = None,
    handle_cli_exit: bool = True,
) -> ResolvedSession:
    """Resolve a CLI mode argument into a ``ResolvedSession``.

    The agent is built only after the mode is known to be valid, and not at all
    for ``list``. With ``handle_cli_exit=False`` errors raise instead of exiting.
    """
    if get_threads_fn is None:
        # The app's own database: `list`, `resume`, and `step[N]` never see another app's threads.
        db_path = checkpoint_db_path(app_name)
        get_threads_fn = functools.partial(get_recent_threads, db_path)
    arg = (raw_arg or "").strip()
    mode = arg.lower()
    hint = (
        cli_command_hint
        or f"uv run python -m agentlab.apps.{app_name}_app step[<index>]"
    )

    if mode in {"list", "history"}:
        print(format_session_list(get_threads_fn(limit=15), cli_command_hint=hint))
        if handle_cli_exit:
            sys.exit(0)
        return ResolvedSession(
            agent=None,
            thread_id=default_thread_id,
            mode_name="list",
        )

    if mode == "secret":
        return ResolvedSession(
            agent=agent_factory(InMemorySaver()),
            thread_id=f"secret_{uuid.uuid4().hex[:6]}",
            mode_name="secret (in-memory)",
            is_secret=True,
        )

    thread_id, mode_name = _resolve_thread(
        arg,
        default_thread_id=default_thread_id,
        app_name=app_name,
        get_threads_fn=get_threads_fn,
        handle_cli_exit=handle_cli_exit,
    )
    return ResolvedSession(
        agent=agent_factory(None),
        thread_id=thread_id,
        mode_name=mode_name,
    )
