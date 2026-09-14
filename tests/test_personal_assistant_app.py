"""Tests for the P5 CLI's memory display (``/memory`` preview and ``/more``)."""

import pytest
from langgraph.store.memory import InMemoryStore

from agentlab.apps.personal_assistant_app import print_user_memories

LONG_PROFILE = "\n".join(f"- fact {number}" for number in range(1, 16))


@pytest.fixture
def store() -> InMemoryStore:
    store = InMemoryStore()
    store.put(("alice", "memories"), "/user_profile.md", {"content": LONG_PROFILE})
    return store


def test_memory_preview_truncates_long_files_and_points_to_more(
    store: InMemoryStore, capsys: pytest.CaptureFixture[str]
) -> None:
    print_user_memories(store, "alice")

    output = capsys.readouterr().out
    assert "- fact 10" in output
    assert "- fact 11" not in output
    assert "[5 more lines, /more shows everything]" in output


def test_more_prints_every_line(store: InMemoryStore, capsys: pytest.CaptureFixture[str]) -> None:
    print_user_memories(store, "alice", max_lines=None)

    output = capsys.readouterr().out
    assert "- fact 15" in output
    assert "more lines" not in output
