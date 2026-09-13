"""Unit tests for generic human-in-the-loop (HITL) execution utility."""

from unittest.mock import MagicMock, patch

from langgraph.types import Command

from agentlab.utils.run_with_hitl_util import (
    _format_prompt,
    _handle_interrupt_decisions,
    run_with_hitl,
)


class MockInterrupt:
    """Mock LangGraph interrupt object."""

    def __init__(self, action_requests: list[dict]):
        self.value = {"action_requests": action_requests}


def test_format_prompt_dynamic_and_custom():
    """Verify prompt formatting for default, template, static, and callable."""
    req_exec = {"name": "execute", "args": {"command": "python test.py"}}
    req_delete = {"name": "delete", "args": {"file_path": "old.py"}}

    # Default dynamic
    assert _format_prompt(None, req_exec) == "\nApprove execute action? [y/n]: "
    assert _format_prompt(None, req_delete) == "\nApprove delete action? [y/n]: "

    # Template with {name}
    assert (
        _format_prompt("Confirm {name}? [y/n]: ", req_delete)
        == "Confirm delete? [y/n]: "
    )

    # Static string
    assert _format_prompt("Approve? [y/n]: ", req_exec) == "Approve? [y/n]: "

    # Callable
    assert (
        _format_prompt(lambda r: f"Review tool {r['name']}: ", req_delete)
        == "Review tool delete: "
    )


def test_handle_interrupt_approval():
    """Verify approving an action produces approve decision."""
    interrupt = MockInterrupt([{"name": "execute", "args": {"command": "ls"}}])

    with patch("builtins.input", side_effect=["y"]):
        res = _handle_interrupt_decisions(interrupt)
        assert res == {"decisions": [{"type": "approve"}]}


def test_handle_interrupt_rejection_with_reason():
    """Verify rejecting an action captures optional feedback reason."""
    interrupt = MockInterrupt([{"name": "delete", "args": {"path": "important.db"}}])

    with patch(
        "builtins.input", side_effect=["n", "Database is critical, do not drop"]
    ):
        res = _handle_interrupt_decisions(interrupt)
        assert res == {
            "decisions": [
                {"type": "reject", "message": "Database is critical, do not drop"}
            ]
        }


def test_handle_interrupt_rejection_empty_reason():
    """Verify rejecting without feedback omits message key."""
    interrupt = MockInterrupt([{"name": "delete", "args": {"path": "tmp.txt"}}])

    with patch("builtins.input", side_effect=["no", ""]):
        res = _handle_interrupt_decisions(interrupt)
        assert res == {"decisions": [{"type": "reject"}]}


def test_run_with_hitl_happy_path_no_interrupt():
    """Verify run_with_hitl invokes agent directly when no interrupt occurs."""
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"messages": ["Task complete"]}

    result = run_with_hitl(
        mock_agent, "hello", config={"configurable": {"thread_id": "1"}}
    )
    assert result == {"messages": ["Task complete"]}
    mock_agent.invoke.assert_called_once_with(
        "hello", {"configurable": {"thread_id": "1"}}
    )


def test_run_with_hitl_multi_turn_interrupt_cycle():
    """Verify run_with_hitl prompts for approval and resumes via Command."""
    mock_agent = MagicMock()
    interrupt = MockInterrupt(
        [{"name": "execute", "args": {"command": "python script.py"}}]
    )

    # 1st invoke produces interrupt, 2nd invoke produces final result
    mock_agent.invoke.side_effect = [
        {"__interrupt__": [interrupt]},
        {"messages": ["Execution succeeded"]},
    ]

    with patch("builtins.input", side_effect=["y"]):
        result = run_with_hitl(
            mock_agent,
            {"messages": ["run"]},
            config={"configurable": {"thread_id": "test"}},
        )

    assert result == {"messages": ["Execution succeeded"]}
    assert mock_agent.invoke.call_count == 2
    second_call_arg = mock_agent.invoke.call_args_list[1][0][0]
    assert isinstance(second_call_arg, Command)
    assert second_call_arg.resume == {"decisions": [{"type": "approve"}]}
