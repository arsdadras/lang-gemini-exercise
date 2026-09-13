"""Time travel & State History utilities for LangGraph checkpoints."""

from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph


def inspect_state_history(
    graph: CompiledStateGraph, thread_id: str
) -> list[dict[str, Any]]:
    """Inspect and return the chronological history of checkpoints for a
    given thread."""

    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    history = []
    for snapshot in graph.get_state_history(config=config):
        chk_id = snapshot.config.get("configurable", {}).get("checkpoint_id", "")
        step = snapshot.metadata.get("step", 0) if snapshot.metadata else 0
        node = (
            snapshot.metadata.get("source", "unknown")
            if snapshot.metadata
            else "unknown"
        )
        next_nodes = list(snapshot.next) if snapshot.next else []

        history.append(
            {
                "checkpoint_id": chk_id,
                "step": step,
                "node": node,
                "next_nodes": next_nodes,
                "created_at": getattr(snapshot, "created_at", None),
                "state_keys": list(snapshot.values.keys()),
            }
        )

    return list(reversed(history))


def fork_from_checkpoint(
    graph: CompiledStateGraph,
    thread_id: str,
    checkpoint_id: str,
    input_or_command: Any = None,
) -> dict[str, Any]:
    """Replay or fork graph execution starting from an exact historical checkpoint."""

    fork_config: RunnableConfig = {
        "configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}
    }
    return graph.invoke(input=input_or_command, config=fork_config)
