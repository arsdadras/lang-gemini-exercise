"""Tests for the P5 CLI: memory display (``/memory``, ``/more``) and input sanitizing."""

import pytest
from langgraph.store.memory import InMemoryStore

from agentlab.apps.personal_assistant_app import (
    print_user_memories,
    sanitize_user_input,
)

LONG_PROFILE = "\n".join(f"- fact {number}" for number in range(1, 16))


@pytest.fixture
def store() -> InMemoryStore:
    store = InMemoryStore()
    store.put(("alice", "memories"), "/user_profile.md", {"content": LONG_PROFILE})
    return store


def test_memory_preview_truncates_long_files_and_points_to_more(
    store: InMemoryStore,
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_user_memories(store, "alice")

    output = capsys.readouterr().out
    assert "- fact 10" in output
    assert "- fact 11" not in output
    assert "[5 more lines, /more shows everything]" in output


def test_more_prints_every_line(
    store: InMemoryStore,
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_user_memories(store, "alice", max_lines=None)

    output = capsys.readouterr().out
    assert "- fact 15" in output
    assert "more lines" not in output


def test_secrets_are_removed_from_user_input_with_a_notice(
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_key = "sk-proj-" + "a1B2c3D4" * 4

    sanitized = sanitize_user_input(f"remember my key {fake_key}")

    assert sanitized == "remember my key [SECRET_DETECTED]"
    assert "Removed 1 secret(s)" in capsys.readouterr().out


def test_ordinary_input_passes_through_silently(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        sanitize_user_input("my email is sam@example.com")
        == "my email is sam@example.com"
    )
    assert capsys.readouterr().out == ""
