"""Role worktrees, cross-branch inbox, session hooks, and handoff, on real temporary git repos."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import handoff
import inbox
import session_hooks
import setup_worktrees
import workspace

OUTBOX = (
    "# Lead Outbox\n\n## Open\n\n"
    "### LD-001 | to mentor | directive | {status}\n\nIssued 2026-09-27. Move in.\n"
)


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A main checkout with an `origin` remote, isolated from the user's git config."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / "gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for key in ("GIT_AUTHOR", "GIT_COMMITTER"):
        monkeypatch.setenv(f"{key}_NAME", "Test")
        monkeypatch.setenv(f"{key}_EMAIL", "test@example.com")
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "--quiet", "--bare", "-b", "main", str(origin))
    main = tmp_path / "project"
    git(tmp_path, "init", "--quiet", "-b", "main", str(main))
    write(main, ".gitignore", ".env\nCLAUDE.local.md\n")  # as in the repo's .gitignore
    write(main, "offices/lead/OUTBOX.md", OUTBOX.format(status="open"))
    write(main, "offices/mentor/STATE.md", "# Mentor State\n\nR0 topic 3 next.\n")
    git(main, "add", "-A")
    git(main, "commit", "--quiet", "-m", "init")
    git(main, "remote", "add", "origin", str(origin))
    git(main, "push", "--quiet", "-u", "origin", "main")
    return main


def worktree(main: Path, role: str) -> Path:
    setup_worktrees.setup(main, role, sync=False, push=True)
    return main.parent / f"lce-{role}"


def test_role_comes_from_worktree_config_before_branch(project):
    assert workspace.detect_role(project) is None
    git(project, "checkout", "--quiet", "-b", "mentor/r0")
    assert workspace.detect_role(project) == "mentor"
    git(project, "config", "extensions.worktreeConfig", "true")
    git(project, "config", "--worktree", workspace.ROLE_CONFIG_KEY, "research")
    assert workspace.detect_role(project) == "research"


def test_setup_builds_a_role_worktree_and_is_idempotent(project):
    write(project, ".env", "SECRET_NAME=value\n")
    first = setup_worktrees.setup(project, "research", sync=False, push=True)
    path = project.parent / "lce-research"
    assert workspace.detect_role(path) == "research"
    assert workspace.current_branch(path) == "research"
    assert "@offices/research/README.md" in (path / "CLAUDE.local.md").read_text(
        encoding="utf-8"
    )
    assert (path / ".env").read_text(encoding="utf-8") == "SECRET_NAME=value\n"
    assert git(project, "ls-remote", "origin", "research")
    assert any("new branch research" in line for line in first)

    second = setup_worktrees.setup(project, "research", sync=False, push=True)
    assert "  worktree present" in second
    assert "  CLAUDE.local.md present" in second


def test_inbox_reads_the_senders_branch_over_a_stale_copy(project):
    lead, mentor = worktree(project, "lead"), worktree(project, "mentor")
    incoming, _ = inbox.inbox(inbox.load(mentor), "mentor")
    assert [m.id for m in incoming] == ["LD-001"]

    write(lead, "offices/lead/OUTBOX.md", OUTBOX.format(status="closed"))
    git(lead, "commit", "--quiet", "-am", "docs(lead): close LD-001")
    git(lead, "push", "--quiet", "origin", "lead")
    assert workspace.fetch(mentor)
    incoming, _ = inbox.inbox(inbox.load(mentor), "mentor")
    assert incoming == []


def test_start_report_gives_role_state_and_inbox(project):
    mentor = worktree(project, "mentor")
    report = session_hooks.start_report(mentor)
    assert "role mentor, branch mentor" in report
    assert "Uncommitted: 0 path(s), clean" in report
    assert "R0 topic 3 next." in report
    assert "LD-001 from lead | directive | Issued 2026-09-27. Move in." in report

    assert "plays no role" in session_hooks.start_report(project)


def test_stop_warns_only_about_unsaved_work_in_a_role_worktree(project):
    research = worktree(project, "research")
    assert session_hooks.stop_message(research) is None
    write(research, "offices/research/notes.md", "draft\n")
    assert "1 uncommitted path(s)" in session_hooks.stop_message(research)
    write(project, "scratch.txt", "x\n")
    assert session_hooks.stop_message(project) is None


def test_handoff_commits_and_pushes_the_role_branch(project, monkeypatch):
    monkeypatch.setattr(handoff, "pull_request", lambda root, branch, create: "stub")
    lead = worktree(project, "lead")
    write(lead, "offices/lead/STATE.md", "# Lead State\n")
    lines = handoff.handoff(lead, "record the draft", wip=True)
    assert git(lead, "log", "-1", "--format=%s") == "wip(lead): record the draft"
    assert git(lead, "rev-parse", "HEAD") in git(project, "ls-remote", "origin", "lead")
    assert lines[0].startswith("lead @ lead: committed")
    assert lines[1].startswith("Branch vs main: 1 ahead of main, 0 behind")
    assert lines[2] == "Pull request: stub"


def test_handoff_refuses_outside_a_role_worktree(project):
    with pytest.raises(handoff.HandoffError):
        handoff.handoff(project, "anything")


def test_start_report_asks_for_the_charter_without_claude_local(project):
    git(project, "checkout", "--quiet", "-b", "research")
    report = session_hooks.start_report(project)
    assert "role research, branch research" in report
    assert "read offices/research/README.md before anything else" in report


def test_setup_ignores_claude_local_on_branches_without_the_gitignore(project):
    write(project, ".gitignore", ".env\n")
    git(project, "commit", "--quiet", "-am", "an older .gitignore")
    git(project, "push", "--quiet", "origin", "main")
    mentor = worktree(project, "mentor")
    assert (mentor / "CLAUDE.local.md").exists()
    assert workspace.status_lines(mentor) == []
