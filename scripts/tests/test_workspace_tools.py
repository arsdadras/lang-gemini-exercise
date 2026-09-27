"""Role worktrees, cross-branch inbox, session hooks, and handoff, on real temporary git repos."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import handoff
import inbox
import pr_report
import session_hooks
import setup_worktrees
import workspace

OWNERSHIP = (
    "# Ownership\n\n| Path | Holds | Writer | Roles |\n| :--- | :--- | :--- | :--- |\n"
    "| `offices/lead/` | lead office | Lead | lead |\n"
    "| `offices/mentor/`, `src/` | mentor office; code | Mentor | mentor |\n"
    "| `archive/` | retired | owner | all |\n"
)

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
    write(main, "library/governance/ownership.md", OWNERSHIP)
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


def test_the_repositorys_ownership_map_parses():
    rules = workspace.ownership_rules(workspace.ROOT)
    assert workspace.owners("src/agentlab/apps/rag_app.py", rules) == {"mentor"}
    assert workspace.owners("AGENTS.md", rules) == {"lead", "mentor"}
    assert workspace.owners("offices/research/STATE.md", rules) == {"research"}
    assert workspace.owners("archive/docs/ROADMAP.md", rules) == {"all"}
    assert workspace.owners("alireza/notes.ipynb", rules) == {"none"}
    assert workspace.owners("a-new-top-level-file.txt", rules) == {"lead"}


def edit(path: Path, tool: str = "Edit") -> dict:
    return {"tool_name": tool, "tool_input": {"file_path": str(path)}}


def test_guard_keeps_each_role_inside_its_own_paths(project, monkeypatch):
    monkeypatch.delenv(session_hooks.GUARD_OFF_ENV, raising=False)
    mentor, lead = worktree(project, "mentor"), worktree(project, "lead")
    assert session_hooks.guard_reason(mentor, edit(mentor / "src" / "a.py")) is None
    assert session_hooks.guard_reason(mentor, edit(mentor / "archive" / "x.md")) is None
    owned = session_hooks.guard_reason(mentor, edit(mentor / "offices/lead/STATE.md"))
    assert "offices/lead/STATE.md belongs to lead" in owned
    foreign = session_hooks.guard_reason(mentor, edit(lead / "offices/lead/STATE.md"))
    assert "another checkout" in foreign
    assert (
        session_hooks.guard_reason(mentor, edit(project.parent / "outside.txt")) is None
    )
    assert (
        session_hooks.guard_reason(mentor, {"tool_name": "Read", "tool_input": {}})
        is None
    )
    relative = {"tool_name": "Write", "tool_input": {"file_path": "offices/lead/x.md"}}
    reason = session_hooks.guard_reason(mentor, {**relative, "cwd": str(mentor)})
    assert "belongs to lead" in reason


def test_guard_refuses_edits_in_a_checkout_with_no_role(project, monkeypatch):
    monkeypatch.delenv(session_hooks.GUARD_OFF_ENV, raising=False)
    worktree(project, "lead")
    reason = session_hooks.guard_reason(project, edit(project / "offices/lead/x.md"))
    assert "plays no role" in reason
    assert "change_directory" in reason
    monkeypatch.setenv(session_hooks.GUARD_OFF_ENV, "off")
    assert (
        session_hooks.guard_reason(project, edit(project / "offices/lead/x.md")) is None
    )


def test_prompt_hook_announces_each_new_message_once(project):
    mentor, lead = worktree(project, "mentor"), worktree(project, "lead")
    session_hooks.start_report(mentor, online=False, session_id="s1")
    assert session_hooks.prompt_report(mentor, "s1", online_check=False) is None

    notice = "\n### LD-002 | to mentor | notice | open\n\nIssued 2026-09-27. Hooks are live.\n"
    write(lead, "offices/lead/OUTBOX.md", OUTBOX.format(status="open") + notice)
    git(lead, "commit", "--quiet", "-am", "docs(lead): LD-002")
    git(lead, "push", "--quiet", "origin", "lead")
    assert workspace.fetch(mentor)
    report = session_hooks.prompt_report(mentor, "s1", online_check=False)
    assert "LD-002 from lead | notice | Issued 2026-09-27. Hooks are live." in report
    assert "LD-001" not in report
    assert session_hooks.prompt_report(mentor, "s1", online_check=False) is None


def test_pr_report_lists_new_messages_and_foreign_files(project):
    mentor = worktree(project, "mentor")
    base = git(mentor, "rev-parse", "HEAD")
    write(mentor, "src/a.py", "x = 1\n")
    write(mentor, "offices/lead/STATE.md", "# edited by the wrong role\n")
    outbox = "# Mentor Outbox\n\n### MN-001 | to lead | request | open\n\nIssued 2026-09-27. Decide.\n"
    write(mentor, "offices/mentor/OUTBOX.md", outbox)
    git(mentor, "add", "-A")
    git(mentor, "commit", "--quiet", "-m", "wip(mentor): mixed")
    head = git(mentor, "rev-parse", "HEAD")

    report = pr_report.pr_report(base, head, "mentor", root=mentor)
    assert (
        "**MN-001** new, mentor to lead, request, open: Issued 2026-09-27. Decide."
        in report
    )
    assert "offices/lead/STATE.md (owner: lead)" in report
    assert "src/a.py" not in report
    assert "not a role branch" in pr_report.pr_report(
        base, head, "dependabot/x", root=mentor
    )


def test_summary_lists_open_messages_by_recipient(project):
    text = pr_report.summary(project)
    assert "### mentor: 1 open" in text
    assert "**LD-001** from lead, directive" in text
