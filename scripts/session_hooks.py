"""Claude Code session hooks for the role worktrees, wired in `.claude/settings.json`.

    python scripts/session_hooks.py start   # SessionStart: role, sync, status, STATE head, inbox
    python scripts/session_hooks.py stop    # Stop: one non-blocking warning about unsaved work

`start` prints plain text, which Claude Code adds to the session's context; `stop` prints a JSON
`systemMessage`, which the user sees without the session being blocked. Both always exit 0, so a
hook can never break a session. Standard library only (ADR-0019).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import inbox
from workspace import (
    MAIN_BRANCH,
    REMOTE,
    ROLES,
    ROOT,
    ahead_behind,
    current_branch,
    detect_role,
    fetch,
    status_lines,
    worktree_path,
)

STATE_HEAD_LINES = 12
STATUS_LINES = 10


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


def start_report(root: Path, online: bool = True) -> str:
    role = detect_role(root)
    branch = current_branch(root)
    out: list[str] = []
    if role is None:
        out.append(
            f"agentlab: this checkout (branch {branch or 'detached'}) plays no role."
        )
        homes = ", ".join(f"{r}: {worktree_path(r, root)}" for r in ROLES)
        out.append(f"Role sessions run in their own worktrees ({homes}).")
        out.append(
            "Here, do only what the user asks; /lead or /research sets a role explicitly."
        )
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
        incoming, replies = inbox.inbox(inbox.load(root), role)
        out.append(
            f"--- inbox: {len(incoming)} open, {len(replies)} repl(ies) to verify ---"
        )
        out += [
            f"  {m.id} from {m.sender} | {m.kind} | {m.first_line}" for m in incoming
        ]
        out += [f"  {m.id} from {m.sender} | {m.kind} | {m.status}" for m in replies]
    return "\n".join(out)


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


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        command = argv[1] if len(argv) > 1 else ""
        if command == "start":
            print(start_report(ROOT, online=fetch(ROOT)))
        elif command == "stop":
            if not sys.stdin.isatty():
                sys.stdin.read()
            message = stop_message(ROOT)
            if message:
                print(json.dumps({"systemMessage": message}))
        else:
            print("usage: session_hooks.py start|stop")
    except Exception as exc:  # noqa: BLE001 - a hook must never break the session
        print(f"agentlab session hook failed: {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
