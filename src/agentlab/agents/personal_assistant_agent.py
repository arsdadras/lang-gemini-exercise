"""P5 memory-rich personal assistant: per-user long-term memory, procedural skills, web search."""

from deepagents import create_deep_agent
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
from agentlab.middlewares.memory_approval_middleware import (
    GatedMemoryBackend,
    MemoryGate,
)
from agentlab.middlewares.security_guard_middleware import (
    SecurityGuard,
    make_security_guard,
)
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_personal_assistant_prompt
from agentlab.prompts.middlewares_prompt import MEMORY_WRITE_POLICY
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.tools.web_search_tool import make_web_search_tool
from agentlab.utils.memory_backend_util import (
    make_memory_composite_backend,
    user_memory_namespace,
)

# Skills are shared by every user: the assistant may read them, never change them.
PERSONAL_ASSISTANT_PERMISSIONS = [
    FilesystemPermission(operations=["write"], paths=[f"{SKILLS_ROUTE_PREFIX}**"], mode="deny"),
]


def make_personal_assistant_agent(
    store: BaseStore,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    guard: SecurityGuard | None = None,
    tier: str = DEFAULT_ASSISTANT_TIER,
    provider: str | None = DEFAULT_ASSISTANT_PROVIDER,
) -> CompiledStateGraph:
    """Build the assistant. Invoke it with ``context=UserContext(user_id=...)``.

    Args:
        store: Long-term memory store. The caller owns it so it can inspect or
            persist memories outside the agent.
        checkpointer: Thread state persistence; defaults to in-memory.
        guard: Security guard for memory writes; defaults to the memory write policy on
            the ``low`` tier.
        tier: Capability tier from the model catalog.
        provider: Pinned provider inside ``tier``; other providers become fallbacks.

    Every memory change passes one gate in the memory storage: ordinary additions run
    freely; overwriting, destructive edits, deletions, and sensitive content wait for
    approval; secrets and credentials are refused. Skills are read-only.
    """
    gate = MemoryGate(guard if guard is not None else make_security_guard(MEMORY_WRITE_POLICY))
    return create_deep_agent(
        model=llm_model.get(tier, provider),
        system_prompt=build_personal_assistant_prompt(),
        tools=[make_web_search_tool()],
        backend=make_memory_composite_backend(memories=GatedMemoryBackend(gate, namespace=user_memory_namespace)),
        permissions=PERSONAL_ASSISTANT_PERMISSIONS,
        memory=[DEFAULT_USER_PROFILE_PATH],
        skills=[SKILLS_ROUTE_PREFIX],
        checkpointer=checkpointer if checkpointer is not None else InMemorySaver(),
        store=store,
        context_schema=UserContext,
        middleware=[make_model_fallback(tier, primary=provider)],
    )
