"""End a role session: commit this worktree's changes, push the role branch, print three lines.

    python scripts/handoff.py -m "docs(lead): record ..." [--wip] [--pr]
                              [--trailer "Co-Authored-By: ..."] [--dry-run]

Run by the `/handoff` skill after the role's STATE.md is up to date. It refuses to run outside a
role worktree or on `main`. A role worktree holds only its role's work, so every change is
committed (library/engineering/git-policy.md). `--wip` marks unfinished work as
`wip(<role>): ...`; `--pr` opens a pull request to `main` when none is open. Standard library
only, plus the `gh` CLI for `--pr`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from workspace import (
    MAIN_BRANCH,
    REMOTE,
    ROOT,
    ahead_behind,
    current_branch,
    detect_role,
    git,
    status_lines,
)


class HandoffError(RuntimeError):
    """The handoff can't run here."""


def commit_message(role: str, subject: str, wip: bool) -> str:
    if wip and not subject.startswith("wip"):
        return f"wip({role}): {subject}"
    return subject


def push(root: Path, branch: str) -> str:
    result = subprocess.run(
        ["git", "push", "--quiet", "-u", REMOTE, branch],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        return f"pushed to {REMOTE}/{branch}"
    reason = (result.stderr.strip().splitlines() or ["unknown error"])[-1]
    return f"push FAILED ({reason})"


def pull_request(root: Path, branch: str, create: bool) -> str:
    """The open pull request from `branch` to main, opened first when `create` is set."""
    try:
        found = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--head",
                branch,
                "--base",
                MAIN_BRANCH,
                "--json",
                "url",
            ],
            cwd=root,
            capture_output=True,
            check=False,
            text=True,
        )
        urls = [pr["url"] for pr in json.loads(found.stdout or "[]")]
        if urls:
            return urls[0]
        if not create:
            return "none (use --pr when the work is ready for main)"
        made = subprocess.run(
            ["gh", "pr", "create", "--base", MAIN_BRANCH, "--head", branch, "--fill"],
            cwd=root,
            capture_output=True,
            check=False,
            text=True,
        )
        return made.stdout.strip() or f"not opened ({made.stderr.strip()})"
    except (OSError, json.JSONDecodeError) as exc:
        return f"unavailable ({type(exc).__name__})"


def handoff(
    root: Path,
    subject: str | None,
    wip: bool = False,
    open_pr: bool = False,
    trailers: tuple[str, ...] = (),
    dry_run: bool = False,
) -> list[str]:
    role = detect_role(root)
    branch = current_branch(root)
    if role is None:
        raise HandoffError(
            "this checkout plays no role; run /handoff in a role worktree"
        )
    if branch in ("", MAIN_BRANCH):
        raise HandoffError("refusing to commit on main or a detached HEAD")

    changes = status_lines(root)
    if not changes:
        committed = "nothing to commit"
    elif not subject:
        raise HandoffError(f"{len(changes)} uncommitted path(s): pass -m <message>")
    else:
        message = commit_message(role, subject, wip)
        if dry_run:
            committed = f"would commit {len(changes)} path(s) as '{message}'"
        else:
            git("add", "-A", cwd=root)
            extra = [arg for trailer in trailers for arg in ("--trailer", trailer)]
            git("commit", "--quiet", "-m", message, *extra, cwd=root)
            committed = (
                f"committed {git('rev-parse', '--short', 'HEAD', cwd=root)} '{message}'"
            )

    pushed = f"would push to {REMOTE}/{branch}" if dry_run else push(root, branch)
    sync = ahead_behind(branch, f"{REMOTE}/{MAIN_BRANCH}", root)
    if sync is None:
        against_main = f"{REMOTE}/{MAIN_BRANCH} not found"
    else:
        against_main = f"{sync[0]} ahead of main, {sync[1]} behind"
        if sync[1]:
            against_main += f" (merge {REMOTE}/{MAIN_BRANCH} next session)"
    pr = "not checked (dry run)" if dry_run else pull_request(root, branch, open_pr)
    return [
        f"{role} @ {branch}: {committed}; {pushed}",
        f"Branch vs main: {against_main}",
        f"Pull request: {pr}",
    ]


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-m", "--message", help="commit subject (conventional commit)")
    parser.add_argument(
        "--wip", action="store_true", help="mark the commit as unfinished work"
    )
    parser.add_argument("--pr", action="store_true", help="open a pull request to main")
    parser.add_argument("--trailer", action="append", default=[], help="commit trailer")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        lines = handoff(
            ROOT, args.message, args.wip, args.pr, tuple(args.trailer), args.dry_run
        )
    except HandoffError as exc:
        print(f"handoff: {exc}")
        return 1
    print("\n".join(lines))
    return 0 if "FAILED" not in lines[0] else 1


if __name__ == "__main__":
    sys.exit(main())
