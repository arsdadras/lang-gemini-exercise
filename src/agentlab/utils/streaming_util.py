"""Streaming CLI observability for DeepAgents and LangGraph agents.

Prints planning updates, subagent delegations, tool calls, and tool results as
they happen instead of blocking silently until the run ends.
"""

from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage

from agentlab.utils.get_text_util import get_text

_PREVIEW_CHARS = 95


def _print_todos(todos: list[dict[str, Any]]) -> None:
    print("\n[Observability] Todo List Updated:")
    for todo in todos:
        status = todo.get("status", "pending")
        icon = {"completed": "[x]", "in_progress": "[>]"}.get(status, "[ ]")
        print(f"  {icon} {todo.get('content')}")


def stream_agent_with_observability(
    agent: Any,
    input_data: dict[str, Any],
    config: dict[str, Any] | None = None,
    *,
    context: Any | None = None,
    show_subgraphs: bool = True,
    callback: Callable[[str, Any], None] | None = None,
) -> dict[str, Any]:
    """Stream an agent run, printing progress, and return what it produced.

    Args:
        agent: Compiled DeepAgent or StateGraph.
        input_data: Graph input, e.g. ``{"messages": [...]}``.
        config: LangGraph config (usually carries ``thread_id``).
        context: Runtime context for agents built with a ``context_schema``.
        show_subgraphs: Also stream updates from subagents and subgraphs.
        callback: Optional ``(event_type, payload)`` hook for each printed event.

    Returns:
        ``{"messages": [...], "last_message": AIMessage | None}`` where
        ``last_message`` is the last non-empty AI answer without tool calls.
    """
    last_ai_message: AIMessage | None = None
    all_messages: list[Any] = []

    for item in agent.stream(
        input_data,
        config=config,
        context=context,
        stream_mode="updates",
        subgraphs=show_subgraphs,
    ):
        namespace, updates = item if isinstance(item, tuple) and len(item) == 2 else ((), item)
        if not isinstance(updates, dict):
            continue

        for node_update in updates.values():
            if not isinstance(node_update, dict):
                continue

            todos = node_update.get("todos")
            if todos and isinstance(todos, list):
                _print_todos(todos)
                if callback:
                    callback("todos", todos)

            for message in node_update.get("messages", []):
                all_messages.append(message)
                if isinstance(message, AIMessage):
                    if get_text(message).strip() and not message.tool_calls:
                        last_ai_message = message
                    for tool_call in message.tool_calls:
                        name = tool_call.get("name", "")
                        args = tool_call.get("args", {})
                        if name == "task":
                            subagent = args.get("subagent_type") or args.get("subagent") or "subagent"
                            description = args.get("description", "")
                            print(
                                f"\n[Coordinator -> Delegating to {subagent}]: "
                                f"{str(description)[:_PREVIEW_CHARS]}"
                            )
                            if callback:
                                callback("delegation", {"subagent": subagent, "desc": description})
                        elif name != "write_todos":
                            prefix = f"[{namespace[0]}] " if namespace else ""
                            print(f"\n{prefix}[Tool Call -> {name}]: {str(args)[:_PREVIEW_CHARS]}")
                            if callback:
                                callback("tool_call", {"name": name, "args": args})
                elif isinstance(message, ToolMessage) and message.name != "write_todos":
                    content = get_text(message).strip().replace("\n", " ")
                    print(f"  [Tool Result <- {message.name}]: {content[:_PREVIEW_CHARS]}...")
                    if callback:
                        callback("tool_result", {"name": message.name, "content": content})

    return {"messages": all_messages, "last_message": last_ai_message}
