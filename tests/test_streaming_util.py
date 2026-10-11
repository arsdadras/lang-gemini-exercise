"""Unit tests for streaming observability utility."""

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agentlab.utils.streaming_util import stream_agent_with_observability


class MockStreamingAgent:
    """Mock agent returning predefined stream chunks."""

    def __init__(self, chunks: list[Any]) -> None:
        self.chunks = chunks

    def stream(self, *args, **kwargs):
        yield from self.chunks


def test_stream_agent_with_observability_basic():
    """Verify basic message streaming and last_message extraction."""
    ai_msg = AIMessage(content="Hello world from assistant")
    mock_chunks = [
        ((), {"model": {"messages": [ai_msg]}}),
    ]
    agent = MockStreamingAgent(mock_chunks)
    res = stream_agent_with_observability(
        agent,
        {"messages": [HumanMessage(content="Hi")]},
    )
    assert res["last_message"] == ai_msg
    assert len(res["messages"]) == 1


def test_stream_agent_with_observability_todos():
    """Verify todos planning channel updates and callback invocation."""
    events = []

    def on_event(etype: str, payload: Any):
        events.append((etype, payload))

    mock_todos = [
        {"content": "Step 1", "status": "completed"},
        {"content": "Step 2", "status": "in_progress"},
    ]
    mock_chunks = [
        ((), {"tools": {"todos": mock_todos}}),
        ((), {"model": {"messages": [AIMessage(content="Done")]}}),
    ]
    agent = MockStreamingAgent(mock_chunks)
    res = stream_agent_with_observability(
        agent,
        {"messages": [HumanMessage(content="Do tasks")]},
        callback=on_event,
    )
    assert len(events) == 1
    assert events[0][0] == "todos"
    assert events[0][1] == mock_todos
    assert res["last_message"].content == "Done"


def test_stream_agent_with_observability_delegation():
    """Verify subagent task delegation and tool result tracking."""
    events = []

    def on_event(etype: str, payload: Any):
        events.append((etype, payload))

    delegate_msg = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "task",
                "args": {"subagent": "researcher", "description": "Search web"},
                "id": "call_01",
            },
        ],
    )
    tool_res = ToolMessage(
        content="Search results found",
        name="task",
        tool_call_id="call_01",
    )
    final_msg = AIMessage(content="Synthesis report")

    mock_chunks = [
        ((), {"model": {"messages": [delegate_msg]}}),
        ((), {"tools": {"messages": [tool_res]}}),
        ((), {"model": {"messages": [final_msg]}}),
    ]
    agent = MockStreamingAgent(mock_chunks)
    res = stream_agent_with_observability(
        agent,
        {"messages": [HumanMessage(content="Research")]},
        callback=on_event,
    )

    event_types = [e[0] for e in events]
    assert "delegation" in event_types
    assert "tool_result" in event_types
    assert res["last_message"] == final_msg
