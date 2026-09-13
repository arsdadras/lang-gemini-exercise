"""Unit tests for P5 Personal Assistant agent, memory backend routing, and skills library."""

from deepagents.backends import FilesystemBackend
from langgraph.store.memory import InMemoryStore

from configs.personal_assistant_config import (
    DEFAULT_USER_ID,
    MEMORIES_ROUTE_PREFIX,
    SKILLS_ROUTE_PREFIX,
)
from utils.memory_backend_util import (
    make_memory_composite_backend,
    make_memory_namespace,
    make_skills_namespace,
)


def test_make_memory_namespace_fallback():
    """Verify namespace falls back to DEFAULT_USER_ID when runtime is None or unconfigured."""
    assert make_memory_namespace(None) == (DEFAULT_USER_ID, "memories")

    class MockRuntime:
        def __init__(self):
            self.config = {"configurable": {}}

    assert make_memory_namespace(MockRuntime()) == (DEFAULT_USER_ID, "memories")


def test_make_memory_namespace_configurable():
    """Verify namespace extracts user_id correctly from runtime config."""

    class MockRuntime:
        def __init__(self):
            self.config = {"configurable": {"user_id": "alice"}}

    assert make_memory_namespace(MockRuntime()) == ("alice", "memories")


def test_make_skills_namespace():
    """Verify skills namespace returns shared static namespace tuple."""
    assert make_skills_namespace(None) == ("skills",)


def test_memory_composite_backend_routing(tmp_path):
    """Verify CompositeBackend routes /memories/ to Store and /skills/ to Filesystem."""
    # Setup test skill on disk
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: test-skill\ndescription: Test\n---\nBody", encoding="utf-8")

    store = InMemoryStore()
    backend = make_memory_composite_backend(
        store=store,
        skills_backend=FilesystemBackend(root_dir=str(skills_dir)),
    )

    # 1. Verify /skills/ route reads directly from filesystem
    read_res = backend.read(f"{SKILLS_ROUTE_PREFIX}test-skill/SKILL.md")
    assert read_res.error is None
    assert "test-skill" in read_res.file_data["content"]

    # 2. Verify /skills/ ls discovers the skill directory
    ls_res = backend.ls(SKILLS_ROUTE_PREFIX)
    paths = [e["path"] for e in ls_res.entries]
    assert f"{SKILLS_ROUTE_PREFIX}test-skill/" in paths

    # 3. Verify /memories/ route writes to BaseStore
    write_res = backend.write(f"{MEMORIES_ROUTE_PREFIX}notes.txt", "User memory note")
    assert write_res.error is None
    stored_items = store.search((DEFAULT_USER_ID, "memories"))
    assert len(stored_items) == 1
    assert stored_items[0].key in {"notes.txt", "/notes.txt"}
