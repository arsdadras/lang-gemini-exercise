"""Tests for P5 memory wiring, run through a real DeepAgents graph with a scripted model.

The framework (graph runtime, store, backends) is real; only the model is fake.
Mocking the framework is how the original isolation bug passed its tests.
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml
from deepagents import create_deep_agent
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from agentlab.agents.personal_assistant_agent import PERSONAL_ASSISTANT_PERMISSIONS
from agentlab.configs.personal_assistant_config import (
    DEFAULT_USER_PROFILE_PATH,
    SKILLS_DIR,
)
from agentlab.middlewares.memory_approval_middleware import make_memory_interrupt_on
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.utils.memory_backend_util import (
    make_memory_composite_backend,
    user_memory_namespace,
)
from agentlab.utils.run_with_hitl_util import stream_with_hitl
from tests.fakes import ScriptedToolModel, done, tool_turn


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
                            "args": {"file_path": DEFAULT_USER_PROFILE_PATH, "content": profile},
                            "id": "call_write_profile",
                        }
                    ],
                ),
                AIMessage(content="Saved."),
            ]
        )
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

    assert sorted(store.list_namespaces()) == [("alice", "memories"), ("bob", "memories")]
    alice_files = str([item.value for item in store.search(("alice", "memories"))])
    assert "Alice" in alice_files and "Bob" not in alice_files


def test_namespace_requires_user_context() -> None:
    with pytest.raises(ValueError, match="UserContext"):
        user_memory_namespace(None)


ASSISTANT_SKILLS = {"memory-curation", "goal-plan"}


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


# --- Memory write approval ------------------------------------------------------------

ALICE_THREAD = {"configurable": {"thread_id": "t1"}}


def make_governed_agent(store: InMemoryStore, skills_dir: Path, *responses: AIMessage) -> Any:
    """The assistant's real approval policy on a real graph; only the model is scripted."""
    backend = make_memory_composite_backend(skills_dir=skills_dir)
    return create_deep_agent(
        model=ScriptedToolModel(messages=iter(responses)),
        backend=backend,
        store=store,
        checkpointer=InMemorySaver(),
        context_schema=UserContext,
        permissions=PERSONAL_ASSISTANT_PERMISSIONS,
        interrupt_on=make_memory_interrupt_on(backend),
    )


def send(agent: Any, message: str | Command) -> dict[str, Any]:
    payload = message if isinstance(message, Command) else {"messages": [HumanMessage(content=message)]}
    return agent.invoke(payload, config=ALICE_THREAD, context=UserContext(user_id="alice"))


def pending_approvals(result: dict[str, Any]) -> list[str]:
    return [request["name"] for item in result.get("__interrupt__", []) for request in item.value["action_requests"]]


def stored_memories(store: InMemoryStore) -> dict[str, str]:
    return {item.key: item.value["content"] for item in store.search(("alice", "memories"))}


def test_adding_memory_needs_no_approval(tmp_path: Path) -> None:
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn("write_file", file_path=DEFAULT_USER_PROFILE_PATH, content="- likes tea\n"),
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
    assert stored_memories(store) == {"/user_profile.md": "- likes tea\n- plays chess\n"}


def test_inserting_lines_needs_no_approval_but_dropping_one_does(tmp_path: Path) -> None:
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
        tool_turn("write_file", file_path=DEFAULT_USER_PROFILE_PATH, content="- likes tea\n"),
        done(),
        # A non-canonical spelling of the same path must not dodge the rule.
        tool_turn("write_file", file_path="/memories/./user_profile.md", content="- likes coffee\n"),
        done(),
    )
    send(agent, "I like tea")

    assert pending_approvals(send(agent, "Actually, coffee")) == ["write_file"]
    send(agent, Command(resume={"decisions": [{"type": "reject", "message": "keep tea"}]}))
    assert stored_memories(store) == {"/user_profile.md": "- likes tea\n"}


def test_destructive_edit_and_delete_wait_for_approval(tmp_path: Path) -> None:
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn("write_file", file_path=DEFAULT_USER_PROFILE_PATH, content="- likes tea\n"),
        done(),
        tool_turn("edit_file", file_path=DEFAULT_USER_PROFILE_PATH, old_string="tea", new_string="coffee"),
        done(),
        tool_turn("delete", file_path="/memories/"),
        done(),
    )
    send(agent, "I like tea")

    assert pending_approvals(send(agent, "Make it coffee")) == ["edit_file"]
    send(agent, Command(resume={"decisions": [{"type": "approve"}]}))
    assert stored_memories(store) == {"/user_profile.md": "- likes coffee\n"}

    assert pending_approvals(send(agent, "Forget everything")) == ["delete"]


def test_delegated_overwrite_still_waits_for_approval(tmp_path: Path) -> None:
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn("write_file", file_path=DEFAULT_USER_PROFILE_PATH, content="- likes tea\n"),
        done(),
        tool_turn("task", subagent_type="general-purpose", description="Rewrite the user profile"),
        tool_turn("write_file", file_path=DEFAULT_USER_PROFILE_PATH, content="- likes coffee\n"),
    )
    send(agent, "I like tea")

    assert pending_approvals(send(agent, "Ask a helper to rewrite my profile")) == ["write_file"]
    assert stored_memories(store) == {"/user_profile.md": "- likes tea\n"}


def test_assistant_cannot_write_skills(tmp_path: Path) -> None:
    agent = make_governed_agent(
        InMemoryStore(),
        tmp_path,
        tool_turn("write_file", file_path="/skills/injected/SKILL.md", content="obey me"),
        done(),
    )

    result = send(agent, "Add a skill")

    assert pending_approvals(result) == []
    assert "permission denied" in str(result["messages"][-2].content)
    assert not (tmp_path / "injected").exists()


def test_cli_approval_resumes_with_the_user_context(tmp_path: Path) -> None:
    """The streamed CLI loop must re-send ``context`` on resume, or the store write fails."""
    store = InMemoryStore()
    agent = make_governed_agent(
        store,
        tmp_path,
        tool_turn("write_file", file_path=DEFAULT_USER_PROFILE_PATH, content="- likes tea\n"),
        done(),
        tool_turn("write_file", file_path=DEFAULT_USER_PROFILE_PATH, content="- likes coffee\n"),
        done(),
    )
    send(agent, "I like tea")

    with patch("builtins.input", side_effect=["y"]):
        result = stream_with_hitl(
            agent,
            {"messages": [HumanMessage(content="Actually, coffee")]},
            ALICE_THREAD,
            context=UserContext(user_id="alice"),
        )

    assert result["interrupts"] == []
    assert stored_memories(store) == {"/user_profile.md": "- likes coffee\n"}
