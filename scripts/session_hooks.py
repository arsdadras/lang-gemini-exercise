"""Claude Code session hooks for the role worktrees, wired in `.claude/settings.json`.

    python scripts/session_hooks.py start   # SessionStart: role, sync, status, STATE head, inbox
    python scripts/session_hooks.py prompt  # UserPromptSubmit: messages that arrived since
    python scripts/session_hooks.py guard   # PreToolUse on edits: the ownership guard
    python scripts/session_hooks.py stop    # Stop: one non-blocking warning about unsaved work

`start` and `prompt` print plain text, which Claude Code adds to the session's context; `guard`
prints a JSON denial when an edit is out of bounds; `stop` prints a JSON `systemMessage`, which
the user sees without the session being blocked. Every hook exits 0, and a failing hook lets the
session carry on (ADR-0019, ADR-0020). Standard library only.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import inbox
from workspace import (
    MAIN_BRANCH,
    REMOTE,
    ROLES,
    ROOT,
    ahead_behind,
    checkouts,
    current_branch,
    detect_role,
    fetch,
    git_dir,
    may_write,
    owners,
    ownership_rules,
    status_lines,
    worktree_path,
)

STATE_HEAD_LINES = 12
STATUS_LINES = 10
FETCH_EVERY_SECONDS = 300
SESSION_FILES_KEPT_DAYS = 7
EDIT_TOOLS = frozenset({"Edit", "Write", "MultiEdit", "NotebookEdit"})
GUARD_OFF_ENV = "AGENTLAB_GUARD"


# ---------------------------------------------------------------- session memory of the hooks


def session_file(root: Path, session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id or "unknown")
    return git_dir(root) / "agentlab" / f"session-{safe}.json"


def load_session(root: Path, session_id: str) -> dict:
    path = session_file(root, session_id)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"announced": [], "fetched_at": 0.0}


def save_session(root: Path, session_id: str, data: dict) -> None:
    path = session_file(root, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    cutoff = time.time() - SESSION_FILES_KEPT_DAYS * 86400
    for old in path.parent.glob("session-*.json"):
        if old.stat().st_mtime < cutoff:
            old.unlink(missing_ok=True)


def message_lines(role: str, root: Path) -> tuple[list[str], list[str]]:
    """(the role's inbox as display lines, the IDs they show)."""
    incoming, replies = inbox.inbox(inbox.load(root), role)
    lines = [f"  {m.id} from {m.sender} | {m.kind} | {m.first_line}" for m in incoming]
    lines += [f"  {m.id} from {m.sender} | {m.kind} | {m.status}" for m in replies]
    return lines, [m.id for m in incoming + replies]


# ---------------------------------------------------------------- SessionStart


def state_head(root: Path, role: str) -> list[str]:
    """The first non-empty lines of the role's STATE.md."""
    path = root / "offices" / role / "STATE.md"
    if not path.is_file():
        return [f"(offices/{role}/STATE.md not found)"]
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    return lines[:STATE_HEAD_LINES]


def sync_lines(root: Path, branch: str, role: str | None) -> list[str]:
    """What this branch lacks from main, and what isn't pushed or pulled yet."""
    if not branch:
        return ["HEAD is detached."]
    lines: list[str] = []
    upstream = f"{REMOTE}/{MAIN_BRANCH}"
    behind_main = ahead_behind(branch, upstream, root)
    if branch != MAIN_BRANCH and behind_main and behind_main[1]:
        lines.append(
            f"{upstream} has {behind_main[1]} commit(s) this branch lacks: "
            f"run `git merge {upstream}` before working."
        )
    remote = ahead_behind(branch, f"{REMOTE}/{branch}", root)
    if remote is None:
        if role:
            lines.append(
                f"Branch {branch} has no copy on {REMOTE} yet: /handoff pushes it."
            )
    else:
        if remote[0]:
            lines.append(f"{remote[0]} commit(s) not pushed yet.")
        if remote[1]:
            lines.append(
                f"{REMOTE}/{branch} has {remote[1]} commit(s) this checkout lacks: pull first."
            )
    return lines


def routing_lines(root: Path) -> list[str]:
    """What a session outside the role worktrees must do before any change."""
    homes = ", ".join(f"{r}: {worktree_path(r, root)}" for r in ROLES)
    return [
        (
            f"Role work runs only in the role worktrees ({homes}); the ownership guard "
            "refuses edits here."
        ),
        (
            "Before any change, take the session to the worktree of the role the request "
            "needs (lead for decisions, plans, reviews, and git; engineer for code, tests, and "
            "repo tooling; mentor for lessons; research for investigation): in the desktop "
            "app call the change_directory tool with that path (continue with absolute paths "
            "until it takes effect); in a terminal, ask the user to start claude in that "
            "folder. Say which role and why in one line."
        ),
    ]


def start_report(root: Path, online: bool = True, session_id: str | None = None) -> str:
    role = detect_role(root)
    branch = current_branch(root)
    out: list[str] = []
    if role is None:
        out.append(
            f"agentlab: this checkout (branch {branch or 'detached'}) plays no role."
        )
        out += routing_lines(root)
    else:
        out.append(f"agentlab: role {role}, branch {branch}, worktree {root}.")
        out.append(f"Charter: offices/{role}/README.md. End the session with /handoff.")
        if not (root / "CLAUDE.local.md").is_file():
            out.append(
                f"No CLAUDE.local.md here: read offices/{role}/README.md before anything else."
            )
    if not online:
        out.append(f"(git fetch failed: {REMOTE} refs may be stale)")
    out += sync_lines(root, branch, role)
    changes = status_lines(root)
    out.append(f"Uncommitted: {len(changes)} path(s)" + ("" if changes else ", clean"))
    out += [f"  {line}" for line in changes[:STATUS_LINES]]
    if len(changes) > STATUS_LINES:
        out.append(f"  ... and {len(changes) - STATUS_LINES} more")
    if role:
        out.append(f"--- offices/{role}/STATE.md (head) ---")
        out += state_head(root, role)
        lines, ids = message_lines(role, root)
        out.append(f"--- inbox: {len(lines)} message(s) for {role} ---")
        out += lines
        if session_id is not None:
            save_session(
                root, session_id, {"announced": ids, "fetched_at": time.time()}
            )
    return "\n".join(out)


# ---------------------------------------------------------------- UserPromptSubmit


def prompt_report(root: Path, session_id: str, online_check: bool = True) -> str | None:
    """New inbox messages since this session last heard, fetching at most every 5 minutes."""
    role = detect_role(root)
    if role is None:
        return None
    state = load_session(root, session_id)
    if (
        online_check
        and time.time() - state.get("fetched_at", 0.0) > FETCH_EVERY_SECONDS
    ):
        fetch(root, timeout=10)
        state["fetched_at"] = time.time()
    lines, ids = message_lines(role, root)
    announced = set(state.get("announced", []))
    fresh = [line for line, mid in zip(lines, ids, strict=True) if mid not in announced]
    state["announced"] = sorted(announced | set(ids))
    save_session(root, session_id, state)
    if not fresh:
        return None
    return "\n".join(
        [f"agentlab: new message(s) for {role} since this session heard:", *fresh]
    )


# ---------------------------------------------------------------- PreToolUse guard


def guard_reason(root: Path, payload: dict) -> str | None:
    """Why an edit must not happen, or None to let it through (ADR-0020)."""
    if os.environ.get(GUARD_OFF_ENV, "").lower() == "off":
        return None
    if payload.get("tool_name") not in EDIT_TOOLS:
        return None
    tool_input = payload.get("tool_input") or {}
    raw = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not raw:
        return None
    target = Path(raw)
    if not target.is_absolute():
        target = Path(payload.get("cwd") or root) / target
    target = target.resolve()
    homes = sorted(checkouts(root), key=lambda p: len(str(p)), reverse=True)
    home = next((h for h in homes if target == h or h in target.parents), None)
    if home is None:
        return None  # outside this repository: not the guard's business
    role = detect_role(root)
    here = root.resolve()
    if role is None:
        return " ".join(
            [
                f"This checkout ({here}) plays no role, so it takes no edits.",
                *routing_lines(root),
            ]
        )
    if home != here:
        return (
            f"{target} is in another checkout ({home}); a {role} session edits only its own "
            f"worktree ({here}). Send that role a message instead "
            "(library/governance/protocol.md)."
        )
    rel = target.relative_to(home).as_posix()
    rules = ownership_rules(root)
    if may_write(role, rel, rules):
        return None
    allowed = ", ".join(sorted(owners(rel, rules)))
    return (
        f"{rel} belongs to {allowed} (library/governance/ownership.md), so a {role} session "
        "can't edit it. Send the owner a message; if the user wants that role's work done, "
        "move the session to that role's worktree."
    )


# ---------------------------------------------------------------- Stop


def stop_message(root: Path) -> str | None:
    """A one-line warning when a role worktree holds uncommitted or unpushed work."""
    role = detect_role(root)
    branch = current_branch(root)
    if role is None or not branch:
        return None
    parts: list[str] = []
    changes = status_lines(root)
    if changes:
        parts.append(f"{len(changes)} uncommitted path(s)")
    remote = ahead_behind(branch, f"{REMOTE}/{branch}", root)
    if remote is None:
        parts.append(f"branch {branch} not on {REMOTE}")
    elif remote[0]:
        parts.append(f"{remote[0]} unpushed commit(s)")
    if not parts:
        return None
    return f"agentlab ({role}): {', '.join(parts)}. Run /handoff before ending the session."


# ---------------------------------------------------------------- entry point


def read_payload() -> dict:
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        return json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else ""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        payload = read_payload()
        session_id = payload.get("session_id") or "unknown"
        if command == "start":
            print(start_report(ROOT, online=fetch(ROOT), session_id=session_id))
        elif command == "prompt":
            report = prompt_report(ROOT, session_id)
            if report:
                print(report)
        elif command == "guard":
            reason = guard_reason(ROOT, payload)
            if reason:
                decision = {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
                print(json.dumps({"hookSpecificOutput": decision}))
        elif command == "stop":
            message = stop_message(ROOT)
            if message:
                print(json.dumps({"systemMessage": message}))
        else:
            print("usage: session_hooks.py start|prompt|guard|stop")
    except Exception as exc:  # noqa: BLE001 - a hook must never break the session
        failure = f"agentlab {command} hook failed: {type(exc).__name__}: {exc}"
        if command in ("guard", "stop"):
            print(json.dumps({"systemMessage": failure}))
        else:
            print(failure)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
