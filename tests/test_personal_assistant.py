"""Tests for P5 memory wiring, run through a real DeepAgents graph with a scripted model.

The framework (graph runtime, store, backends) is real; only the model is fake.
Mocking the framework is how the original isolation bug passed its tests.
"""

from typing import Any

import pytest
from deepagents import create_deep_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from agentlab.configs.personal_assistant_config import DEFAULT_USER_PROFILE_PATH
from agentlab.state.context_state import UserContext
from agentlab.utils.memory_backend_util import (
    make_memory_composite_backend,
    user_memory_namespace,
)


class ScriptedToolModel(GenericFakeChatModel):
    """Fake chat model that accepts tool binding, as the agent loop requires."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedToolModel":
        return self


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


def test_skills_route_serves_packaged_skill_files() -> None:
    listing = make_memory_composite_backend().ls("/skills/")
    names = {entry["path"].rstrip("/").rsplit("/", 1)[-1] for entry in listing.entries}
    assert {"python-pro", "clean-committer"} <= names
