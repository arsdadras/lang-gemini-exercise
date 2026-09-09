"""Universal session resolution & thread management utility for Agentic AI applications.

Supports 6 operational session modes:
1. 'default' (or empty/None): Uses the application's default thread ID.
2. 'new': Generates a unique, prefixed thread ID (e.g. `interpreter_a1b2c3`).
3. 'secret': Ephemeral in-memory execution bypassing persistence (`InMemorySaver`), leaving zero DB footprints.
4. 'resume': Automatically resumes the latest recorded checkpoint thread from storage.
5. 'step[N]': Resumes a recorded checkpoint thread by reverse-chronological 0-based index (`step[0]` = latest).
6. 'custom' (any other string): Directly adopts the user-provided thread ID name.
7. 'list' / 'history': Inspects and displays recent recorded sessions.
"""

from __future__ import annotations

import re
import sys
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver

from data.sqlite_db_data import get_recent_threads


@dataclass(frozen=True)
class ResolvedSession:
    """Encapsulates the resolved runtime session configuration."""

    agent: Any
    thread_id: str
    mode_name: str
    is_secret: bool

    @property
    def config(self) -> dict[str, Any]:
        """Convenience dictionary for LangGraph / DeepAgents invocation."""
        return {"configurable": {"thread_id": self.thread_id}}


def format_session_list(
    threads: list[str],
    *,
    cli_command_hint: str = "python app.py step[<index>]",
) -> str:
    """Format a list of recorded session thread IDs into a clean readable banner."""
    if not threads:
        return "No recorded sessions found in database."

    lines = [
        "=" * 60,
        "Recorded Sessions (0-indexed, most recent first):",
    ]
    for i, tid in enumerate(threads):
        tag = " (latest)" if i == 0 else ""
        lines.append(f"  step[{i}]: {tid}{tag}")
    lines.append("=" * 60)
    lines.append(f"To resume: {cli_command_hint}")
    return "\n".join(lines)


def resolve_session(
    raw_arg: str | None,
    *,
    default_thread_id: str,
    default_agent: Any | None = None,
    agent_factory: Callable[[Any], Any] | None = None,
    app_name: str = "agent",
    get_threads_fn: Callable[..., list[str]] = get_recent_threads,
    cli_command_hint: str | None = None,
    handle_cli_exit: bool = True,
) -> ResolvedSession:
    """Resolve an incoming CLI argument or mode string into a fully configured `ResolvedSession`.

    Args:
        raw_arg: The argument string passed by caller (e.g. sys.argv[1]), mode name, or None.
        default_thread_id: The fallback/default thread ID for standard session.
        default_agent: Pre-initialized default agent instance (using persistent checkpointer).
        agent_factory: Optional callable `factory(checkpointer) -> agent` used to construct
            agents on the fly, essential for ephemeral `secret` mode with `InMemorySaver()`.
            If omitted and `secret` mode is requested, `default_agent` is used.
        app_name: Prefix used when generating unique thread IDs in `new` mode.
        get_threads_fn: Callable returning recorded thread IDs ordered descending by latest activity.
        cli_command_hint: Hint displayed in `list` mode and error messages. Defaults to
            `python core/apps/{app_name}_app.py step[<index>]`.
        handle_cli_exit: If True, exits via `sys.exit(0)` on `list` or `sys.exit(1)` on invalid
            step index. If False, raises ValueError or returns special sessions.

    Returns:
        A `ResolvedSession` instance containing (agent, thread_id, mode_name, is_secret).
    """
    arg = (raw_arg or "").strip()
    hint = cli_command_hint or f"python core/apps/{app_name}_app.py step[<index>]"

    def _resolve_agent(checkpointer: Any | None) -> Any:
        if agent_factory is not None:
            return agent_factory(checkpointer)
        return default_agent

    # 1. Default Mode
    if not arg or arg.lower() == "default":
        return ResolvedSession(
            agent=_resolve_agent(None),
            thread_id=default_thread_id,
            mode_name="default",
            is_secret=False,
        )

    # 2. New Unique Mode
    if arg.lower() == "new":
        tid = f"{app_name}_{uuid.uuid4().hex[:6]}"
        return ResolvedSession(
            agent=_resolve_agent(None),
            thread_id=tid,
            mode_name="new",
            is_secret=False,
        )

    # 3. Secret (Ephemeral In-Memory) Mode
    if arg.lower() == "secret":
        tid = f"secret_{uuid.uuid4().hex[:6]}"
        mem_saver = InMemorySaver()
        secret_agent = _resolve_agent(mem_saver)
        return ResolvedSession(
            agent=secret_agent,
            thread_id=tid,
            mode_name="secret (in-memory)",
            is_secret=True,
        )

    # 4. List / History Mode
    if arg.lower() in {"list", "history"}:
        threads = get_threads_fn(limit=15)
        output = format_session_list(threads, cli_command_hint=hint)
        print(output)
        if handle_cli_exit:
            sys.exit(0)
        return ResolvedSession(
            agent=_resolve_agent(None),
            thread_id=default_thread_id,
            mode_name="list",
            is_secret=False,
        )

    # 5. Resume (Latest Recorded Thread) Mode
    if arg.lower() == "resume":
        threads = get_threads_fn()
        if threads:
            return ResolvedSession(
                agent=_resolve_agent(None),
                thread_id=threads[0],
                mode_name=f"resume ({threads[0]})",
                is_secret=False,
            )
        print("[Notice] No previous sessions found in database. Using default.")
        return ResolvedSession(
            agent=_resolve_agent(None),
            thread_id=default_thread_id,
            mode_name="default (no prior sessions)",
            is_secret=False,
        )

    # 6. Step[Index] Mode (Reverse-chronological 0-based index)
    step_match = re.match(r"^step\[?(\d+)\]?$", arg, re.IGNORECASE)
    if step_match:
        idx = int(step_match.group(1))
        threads = get_threads_fn()
        if not threads:
            msg = "[Error] No recorded sessions found in database."
            print(msg)
            if handle_cli_exit:
                sys.exit(1)
            raise ValueError(msg)

        if 0 <= idx < len(threads):
            selected = threads[idx]
            return ResolvedSession(
                agent=_resolve_agent(None),
                thread_id=selected,
                mode_name=f"step[{idx}] ({selected})",
                is_secret=False,
            )

        err_msg = (
            f"[Error] Index {idx} out of range. Available: step[0] to step[{len(threads) - 1}].\n"
            "Recent sessions:\n"
            + "\n".join(f"  step[{i}]: {t}" for i, t in enumerate(threads[:5]))
        )
        print(err_msg)
        if handle_cli_exit:
            sys.exit(1)
        raise IndexError(err_msg)

    # 7. Custom Named Session
    return ResolvedSession(
        agent=_resolve_agent(None),
        thread_id=arg,
        mode_name=f"custom ({arg})",
        is_secret=False,
    )
