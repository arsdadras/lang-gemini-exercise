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


def test_print_user_memories_when_empty(
    store: InMemoryStore,
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_user_memories(store, "nobody")
    output = capsys.readouterr().out
    assert "No stored memories for user 'nobody'" in output


def test_print_history_empty_and_populated(
    store: InMemoryStore,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from agentlab.apps.personal_assistant_app import print_history

    # Empty history
    print_history(store, "nobody")
    assert "No previous versions for user 'nobody'" in capsys.readouterr().out

    # Populated history
    store.put(
        ("alice", "memory_history"),
        "v1",
        {
            "path": "/notes.md",
            "content": "previous content",
            "saved_at": 1700000000.0,
            "replaced_by": "edit",
        },
    )
    print_history(store, "alice")
    output = capsys.readouterr().out
    assert "/notes.md" in output
    assert "Previous versions for 'alice'" in output


def test_frontmatter_parser() -> None:
    from agentlab.apps.personal_assistant_app import _frontmatter

    # No frontmatter
    assert _frontmatter("Just text without dashes") == {}

    # Valid YAML frontmatter
    text_valid = "---\nname: my_skill\ndescription: A helpful skill\n---\n# Body"
    meta = _frontmatter(text_valid)
    assert meta.get("name") == "my_skill"
    assert meta.get("description") == "A helpful skill"

    # Malformed YAML
    text_invalid = "---\n: : bad yaml\n---\nBody"
    assert _frontmatter(text_invalid) == {}


def test_print_available_skills_packaged_and_published(
    store: InMemoryStore,
    tmp_path: pytest.TempPathFactory,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from pathlib import Path

    from agentlab.apps.personal_assistant_app import print_available_skills
    from agentlab.nodes.skill_designer_node import PUBLISHED_SKILLS_NAMESPACE

    skills_dir = Path(str(tmp_path)) / "skills"
    skills_dir.mkdir()
    skill_a = skills_dir / "skill_a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text(
        "---\nname: Skill Alpha\ndescription: Does alpha things\n---\n",
        encoding="utf-8",
    )

    # Put a published skill in the store
    store.put(
        PUBLISHED_SKILLS_NAMESPACE,
        "/published_beta/SKILL.md",
        {
            "content": "---\nname: Skill Beta\ndescription: Does beta things\n---\n",
        },
    )

    print_available_skills(store=store, skills_dir=skills_dir)
    output = capsys.readouterr().out
    assert "Available skills" in output
    assert "Skill Alpha: Does alpha things" in output
    assert "Skill Beta: Does beta things" in output
