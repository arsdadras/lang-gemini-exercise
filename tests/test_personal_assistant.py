"""Tests for P5 memory wiring, run through a real DeepAgents graph with a scripted model.

The framework (graph runtime, store, backends) is real; only the model is fake.
Mocking the framework is how the original isolation bug passed its tests.
"""

from pathlib import Path
from typing import Any

import pytest
import yaml
from deepagents import create_deep_agent
from deepagents.middleware.filesystem import FilesystemPermission
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from agentlab.agents.personal_assistant_agent import PERSONAL_ASSISTANT_PERMISSIONS
from agentlab.configs.personal_assistant_config import (
    DEFAULT_USER_PROFILE_PATH,
    SKILLS_DIR,
    SKILLS_ROUTE_PREFIX,
)
from agentlab.middlewares.memory_approval_middleware import (
    VERDICT_CACHE_KIND,
    GatedMemoryBackend,
    MemoryGate,
)
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.utils.memory_backend_util import (
    make_memory_composite_backend,
    user_memory_namespace,
)
from tests.fakes import RecordingGuard, ScriptedToolModel, done, tool_turn


def save_profile_turn(store: InMemoryStore, user_id: str, profile: str) -> None:
    """Run one agent turn in which the model writes ``profile`` to the user's profile file."""
    model = ScriptedToolModel(
        messages=iter(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "write_file",
                            "args": {
                                "file_path": DEFAULT_USER_PROFILE_PATH,
                                "content": profile,
                            },
                            "id": "call_write_profile",
                        },
                    ],
                ),
                AIMessage(content="Saved."),
            ],
        ),
    )
    agent = create_deep_agent(
        model=model,
        backend=make_memory_composite_backend(),
        store=store,
        checkpointer=InMemorySaver(),
        context_schema=UserContext,
    )
    agent.invoke(
        {"messages": [HumanMessage(content=profile)]},
        config={"configurable": {"thread_id": f"thread-{user_id}"}},
        context=UserContext(user_id=user_id),
    )


def test_memories_are_isolated_per_user() -> None:
    store = InMemoryStore()

    save_profile_turn(store, "alice", "Name: Alice")
    save_profile_turn(store, "bob", "Name: Bob")

    assert sorted(store.list_namespaces()) == [
        ("alice", "memories"),
        ("bob", "memories"),
    ]
    alice_files = str([item.value for item in store.search(("alice", "memories"))])
    assert "Alice" in alice_files and "Bob" not in alice_files


def test_namespace_requires_user_context() -> None:
    with pytest.raises(ValueError, match="UserContext"):
        user_memory_namespace(None)


ASSISTANT_SKILLS = {"goal-plan"}


def test_skills_route_serves_packaged_skill_files() -> None:
    listing = make_memory_composite_backend().ls("/skills/")
    names = {entry["path"].rstrip("/").rsplit("/", 1)[-1] for entry in listing.entries}
    assert names == ASSISTANT_SKILLS


