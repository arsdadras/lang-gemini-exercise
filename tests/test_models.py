"""Tests for model imports and state schemas."""

from state import AgentContext, AgentSetup


def test_agent_setup_defaults() -> None:
    setup = AgentSetup()
    assert setup.tools == []
    assert setup.namespace == ("", "", {})


def test_agent_context_defaults() -> None:
    ctx = AgentContext()
    assert ctx.user_id == ""
    assert ctx.workspace_id == ""
    assert ctx.db is None


def test_agent_context_custom() -> None:
    ctx = AgentContext(user_id="u1", workspace_id="w1")
    assert ctx.user_id == "u1"
    assert ctx.workspace_id == "w1"
