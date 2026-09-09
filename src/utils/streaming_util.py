"""Universal streaming observability utility for DeepAgents and LangGraph agents.

Streams node updates, subagent handoffs, and tool executions in real-time,
providing rich CLI feedback rather than blocking silently.
"""

from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage

from utils.get_text_util import get_text


def stream_agent_with_observability(
    agent: Any,
    input_data: dict[str, Any],
    config: dict[str, Any] | None = None,
    *,
    show_subgraphs: bool = True,
    callback: Callable[[str, Any], None] | None = None,
) -> dict[str, Any]:
    """Streams agent execution updates with real-time CLI observability.

    Args:
        agent: Compiled DeepAgent or StateGraph runnable.
        input_data: Input dictionary passed to stream (e.g. {"messages": [...]}).
        config: Optional LangGraph configuration dict with thread_id.
        show_subgraphs: Whether to stream subagent updates recursively.
        callback: Optional custom notification callback (event_type, payload).

    Returns:
        Dictionary containing `messages` list and `last_message`.
    """
    last_ai_message: AIMessage | None = None
    all_messages: list[Any] = []

    for item in agent.stream(
        input_data,
        config=config,
        stream_mode="updates",
        subgraphs=show_subgraphs,
    ):
        ns, updates = item if isinstance(item, tuple) and len(item) == 2 else ((), item)
        if not isinstance(updates, dict):
            continue

        for node_update in updates.values():
            if not isinstance(node_update, dict):
                continue

            # 1. Observability for Todos / Planning (TodoListMiddleware)
            todos = node_update.get("todos")
            if todos and isinstance(todos, list):
                print("\n[Observability] Todo List Updated:")
                for t in todos:
                    status = t.get("status", "pending")
                    icon = (
                        "[x]"
                        if status == "completed"
                        else ("[>]" if status == "in_progress" else "[ ]")
                    )
                    print(f"  {icon} {t.get('content')}")
                if callback:
                    callback("todos", todos)

            # 2. Observability for Messages & Tool Calls
            msgs = node_update.get("messages", [])
            for m in msgs:
                all_messages.append(m)
                if isinstance(m, AIMessage):
                    content = get_text(m)
                    if content.strip() and not getattr(m, "tool_calls", None):
                        last_ai_message = m

                    for tc in getattr(m, "tool_calls", []):
                        tname = tc.get("name", "")
                        targs = tc.get("args", {})
                        if tname == "task":
                            sub = (
                                targs.get("subagent") or targs.get("name") or "subagent"
                            )
                            desc = (
                                targs.get("description")
                                or targs.get("sub_question")
                                or ""
                            )
                            print(
                                f"\n[Coordinator -> Delegating to {sub}]: {str(desc)[:95]}"
                            )
                            if callback:
                                callback("delegation", {"subagent": sub, "desc": desc})
                        elif tname == "write_todos":
                            pass  # Handled by todos channel check above
                        else:
                            prefix = f"[{ns[0]}] " if ns else ""
                            print(
                                f"\n{prefix}[Tool Call -> {tname}]: {str(targs)[:95]}"
                            )
                            if callback:
                                callback("tool_call", {"name": tname, "args": targs})

                elif isinstance(m, ToolMessage):
                    if m.name != "write_todos":
                        content = str(m.content).strip().replace("\n", " ")
                        print(f"  [Tool Result <- {m.name}]: {content[:95]}...")
                        if callback:
                            callback(
                                "tool_result", {"name": m.name, "content": content}
                            )

    return {"messages": all_messages, "last_message": last_ai_message}
