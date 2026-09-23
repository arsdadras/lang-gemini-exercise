"""Tests for the P5 memory lifecycle: background consolidation, durable review, forget-me.

Uses real SQLite (store and checkpointer in a temp directory) and a real consolidator graph;
the assistant is a stand-in that only holds messages, and the edit model is scripted.
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda

from agentlab.data.sqlite_db_data import get_sqlite_checkpointer, get_sqlite_store
from agentlab.graphs.memory_consolidation_graph import make_memory_consolidation_graph
from agentlab.schemas.output.memory_consolidation_output_schema import (
    MemoryEdit,
    MemoryEdits,
)
from agentlab.utils.memory_session_util import (
    REVIEWS_KIND,
    THREADS_KIND,
    MemorySessions,
    forget_user,
    load_session,
    save_session,
)
from tests.fakes import RecordingGuard

PROFILE_KEY = "/user_profile.md"


class FakeAssistant:
    """Stands in for the assistant graph: only its checkpointed messages per thread are read."""

    def __init__(self) -> None:
        self.threads: dict[str, list[Any]] = {}

    def say(self, thread_id: str, *texts: str) -> None:
        for text in texts:
            self.threads.setdefault(thread_id, []).extend(
                [HumanMessage(content=text), AIMessage(content="ok")],
            )

    def get_state(self, config: dict[str, Any]) -> Any:
        messages = self.threads.get(config["configurable"]["thread_id"], [])
        return type("Snapshot", (), {"values": {"messages": list(messages)}})()


class RecordingModel:
    def __init__(self, *edits: MemoryEdit) -> None:
        self.edits = MemoryEdits(edits=list(edits))
        self.transcripts: list[str] = []

    def __call__(self, prompt: Any) -> MemoryEdits:
        text = prompt.to_string()
        self.transcripts.append(text.split("<conversation>\n", 1)[1])
        return self.edits


@pytest.fixture
def storage(tmp_path: Path) -> tuple[Any, Any]:
    return get_sqlite_store(tmp_path / "store.db"), get_sqlite_checkpointer(
        tmp_path / "checkpoints.db",
    )


def make_sessions(
    storage: tuple[Any, Any],
    assistant: FakeAssistant,
    model: RecordingModel,
    **kwargs: Any,
) -> Any:
    store, checkpointer = storage
    graph = make_memory_consolidation_graph(
        store,
        checkpointer=checkpointer,
        model=RunnableLambda(model),
        guard=RecordingGuard("allow"),
    )
    return MemorySessions(
        store,
        assistant,
        graph,
        long_thread_chars=kwargs.get("long_thread_chars", 10_000),
    )


def finish(sessions: MemorySessions) -> None:
    for future in list(sessions._running.values()):
        future.result()


def profile(store: Any) -> str:
    return store.get(("alice", "memories"), PROFILE_KEY).value["content"]


def put_profile(store: Any, content: str) -> None:
    store.put(
        ("alice", "memories"),
        PROFILE_KEY,
        {"content": content, "encoding": "utf-8"},
    )


def test_each_consolidation_covers_only_messages_after_the_last_one(
    storage: tuple[Any, Any],
) -> None:
    assistant, model = FakeAssistant(), RecordingModel()
    sessions = make_sessions(storage, assistant, model)

    assistant.say("t1", "I live in Tehran")
    sessions.start("alice", "t1")
    finish(sessions)
    assistant.say("t1", "I moved to Karaj")
    sessions.start("alice", "t1")
    finish(sessions)
    sessions.close()

    assert "Tehran" in model.transcripts[0]
    assert "Tehran" not in model.transcripts[1] and "Karaj" in model.transcripts[1]


def test_a_long_conversation_is_consolidated_before_it_ends(
    storage: tuple[Any, Any],
) -> None:
    assistant, model = FakeAssistant(), RecordingModel()
    sessions = make_sessions(storage, assistant, model, long_thread_chars=60)

    assistant.say("t1", "short")
    assert sessions.start_if_long("alice", "t1") is False
    assistant.say(
        "t1",
        "a much longer message that pushes the transcript past the limit",
    )
    assert sessions.start_if_long("alice", "t1") is True
    finish(sessions)
    sessions.close()

    assert len(model.transcripts) == 1


def test_a_review_survives_an_app_restart(
    storage: tuple[Any, Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    store, _ = storage
    put_profile(store, "- Lives in Tehran\n")
    assistant = FakeAssistant()
    model = RecordingModel(
        MemoryEdit(
            kind="replace",
            path="/memories/user_profile.md",
            old="- Lives in Tehran",
            new="- Lives in Karaj",
            reason="The user moved.",
        ),
    )
    first = make_sessions(storage, assistant, model)
    assistant.say("t1", "I moved to Karaj")
    first.start("alice", "t1")
    finish(first)
    first.close()  # the app exits with the approval still pending

    second = make_sessions(storage, assistant, model)
    second.resume("alice")
    with patch("builtins.input", side_effect=["y"]):
        second.review("alice")
    second.close()

    assert profile(store) == "- Lives in Karaj\n"
    assert (
        "Applied /memories/user_profile.md: - Lives in Tehran -> - Lives in Karaj."
        in capsys.readouterr().out
    )
    assert store.search(("alice", REVIEWS_KIND)) == []


def test_a_conversation_left_at_exit_is_consolidated_on_the_next_start(
    storage: tuple[Any, Any],
) -> None:
    assistant, model = FakeAssistant(), RecordingModel()
    first = make_sessions(storage, assistant, model)
    assistant.say("t1", "I play chess")
    first.queue("alice", "t1")
    first.close()
    assert model.transcripts == []

    second = make_sessions(storage, assistant, model)
    second.resume("alice")
    finish(second)
    second.close()

    assert "chess" in model.transcripts[0]


def test_another_users_session_never_sees_the_proposal(
    storage: tuple[Any, Any],
    capsys: Any,
) -> None:
    assistant = FakeAssistant()
    model = RecordingModel(
        MemoryEdit(
            kind="add",
            path="/memories/user_profile.md",
            new="- Plays chess",
            reason="The user said so.",
        ),
    )
    sessions = make_sessions(storage, assistant, model)
    assistant.say("t1", "I play chess")
    sessions.start("alice", "t1")
    finish(sessions)

    sessions.review("bob")
    assert "[Memory]" not in capsys.readouterr().out
    sessions.review("alice")
    sessions.close()

    assert (
        "Applied /memories/user_profile.md: + - Plays chess" in capsys.readouterr().out
    )


def test_forget_deletes_memory_bookkeeping_and_conversations(
    storage: tuple[Any, Any],
) -> None:
    store, checkpointer = storage
    put_profile(store, "- Lives in Tehran\n")
    store.put(
        ("bob", "memories"),
        PROFILE_KEY,
        {"content": "- Bob", "encoding": "utf-8"},
    )
    store.put(("alice", THREADS_KIND), "t1", {"consolidated": 0, "created_at": 0})
    checkpointer.put(
        {"configurable": {"thread_id": "t1", "checkpoint_ns": ""}},
        {
            "v": 1,
            "id": "1",
            "ts": "",
            "channel_values": {},
            "channel_versions": {},
            "versions_seen": {},
        },
        {},
        {},
    )

    deleted = forget_user(store, checkpointer, "alice")

    assert deleted == 1
    assert list(store.list_namespaces(prefix=("alice",))) == []
    assert checkpointer.get_tuple({"configurable": {"thread_id": "t1"}}) is None
    assert store.get(("bob", "memories"), PROFILE_KEY) is not None


def test_the_app_resumes_the_last_user_and_thread(storage: tuple[Any, Any]) -> None:
    store, _ = storage

    assert load_session(store) == ("default_user", "pa_session_001")
    save_session(store, "sara", "thread_abc")
    assert load_session(store) == ("sara", "thread_abc")
