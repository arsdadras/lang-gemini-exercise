"""Node functions for the P5 memory consolidator: ``consolidate`` proposes, ``apply`` stores."""

from collections.abc import Callable, Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime

from agentlab.configs.personal_assistant_config import (
    CONSOLIDATOR_PROVIDER,
    CONSOLIDATOR_TIER,
    MEMORIES_ROUTE_PREFIX,
)
from agentlab.middlewares.memory_approval_middleware import GatedMemoryBackend
from agentlab.models import llm_model
from agentlab.prompts.nodes.memory_consolidation_prompt import MEMORY_CONSOLIDATION_PROMPT
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.memory_consolidation_output_schema import MemoryProposal
from agentlab.schemas.state.memory_consilidation_state import MemoryConsolidationState
from agentlab.utils.get_text_util import get_text
from agentlab.utils.memory_backend_util import user_memory_namespace

NO_MEMORY = "(no memory files yet)"


def format_transcript(messages: Sequence[BaseMessage]) -> str:
    """The user's and the assistant's words only: tool calls and results are left out."""
    lines = []
    for message in messages:
        text = get_text(message).strip()
        if not text:
            continue
        if isinstance(message, HumanMessage):
            lines.append(f"User: {text}")
        elif isinstance(message, AIMessage):
            lines.append(f"Assistant: {text}")
    return "\n\n".join(lines)


def _stored_text(value: dict[str, Any]) -> str:
    content = value.get("content", "")
    return "\n".join(content) if isinstance(content, list) else content


def _read_memory(runtime: Runtime[UserContext]) -> dict[str, str]:
    """Every memory file of the current user, keyed by full path."""
    items = runtime.store.search(user_memory_namespace(runtime), limit=1000)
    return {MEMORIES_ROUTE_PREFIX.rstrip("/") + item.key: _stored_text(item.value) for item in items}


def make_consolidate_node(
    model: Runnable | None = None,
) -> Callable[[MemoryConsolidationState, Runtime[UserContext]], dict]:
    """Build the node that compares the conversation with memory and proposes changes."""
    chain = MEMORY_CONSOLIDATION_PROMPT | (
        model
        if model is not None
        else llm_model.chain(CONSOLIDATOR_TIER, structured=MemoryProposal, provider=CONSOLIDATOR_PROVIDER)
    )

    def consolidate(state: MemoryConsolidationState, runtime: Runtime[UserContext]) -> dict:
        files = _read_memory(runtime)
        memory = "\n\n".join(f'<file path="{path}">\n{text}\n</file>' for path, text in files.items())
        proposal = chain.invoke({"memory": memory or NO_MEMORY, "transcript": state["transcript"]})
        return {"proposal": proposal}

    return consolidate


def _memory_key(path: str) -> str | None:
    """The storage key for a proposed path, or ``None`` if it isn't a memory file."""
    if not path.startswith(MEMORIES_ROUTE_PREFIX) or not path.endswith(".md") or ".." in path:
        return None
    return path[len(MEMORIES_ROUTE_PREFIX) - 1 :]


def make_apply_node(
    backend: GatedMemoryBackend,
) -> Callable[[MemoryConsolidationState, Runtime[UserContext]], dict]:
    """Build the node that stores the proposal through the memory gate, one file at a time."""

    def apply(state: MemoryConsolidationState, runtime: Runtime[UserContext]) -> dict:
        namespace = user_memory_namespace(runtime)
        outcomes = []
        for update in state["proposal"].updates:
            key = _memory_key(update.path)
            if key is None:
                outcomes.append(f"Skipped {update.path}: not a memory file.")
                continue
            # A resume runs this node again from the top: a file stored before the
            # pause already holds its new content and must not be judged again.
            stored = runtime.store.get(namespace, key)
            if stored is not None and _stored_text(stored.value) == update.content:
                outcomes.append(f"Saved {update.path}.")
                continue
            result = backend.write(key, update.content)
            outcomes.append(f"Not saved {update.path}: {result.error}" if result.error else f"Saved {update.path}.")
        return {"outcomes": outcomes}

    return apply



"""Graph assembly for the P5 memory consolidator: consolidate -> apply.

The assistant only reads memory; this graph is its single writer. It runs after a conversation
ends. ``consolidate`` proposes changes from the transcript; ``apply`` stores them through the
same gate as every other memory change (ADR-0010), so a change that needs approval pauses the
graph until the user is back to review it.
"""

from langchain_core.runnables import Runnable
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.middlewares.memory_approval_middleware import GatedMemoryBackend, MemoryGate
from agentlab.middlewares.security_guard_middleware import SecurityGuard, make_security_guard
from agentlab.nodes.memory_consolidation_node import make_apply_node, make_consolidate_node
from agentlab.prompts.middlewares_prompt import MEMORY_WRITE_POLICY
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.memory_consolidation_output_schema import MemoryFileUpdate, MemoryProposal
from agentlab.schemas.state.memory_consolidation_state import MemoryConsolidationState
from agentlab.utils.memory_backend_util import user_memory_namespace

# A paused run keeps its proposal in the checkpoint until the user reviews it, and LangGraph
# only restores the classes a checkpointer's serializer lists (others warn today, fail later).
CONSOLIDATION_STATE_TYPES = [(model.__module__, model.__name__) for model in (MemoryProposal, MemoryFileUpdate)]


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
        checkpointer: Keeps a paused run until the user reviews it; defaults to in-memory. A
            custom one must allow ``CONSOLIDATION_STATE_TYPES`` in its serializer.
        model: Structured-output model for the proposal; defaults to ``CONSOLIDATOR_PROVIDER``.
        guard: Security guard for the memory gate; defaults to the memory write policy.
    """
    gate = MemoryGate(guard if guard is not None else make_security_guard(MEMORY_WRITE_POLICY))
    backend = GatedMemoryBackend(gate, namespace=user_memory_namespace)

    graph = StateGraph(MemoryConsolidationState, context_schema=UserContext)
    graph.add_node("consolidate", make_consolidate_node(model))
    graph.add_node("apply", make_apply_node(backend))
    graph.add_edge(START, "consolidate")
    graph.add_edge("consolidate", "apply")
    graph.add_edge("apply", END)
    if checkpointer is None:
        checkpointer = InMemorySaver(serde=JsonPlusSerializer(allowed_msgpack_modules=CONSOLIDATION_STATE_TYPES))
    return graph.compile(checkpointer=checkpointer, store=store)