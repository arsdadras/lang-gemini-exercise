"""P5 memory-rich personal assistant: per-user long-term memory, procedural skills, web search."""

from deepagents import create_deep_agent
from deepagents.backends import BackendProtocol
from deepagents.middleware.filesystem import FilesystemPermission
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from agentlab.configs.personal_assistant_config import (
    DEFAULT_ASSISTANT_PROVIDER,
    DEFAULT_ASSISTANT_TIER,
    DEFAULT_USER_PROFILE_PATH,
    SKILLS_ROUTE_PREFIX,
)
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.middlewares.memory_approval_middleware import make_memory_interrupt_on
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_personal_assistant_prompt
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.tools.web_search_tool import make_web_search_tool
from agentlab.utils.memory_backend_util import make_memory_composite_backend

# Skills are shared by every user: the assistant may read them, never change them.
PERSONAL_ASSISTANT_PERMISSIONS = [
    FilesystemPermission(operations=["write"], paths=[f"{SKILLS_ROUTE_PREFIX}**"], mode="deny"),
]


def make_personal_assistant_agent(
    store: BaseStore,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    backend: BackendProtocol | None = None,
    tier: str = DEFAULT_ASSISTANT_TIER,
    provider: str | None = DEFAULT_ASSISTANT_PROVIDER,
) -> CompiledStateGraph:
    """Build the assistant. Invoke it with ``context=UserContext(user_id=...)``.

    Args:
        store: Long-term memory store. The caller owns it so it can inspect or
            persist memories outside the agent.
        checkpointer: Thread state persistence; defaults to in-memory.
        backend: Virtual filesystem routing; defaults to ``/memories/`` in ``store``
            (namespaced per user) and ``/skills/`` over the packaged skill files.
        tier: Capability tier from the model catalog.
        provider: Pinned provider inside ``tier``; other providers become fallbacks.

    Memory writes that add a fact run freely; overwriting, destructively editing,
    or deleting stored memory waits for human approval. Skills are read-only.
    """
    backend = backend if backend is not None else make_memory_composite_backend()
    return create_deep_agent(
        model=llm_model.get(tier, provider),
        system_prompt=build_personal_assistant_prompt(),
        tools=[make_web_search_tool()],
        backend=backend,
        permissions=PERSONAL_ASSISTANT_PERMISSIONS,
        interrupt_on=make_memory_interrupt_on(backend),
        memory=[DEFAULT_USER_PROFILE_PATH],
        skills=[SKILLS_ROUTE_PREFIX],
        checkpointer=checkpointer if checkpointer is not None else InMemorySaver(),
        store=store,
        context_schema=UserContext,
        middleware=[make_model_fallback(tier, primary=provider)],
    )
