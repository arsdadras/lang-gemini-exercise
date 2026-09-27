"""Role workspaces: which role a checkout plays, and the git helpers the session scripts share.

Each role works in its own git worktree and branch (ADR-0019): `../lce-lead` on `lead`,
`../lce-mentor` on `mentor`, `../lce-research` on `research`. A worktree's role comes from its
own git config (`agentlab.role`, written by `setup_worktrees.py`); where that is missing, as in
a cloud session, from the branch name (`mentor` or `mentor/<topic>`). The main checkout stays on
`main` and plays no role.

Standard library only, so hooks can run it before any virtual environment exists.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = ("lead", "mentor", "research")
ROLE_CONFIG_KEY = "agentlab.role"
MAIN_BRANCH = "main"
REMOTE = "origin"


class GitError(RuntimeError):
    """A git command failed."""


def git(*args: str, cwd: Path = ROOT, check: bool = True, timeout: float = 60) -> str:
    """Run git in `cwd` and return stdout without its trailing newline."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if check and result.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.rstrip("\n")


def current_branch(cwd: Path = ROOT) -> str:
    """The checked-out branch, or '' when HEAD is detached."""
    return git("branch", "--show-current", cwd=cwd, check=False)


def detect_role(cwd: Path = ROOT) -> str | None:
    """The role this checkout plays: its worktree config first, then its branch name."""
    configured = git("config", "--get", ROLE_CONFIG_KEY, cwd=cwd, check=False).strip()
    if configured in ROLES:
        return configured
    head = current_branch(cwd).split("/", 1)[0]
    return head if head in ROLES else None


def main_checkout(cwd: Path = ROOT) -> Path:
    """The main working tree: the one that owns the shared `.git` directory."""
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=cwd)
    return Path(common).parent


def worktree_path(role: str, cwd: Path = ROOT) -> Path:
    """Where a role's worktree lives: a sibling of the main checkout named `lce-<role>`."""
    return main_checkout(cwd).parent / f"lce-{role}"


def show(ref: str, path: str, cwd: Path = ROOT) -> str | None:
    """A file's content at `ref`, or None when the ref or the path doesn't exist."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=cwd,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout if result.returncode == 0 else None


def status_lines(cwd: Path = ROOT) -> list[str]:
    """`git status --porcelain` lines: every uncommitted change, untracked files included."""
    out = git("status", "--porcelain", cwd=cwd, check=False)
    return [line for line in out.splitlines() if line.strip()]


def ahead_behind(left: str, right: str, cwd: Path = ROOT) -> tuple[int, int] | None:
    """(commits only in `left`, commits only in `right`), or None if either ref is missing."""
    out = git(
        "rev-list", "--left-right", "--count", f"{left}...{right}", cwd=cwd, check=False
    )
    parts = out.split()
    if len(parts) != 2:
        return None
    return int(parts[0]), int(parts[1])


def fetch(cwd: Path = ROOT, timeout: float = 20) -> bool:
    """Fetch the remote quietly; False when offline or it takes too long."""
    try:
        subprocess.run(
            ["git", "fetch", "--quiet", REMOTE],
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            check=True,
        )
    except (subprocess.SubprocessError, OSError):
        return False
    return True