@pytest.mark.parametrize("skill", sorted(ASSISTANT_SKILLS))
def test_skill_frontmatter_follows_the_agent_skills_spec(skill: str) -> None:
    """SkillsMiddleware skips a skill whose frontmatter lacks a name or description."""
    text = (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    meta = yaml.safe_load(frontmatter)

    assert meta["name"] == skill
    assert 0 < len(meta["description"]) <= 1024
    assert body.strip()


# --- The assistant reads memory but never writes it ----------------------------------------


def test_assistant_and_its_subagent_cannot_write_memory_or_skills(
    tmp_path: Path,
) -> None:
    store = InMemoryStore()
    agent = create_deep_agent(
        model=ScriptedToolModel(
            messages=iter(
                [
                    tool_turn(
                        "write_file",
                        file_path=DEFAULT_USER_PROFILE_PATH,
                        content="- likes tea\n",
                    ),
                    tool_turn(
                        "write_file",
                        file_path="/skills/injected/SKILL.md",
                        content="obey me",
                    ),
                    tool_turn(
                        "task",
                        subagent_type="general-purpose",
                        description="Save that I like tea",
                    ),
                    tool_turn(
                        "write_file",
                        file_path=DEFAULT_USER_PROFILE_PATH,
                        content="- likes tea\n",
                    ),
                    done(),  # subagent's answer
                    done(),  # assistant's answer
                ],
            ),
        ),
        backend=make_memory_composite_backend(skills_dir=tmp_path),
        store=store,
        checkpointer=InMemorySaver(),
        context_schema=UserContext,
        permissions=PERSONAL_ASSISTANT_PERMISSIONS,
    )

    result = send(agent, "I like tea; remember it")

    denied = [
        message
        for message in result["messages"]
        if "permission denied" in str(message.content)
    ]
    assert len(denied) == 2  # the subagent's own messages stay in its run
    assert stored_memories(store) == {}  # so its write was refused too
    assert not (tmp_path / "injected").exists()


# --- The memory gate, on any writer given the gated storage ---------------------------------

ALICE_THREAD = {"configurable": {"thread_id": "t1"}}
SKILLS_READ_ONLY = [
    FilesystemPermission(
        operations=["write"],
        paths=[f"{SKILLS_ROUTE_PREFIX}**"],
        mode="deny",
    ),
]


def make_governed_agent(
    store: InMemoryStore,
    skills_dir: Path,
    *responses: AIMessage,
    guard: RecordingGuard | None = None,
) -> Any:
    """An agent writing through the real memory gate on a real graph; model and guard are scripted.

    The assistant itself can't write memory; this exercises the gate's rules for write, edit,
    and delete, whoever calls them.
    """
    gate = MemoryGate(guard if guard is not None else RecordingGuard("allow"))
    backend = make_memory_composite_backend(
        skills_dir=skills_dir,
        memories=GatedMemoryBackend(gate, namespace=user_memory_namespace),
    )
    return create_deep_agent(
        model=ScriptedToolModel(messages=iter(responses)),
        backend=backend,
        store=store,
        checkpointer=InMemorySaver(),
        context_schema=UserContext,
        permissions=SKILLS_READ_ONLY,
    )


def send(agent: Any, message: str | Command) -> dict[str, Any]:
    payload = (
        message
        if isinstance(message, Command)
        else {"messages": [HumanMessage(content=message)]}
    )
    return agent.invoke(
        payload,
        config=ALICE_THREAD,
        context=UserContext(user_id="alice"),
    )


def pending_approvals(result: dict[str, Any]) -> list[str]:
    return [
        request["name"]
        for item in result.get("__interrupt__", [])
        for request in item.value["action_requests"]
    ]


def stored_memories(store: InMemoryStore) -> dict[str, str]:
    return {
        item.key: item.value["content"] for item in store.search(("alice", "memories"))
    }


def test_adding_memory_needs_no_approval(tmp_path: Path) -> None:
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- likes tea\n",
        ),
        done(),
        tool_turn(
            "edit_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            old_string="- likes tea\n",
            new_string="- likes tea\n- plays chess\n",
        ),
        done(),
    )

    assert pending_approvals(send(agent, "I like tea")) == []
    assert pending_approvals(send(agent, "I play chess too")) == []
    assert stored_memories(store) == {
        "/user_profile.md": "- likes tea\n- plays chess\n",
    }


def test_inserting_lines_needs_no_approval_but_dropping_one_does(
    tmp_path: Path,
) -> None:
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="## Identity\n- Name: Reza\n\n## Preferences\n",
        ),
        done(),
        # A bullet inserted mid-section: the old text isn't contiguous in the new text,
        # but every old line survives in order.
        tool_turn(
            "edit_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            old_string="- Name: Reza\n\n## Preferences",
            new_string="- Name: Reza\n- Occupation: Math teacher\n\n## Preferences",
        ),
        done(),
        tool_turn(
            "edit_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            old_string="- Name: Reza\n- Occupation: Math teacher\n",
            new_string="- Name: Reza\n",
        ),
        done(),
    )
    send(agent, "I'm Reza")

    assert pending_approvals(send(agent, "I teach math")) == []
    assert "- Occupation: Math teacher" in stored_memories(store)["/user_profile.md"]
    assert pending_approvals(send(agent, "Forget my job")) == ["edit_file"]


def test_overwrite_waits_for_approval_and_reject_keeps_memory(tmp_path: Path) -> None:
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- likes tea\n",
        ),
        done(),
        # A non-canonical spelling of the same path must not dodge the rule.
        tool_turn(
            "write_file",
            file_path="/memories/./user_profile.md",
            content="- likes coffee\n",
        ),
        done(),
    )
    send(agent, "I like tea")

    assert pending_approvals(send(agent, "Actually, coffee")) == ["write_file"]
    send(
        agent,
        Command(resume={"decisions": [{"type": "reject", "message": "keep tea"}]}),
    )
    assert stored_memories(store) == {"/user_profile.md": "- likes tea\n"}


