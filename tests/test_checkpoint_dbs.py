"""One checkpoint database per app, and a worker prompt only for delegated runs."""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from agentlab.agents import coding_coordinator_agent, interpreter_agent
from agentlab.configs import paths_config
from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_recent_threads, get_sqlite_checkpointer
from agentlab.prompts import (
    build_interpreter_agent_prompt,
    build_interpreter_worker_prompt,
)
from agentlab.utils.session_util import resolve_session


@pytest.fixture
def state_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(paths_config, "STATE_DIR", tmp_path)
    return tmp_path


def write_thread(app: str, thread_id: str) -> None:
    """Checkpoint one real thread into the app's own database."""
    graph = StateGraph(MessagesState)
    graph.add_node("noop", lambda state: {})
    graph.add_edge(START, "noop")
    graph.add_edge("noop", END)
    compiled = graph.compile(
        checkpointer=get_sqlite_checkpointer(checkpoint_db_path(app))
    )
    compiled.invoke({"messages": []}, {"configurable": {"thread_id": thread_id}})


def test_each_app_has_its_own_database(state_dir: Path) -> None:
    assert checkpoint_db_path("rag") == state_dir / "rag_checkpoints.db"
    assert checkpoint_db_path("rag") != checkpoint_db_path("research")


def test_an_app_lists_and_resumes_only_its_own_threads(state_dir: Path) -> None:
    write_thread("alpha", "alpha-thread")
    write_thread("beta", "beta-thread")

    assert get_recent_threads(checkpoint_db_path("alpha")) == ["alpha-thread"]
    for app, thread in (("alpha", "alpha-thread"), ("beta", "beta-thread")):
        session = resolve_session(
            "resume",
            default_thread_id="default",
            agent_factory=lambda _checkpointer: None,
            app_name=app,
            handle_cli_exit=False,
        )
        assert session.thread_id == thread


def test_no_database_means_no_threads(state_dir: Path) -> None:
    assert get_recent_threads(checkpoint_db_path("never_run")) == []


def test_the_interpreter_agent_picks_its_prompt_by_role() -> None:
    prompts = []
    for worker in (False, True):
        with patch.object(interpreter_agent, "create_deep_agent") as create:
            interpreter_agent.make_interpreter_agent(
                InMemorySaver(),
                backend=object(),
                worker=worker,  # type: ignore[arg-type]
            )
        prompts.append(create.call_args.kwargs["system_prompt"])

    assert prompts == [
        build_interpreter_agent_prompt(),
        build_interpreter_worker_prompt(),
    ]


def test_the_coordinator_delegates_to_a_worker_interpreter_on_the_delegations_database(
    state_dir: Path,
) -> None:
    seen: dict[str, Any] = {}

    def fake_interpreter(checkpointer: Any, **kwargs: Any) -> str:
        seen.update(kwargs, checkpointer=checkpointer)
        return "interpreter"

    with (
        patch.object(
            coding_coordinator_agent, "make_interpreter_agent", fake_interpreter
        ),
        patch.object(
            coding_coordinator_agent, "make_interpreter_subagent", lambda agent: agent
        ),
        patch.object(
            coding_coordinator_agent, "make_code_review_subagent", lambda: "review"
        ),
        patch.object(
            coding_coordinator_agent, "make_researcher_subagent", lambda: "research"
        ),
        patch.object(coding_coordinator_agent, "llm_model"),
        patch.object(coding_coordinator_agent, "create_deep_agent"),
        patch.object(coding_coordinator_agent, "make_model_fallback"),
    ):
        coding_coordinator_agent.make_coding_coordinator_agent(InMemorySaver())

    assert seen["worker"] is True
    assert seen["interrupt_tools"] == ()
    assert (state_dir / f"{DELEGATIONS_APP}_checkpoints.db").exists()
