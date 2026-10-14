"""Unit tests for `scripts/reviewer_session_hook.py`."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.reviewer_session_hook import (
    ROOT,
    build_reviewer_briefing,
    categorize_file,
    get_git_branch,
    get_recent_commits,
    handle_hook,
    run_git_command,
    should_inject,
)


def test_should_inject_only_on_reviewer_command() -> None:
    assert should_inject({"userRequest": "/reviewer"}) is True
    assert should_inject({"userRequest": "Salam, lotfan /reviewer ro ejra kon"}) is True
    assert should_inject({"userRequest": "/mentor"}) is False
    assert should_inject({"userRequest": "salam"}) is False
    assert should_inject({}) is False


def test_categorize_file_maps_all_architectural_rungs() -> None:
    assert "Rung-2" in categorize_file("src/agentlab/workflows/research_workflow.py")
    assert "Rung-2" in categorize_file("src/agentlab/subagents/research_subagent.py")
    assert "Rung-2" in categorize_file(
        "src/agentlab/schemas/output/rag_output_schema.py"
    )
    assert "Rung-3: Coordinators" in categorize_file(
        "src/agentlab/agents/coordinators/repo_insight_coordinator.py"
    )
    assert "Rung-1: Role Agents" in categorize_file(
        "src/agentlab/agents/researcher_agent.py"
    )
    assert "Rung-1: LangGraph" in categorize_file(
        "src/agentlab/graphs/research_graph.py"
    )
    assert "Rung-1: LangGraph" in categorize_file("src/agentlab/nodes/research_node.py")
    assert "Rung-0/1: Tools" in categorize_file("src/agentlab/tools/web_search_tool.py")
    assert "Rung-0: Primitives" in categorize_file("src/agentlab/models/llm_model.py")
    assert "Rung-0: Primitives" in categorize_file("src/agentlab/utils/failure_util.py")
    assert "Quality Gate" in categorize_file("tests/test_specialist_contract.py")
    assert "Governance" in categorize_file("mentor/STATE.md")
    assert "Customizations" in categorize_file(".agents/skills/reviewer/SKILL.md")
    assert "Support" in categorize_file("pyproject.toml")


def test_handle_hook_returns_empty_when_not_invoked(tmp_path: Path) -> None:
    payload = json.dumps({"invocationNum": 1, "userRequest": "hi"})
    assert handle_hook(payload, repo_root=tmp_path) == {}


def test_handle_hook_emits_ephemeral_message_on_reviewer_command() -> None:
    payload = json.dumps({"userRequest": "/reviewer check changes"})
    result = handle_hook(payload, repo_root=ROOT)
    assert "ephemeralMessage" in result
    msg = result["ephemeralMessage"]
    assert "[REVIEWER & TESTER ACTIVATION]" in msg
    assert "Active Branch:" in msg
    assert "ADR-0033" in msg
    assert "Pragmatic Testing" in msg
    assert "Critical Vigilance" in msg


def test_run_git_command_handles_invalid_commands_gracefully(tmp_path: Path) -> None:
    res = run_git_command(["invalid-git-command-xyz"], cwd=tmp_path)
    assert res == ""


def test_get_git_branch_falls_back_on_non_git_dir(tmp_path: Path) -> None:
    branch = get_git_branch(cwd=tmp_path)
    assert branch in ("unknown", "")


def test_build_reviewer_briefing_with_empty_git_dir(tmp_path: Path) -> None:
    briefing = build_reviewer_briefing(cwd=tmp_path)
    assert "[REVIEWER & TESTER ACTIVATION]" in briefing
    assert "no modified or committed files" in briefing


def test_get_recent_commits_returns_list() -> None:
    commits = get_recent_commits(cwd=ROOT, limit=3)
    assert isinstance(commits, list)
    if commits:
        assert isinstance(commits[0], str)
