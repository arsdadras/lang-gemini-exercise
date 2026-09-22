"""Graph assembly for the P5 memory consolidator: consolidate -> apply_next_edit (loop).

The assistant only reads memory; this graph is its single writer. It runs after a conversation
ends. ``consolidate`` proposes line-level edits; ``apply_next_edit`` applies them one per run,
through the same gate as every other memory change (ADR-0010). An edit that needs approval
pauses the graph until the user is back to review it.
"""

from typing import Literal

from langchain_core.runnables import Runnable
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.middlewares.memory_approval_middleware import (
    GatedMemoryBackend,
    MemoryGate,
)
from agentlab.middlewares.security_guard_middleware import (
    SecurityGuard,
    make_security_guard,
)
from agentlab.nodes.memory_consolidation_node import (
    make_apply_next_edit_node,
    make_consolidate_node,
)
from agentlab.prompts.middlewares_prompt import MEMORY_WRITE_POLICY
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.state.memory_consolidation_state import MemoryConsolidationState
from agentlab.utils.memory_backend_util import user_memory_namespace

# Each edit is one step of the loop; LangGraph's default limit (25 steps) would cap a proposal
# at about 23 edits.
CONSOLIDATION_RECURSION_LIMIT = 200


def route_next_edit(state: MemoryConsolidationState) -> Literal["apply_next_edit", "__end__"]:
    """Loop while edits remain."""
    return "apply_next_edit" if state.get("cursor", 0) < len(state.get("edits", [])) else END


def make_memory_consolidation_graph(
    store: BaseStore,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    model: Runnable | None = None,
    guard: SecurityGuard | None = None,
) -> CompiledStateGraph:
    """Compile the consolidator. Invoke it with ``context=UserContext(user_id=...)``.

    Args:
        store: The assistant's memory store.
        checkpointer: Keeps a paused run until the user reviews it; defaults to in-memory.
        model: Structured-output model for the edits; defaults to ``CONSOLIDATOR_PROVIDER``.
        guard: Security guard for the memory gate; defaults to the memory write policy.
    """
    gate = MemoryGate(guard if guard is not None else make_security_guard(MEMORY_WRITE_POLICY))
    backend = GatedMemoryBackend(gate, namespace=user_memory_namespace)

    graph = StateGraph(MemoryConsolidationState, context_schema=UserContext)
    graph.add_node("consolidate", make_consolidate_node(model))
    graph.add_node("apply_next_edit", make_apply_next_edit_node(backend))
    graph.add_edge(START, "consolidate")
    graph.add_conditional_edges("consolidate", route_next_edit)
    graph.add_conditional_edges("apply_next_edit", route_next_edit)
    compiled = graph.compile(checkpointer=checkpointer if checkpointer is not None else InMemorySaver(), store=store)
    return compiled.with_config(recursion_limit=CONSOLIDATION_RECURSION_LIMIT)
