"""Unit tests for universal session resolution & thread management utility."""

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from utils.session_util import ResolvedSession, format_session_list, resolve_session


class DummyAgent:
    """Mock agent object for testing."""

    def __init__(self, name: str = "dummy", checkpointer=None):
        self.name = name
        self.checkpointer = checkpointer


def test_resolved_session_config_property():
    """Verify ResolvedSession provides a valid LangGraph config dict."""
    session = ResolvedSession(
        agent=DummyAgent(),
        thread_id="test_thread_123",
        mode_name="custom (test_thread_123)",
        is_secret=False,
    )
    assert session.thread_id == "test_thread_123"
    assert session.config == {"configurable": {"thread_id": "test_thread_123"}}
    assert not session.is_secret


def test_resolve_session_default_mode():
    """Verify default mode when raw_arg is None or 'default'."""
    agent = DummyAgent("default_agent")
    s1 = resolve_session(None, default_thread_id="sess_default", default_agent=agent)
    assert s1.thread_id == "sess_default"
    assert s1.mode_name == "default"
    assert not s1.is_secret
    assert s1.agent == agent

    s2 = resolve_session("default", default_thread_id="sess_default", default_agent=agent)
    assert s2.thread_id == "sess_default"
    assert s2.mode_name == "default"


def test_resolve_session_new_mode():
    """Verify new mode generates a unique prefixed thread ID."""
    agent = DummyAgent()
    s = resolve_session("new", default_thread_id="sess_default", default_agent=agent, app_name="testapp")
    assert s.thread_id.startswith("testapp_")
    assert len(s.thread_id) > len("testapp_")
    assert s.mode_name == "new"
    assert not s.is_secret


def test_resolve_session_secret_mode():
    """Verify secret mode creates ephemeral in-memory session."""
    def factory(saver):
        return DummyAgent(checkpointer=saver)

    s = resolve_session(
        "secret",
        default_thread_id="sess_default",
        agent_factory=factory,
    )
    assert s.thread_id.startswith("secret_")
    assert s.is_secret is True
    assert "secret" in s.mode_name
    assert isinstance(s.agent.checkpointer, InMemorySaver)


def test_resolve_session_resume_mode():
    """Verify resume picks the latest recorded thread or falls back gracefully."""
    mock_threads = ["thread_3_latest", "thread_2", "thread_1"]
    s = resolve_session(
        "resume",
        default_thread_id="sess_default",
        default_agent=DummyAgent(),
        get_threads_fn=lambda **kwargs: mock_threads,
    )
    assert s.thread_id == "thread_3_latest"
    assert "resume" in s.mode_name

    # Empty DB fallback
    s_empty = resolve_session(
        "resume",
        default_thread_id="sess_default",
        default_agent=DummyAgent(),
        get_threads_fn=lambda **kwargs: [],
    )
    assert s_empty.thread_id == "sess_default"
    assert "no prior sessions" in s_empty.mode_name


def test_resolve_session_step_mode():
    """Verify step[N] indexes correctly and handles bounds."""
    mock_threads = ["t0_latest", "t1", "t2", "t3"]

    s0 = resolve_session(
        "step[0]",
        default_thread_id="sess_default",
        default_agent=DummyAgent(),
        get_threads_fn=lambda **kwargs: mock_threads,
        handle_cli_exit=False,
    )
    assert s0.thread_id == "t0_latest"
    assert s0.mode_name == "step[0] (t0_latest)"

    s2 = resolve_session(
        "step2",
        default_thread_id="sess_default",
        default_agent=DummyAgent(),
        get_threads_fn=lambda **kwargs: mock_threads,
        handle_cli_exit=False,
    )
    assert s2.thread_id == "t2"
    assert s2.mode_name == "step[2] (t2)"

    # Out of bounds
    with pytest.raises(IndexError):
        resolve_session(
            "step[10]",
            default_thread_id="sess_default",
            default_agent=DummyAgent(),
            get_threads_fn=lambda **kwargs: mock_threads,
            handle_cli_exit=False,
        )

    # Empty DB
    with pytest.raises(ValueError, match="No recorded sessions"):
        resolve_session(
            "step[0]",
            default_thread_id="sess_default",
            default_agent=DummyAgent(),
            get_threads_fn=lambda **kwargs: [],
            handle_cli_exit=False,
        )


def test_resolve_session_custom_mode():
    """Verify custom user-provided thread ID."""
    s = resolve_session(
        "my_custom_feature_session",
        default_thread_id="sess_default",
        default_agent=DummyAgent(),
    )
    assert s.thread_id == "my_custom_feature_session"
    assert s.mode_name == "custom (my_custom_feature_session)"
    assert not s.is_secret


def test_format_session_list():
    """Verify banner formatting for recorded threads."""
    banner = format_session_list(["tid_1", "tid_2"], cli_command_hint="python test.py step[<index>]")
    assert "Recorded Sessions" in banner
    assert "step[0]: tid_1 (latest)" in banner
    assert "step[1]: tid_2" in banner
    assert "python test.py step[<index>]" in banner

    empty_banner = format_session_list([])
    assert "No recorded sessions found" in empty_banner