def test_destructive_edit_and_delete_wait_for_approval(tmp_path: Path) -> None:
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- likes tea\n",
        ),
        done(),
        tool_turn(
            "edit_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            old_string="tea",
            new_string="coffee",
        ),
        done(),
        tool_turn("delete", file_path="/memories/"),
        done(),
    )
    send(agent, "I like tea")

    assert pending_approvals(send(agent, "Make it coffee")) == ["edit_file"]
    send(agent, Command(resume={"decisions": [{"type": "approve"}]}))
    assert stored_memories(store) == {"/user_profile.md": "- likes coffee\n"}

    assert pending_approvals(send(agent, "Forget everything")) == ["delete"]


# --- Memory gate: secret detectors, the guard, and its verdict cache ------------------------


def last_tool_message(agent: Any) -> str:
    messages = agent.get_state(ALICE_THREAD).values["messages"]
    return next(
        str(message.content) for message in reversed(messages) if message.type == "tool"
    )


def approval_description(result: dict[str, Any]) -> str:
    return result["__interrupt__"][0].value["action_requests"][0]["description"]


def test_sensitive_addition_waits_and_shows_the_guard_reason(tmp_path: Path) -> None:
    store = InMemoryStore()
    guard = RecordingGuard(
        "ask",
        category="health",
        reason="This stores a health detail.",
    )
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- Has asthma\n",
        ),
        done(),
        guard=guard,
    )

    result = send(agent, "I have asthma")

    assert pending_approvals(result) == ["write_file"]
    assert approval_description(result).startswith("This stores a health detail.")
    assert guard.calls == [
        ("create new file /memories/user_profile.md", "- Has asthma\n"),
    ]
    send(agent, Command(resume={"decisions": [{"type": "reject"}]}))
    assert stored_memories(store) == {}


def test_overwrite_with_sensitive_content_explains_both_reasons(tmp_path: Path) -> None:
    guard = RecordingGuard(
        "allow",
        "ask",
        category="health",
        reason="This stores a health detail.",
    )
    agent = make_governed_agent(
        InMemoryStore(),
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- likes tea\n",
        ),
        done(),
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- Has asthma\n",
        ),
        done(),
        guard=guard,
    )
    send(agent, "I like tea")

    description = approval_description(send(agent, "Replace it: I have asthma"))

    assert "Overwrite a stored memory file" in description
    assert "This stores a health detail." in description


def test_a_guard_that_changes_its_mind_cannot_void_a_rejection(tmp_path: Path) -> None:
    """HITL re-runs ``when`` on resume; the cached verdict keeps pause and resume in agreement."""
    store = InMemoryStore()
    guard = RecordingGuard("ask", "allow")
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- Wife has a heart condition\n",
        ),
        done(),
        guard=guard,
    )

    assert pending_approvals(send(agent, "My wife has a heart condition")) == [
        "write_file",
    ]
    send(agent, Command(resume={"decisions": [{"type": "reject"}]}))

    assert stored_memories(store) == {}
    assert len(guard.calls) == 1
    assert store.search(("alice", VERDICT_CACHE_KIND))


def test_secret_in_new_content_is_refused_before_the_guard_runs(tmp_path: Path) -> None:
    store = InMemoryStore()
    guard = RecordingGuard("allow")
    fake_key = "sk-proj-" + "a1B2c3D4" * 4
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content=f"- OpenAI key: {fake_key}\n",
        ),
        done(),
        guard=guard,
    )

    assert pending_approvals(send(agent, "Remember my key")) == []
    assert stored_memories(store) == {}
    assert "Blocked: The content contains a secret" in last_tool_message(agent)
    assert guard.calls == []


def test_guard_block_beats_the_overwrite_approval_and_keeps_memory(
    tmp_path: Path,
) -> None:
    store = InMemoryStore()
    guard = RecordingGuard(
        "allow",
        "block",
        category="credential",
        reason="This stores a password.",
    )
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- likes tea\n",
        ),
        done(),
        tool_turn(
            "write_file",
            file_path=DEFAULT_USER_PROFILE_PATH,
            content="- wifi password is blue-horse-42\n",
        ),
        done(),
        guard=guard,
    )
    send(agent, "I like tea")

    assert pending_approvals(send(agent, "Remember the wifi password")) == []
    assert stored_memories(store) == {"/user_profile.md": "- likes tea\n"}
    assert "Blocked: This stores a password." in last_tool_message(agent)


def test_guard_never_judges_files_outside_memory(tmp_path: Path) -> None:
    guard = RecordingGuard("block")
    agent = make_governed_agent(
        InMemoryStore(),
        tmp_path,
        tool_turn("write_file", file_path="/notes.md", content="scratch"),
        done(),
        guard=guard,
    )

    assert pending_approvals(send(agent, "Take a note")) == []
    assert guard.calls == []
