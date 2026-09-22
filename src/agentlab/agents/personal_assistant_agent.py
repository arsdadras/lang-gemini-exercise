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
    MEMORIES_ROUTE_PREFIX,
    PUBLISHED_SKILLS_ROUTE_PREFIX,
    SKILLS_ROUTE_PREFIX,
)
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.middlewares.finglish_output_middleware import make_finglish_output_guard
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_personal_assistant_prompt
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.tools.web_search_tool import make_web_search_tool
from agentlab.utils.memory_backend_util import make_memory_composite_backend

# The assistant reads memory and skills but changes neither. Memory has one writer, the
# consolidator that runs after each conversation; skills are shared by every user, and only the
# skill designer publishes new ones.
PERSONAL_ASSISTANT_PERMISSIONS = [
    FilesystemPermission(operations=["write"], paths=[f"{MEMORIES_ROUTE_PREFIX}**", f"{SKILLS_ROUTE_PREFIX}**", f"{PUBLISHED_SKILLS_ROUTE_PREFIX}**"], mode="deny"),
]


def make_personal_assistant_agent(
    store: BaseStore,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    tier: str = DEFAULT_ASSISTANT_TIER,
    provider: str | None = DEFAULT_ASSISTANT_PROVIDER,
) -> CompiledStateGraph:
    """Build the assistant. Invoke it with ``context=UserContext(user_id=...)``.

    Args:
        store: Long-term memory store. The caller owns it so it can inspect or
            persist memories outside the agent.
        checkpointer: Thread state persistence; defaults to in-memory.
        tier: Capability tier from the model catalog.
        provider: Pinned provider inside ``tier``; other providers become fallbacks.

    Memory and skills are read-only for the assistant and its subagents (the permissions are
    inherited): the memory consolidator updates memory after the conversation. A final answer
    that leaks Perso-Arabic script is repaired into Finglish.
    """
    return create_deep_agent(
        model=llm_model.get(tier, provider),
        system_prompt=build_personal_assistant_prompt(),
        tools=[make_web_search_tool()],
        backend=make_memory_composite_backend(),
        permissions=PERSONAL_ASSISTANT_PERMISSIONS,
        memory=[DEFAULT_USER_PROFILE_PATH],
        skills=[SKILLS_ROUTE_PREFIX, PUBLISHED_SKILLS_ROUTE_PREFIX],
        checkpointer=checkpointer if checkpointer is not None else InMemorySaver(),
        store=store,
        context_schema=UserContext,
        middleware=[make_model_fallback(tier, primary=provider), make_finglish_output_guard()],
    )
