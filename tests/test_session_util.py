"""Tests for CLI session resolution."""

from typing import Any

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from agentlab.utils.session_util import (
    ResolvedSession,
    format_session_list,
    resolve_session,
)


class RecordingFactory:
    """Agent factory double that records the checkpointer each call received."""

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def __call__(self, checkpointer: Any) -> dict[str, Any]:
        self.calls.append(checkpointer)
        return {"checkpointer": checkpointer}


def resolve(
    arg: str | None,
    factory: RecordingFactory,
    threads: list[str] | None = None,
) -> ResolvedSession:
    return resolve_session(
        arg,
        default_thread_id="sess_default",
        agent_factory=factory,
        app_name="testapp",
        get_threads_fn=lambda **_: list(threads or []),
        handle_cli_exit=False,
    )


def test_config_carries_the_thread_id() -> None:
    session = ResolvedSession(agent=None, thread_id="t1", mode_name="custom (t1)")
    assert session.config == {"configurable": {"thread_id": "t1"}}


@pytest.mark.parametrize("arg", [None, "", "default"])
def test_default_mode_uses_default_thread_and_durable_factory(arg: str | None) -> None:
    factory = RecordingFactory()
    session = resolve(arg, factory)

    assert (session.thread_id, session.mode_name, session.is_secret) == (
        "sess_default",
        "default",
        False,
    )
    assert factory.calls == [None]


def test_new_mode_generates_prefixed_thread() -> None:
    session = resolve("new", RecordingFactory())
    assert session.thread_id.startswith("testapp_") and len(session.thread_id) > len(
        "testapp_",
    )


def test_secret_mode_uses_in_memory_checkpointer() -> None:
    factory = RecordingFactory()
    session = resolve("secret", factory)

    assert session.is_secret and session.thread_id.startswith("secret_")
    assert isinstance(factory.calls[0], InMemorySaver)


def test_resume_picks_latest_thread_or_falls_back() -> None:
    assert (
        resolve("resume", RecordingFactory(), ["t_latest", "t_old"]).thread_id
        == "t_latest"
    )
    assert resolve("resume", RecordingFactory(), []).thread_id == "sess_default"


def test_step_mode_indexes_recent_threads() -> None:
    threads = ["t0", "t1", "t2"]
    assert resolve("step[0]", RecordingFactory(), threads).thread_id == "t0"
    assert resolve("step2", RecordingFactory(), threads).mode_name == "step[2] (t2)"


def test_step_mode_errors_do_not_build_an_agent() -> None:
    factory = RecordingFactory()
    with pytest.raises(IndexError):
        resolve("step[9]", factory, ["t0"])
    with pytest.raises(ValueError, match="No recorded sessions"):
        resolve("step[0]", factory, [])
    assert factory.calls == []


def test_custom_mode_uses_argument_as_thread_id() -> None:
    session = resolve("feature_x", RecordingFactory())
    assert (session.thread_id, session.mode_name) == ("feature_x", "custom (feature_x)")


def test_list_mode_prints_threads_without_building_an_agent(
    capsys: pytest.CaptureFixture[str],
) -> None:
    factory = RecordingFactory()
    session = resolve("list", factory, ["t0"])

    assert session.agent is None and factory.calls == []
    assert "step[0]: t0 (latest)" in capsys.readouterr().out


def test_format_session_list() -> None:
    banner = format_session_list(
        ["tid_1", "tid_2"],
        cli_command_hint="python test.py step[<index>]",
    )
    assert "step[0]: tid_1 (latest)" in banner
    assert "step[1]: tid_2" in banner
    assert "python test.py step[<index>]" in banner
    assert "No recorded sessions found" in format_session_list([])
