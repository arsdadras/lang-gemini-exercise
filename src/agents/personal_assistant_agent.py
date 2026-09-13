"""P5 Memory-Rich Personal Assistant agent — maintains ongoing user context across sessions."""

from collections.abc import Sequence
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from configs.personal_assistant_config import (
    DEFAULT_ASSISTANT_PROVIDER,
    DEFAULT_ASSISTANT_TIER,
    DEFAULT_USER_PROFILE_PATH,
    SKILLS_ROUTE_PREFIX,
)
from core.manifest import AgentManifest
from core.registry import agent_registry
from models import llm_model
from prompts.agents_prompt import build_personal_assistant_prompt
from tools.web_search_tool import web_search
from utils.memory_backend_util import make_memory_composite_backend

personal_assistant_manifest = AgentManifest(
    name="personal_assistant",
    display_name="Personal Assistant Agent",
    description="Maintains ongoing user context, manages user preferences, and persists long-term memories across sessions.",
    agent_type="pure",
    model_tier=DEFAULT_ASSISTANT_TIER,
    tools=["read_file", "write_file", "edit_file", "ls", "web_search"],
)


@agent_registry.register("personal_assistant", manifest=personal_assistant_manifest)
def make_personal_assistant_agent(
    backend: CompositeBackend | None = None,
    store: BaseStore | None = None,
    checkpointer: Any | None = None,
    tier: str = DEFAULT_ASSISTANT_TIER,
    provider: str | None = DEFAULT_ASSISTANT_PROVIDER,
    tools: Sequence[BaseTool | Any] | None = None,
    memory_sources: list[str] | None = None,
    skills: list[str] | None = None,
    response_format: Any | None = None,
):
    """Build and return an autonomous Personal Assistant agent with composite memory and procedural skills."""
    if store is None:
        store = InMemoryStore()

    if backend is None:
        backend = make_memory_composite_backend(store=store)

    if checkpointer is None:
        checkpointer = InMemorySaver()

    if tools is None:
        tools = [web_search]

    if memory_sources is None:
        memory_sources = [DEFAULT_USER_PROFILE_PATH]

    if skills is None:
        skills = [SKILLS_ROUTE_PREFIX]

    agent = create_deep_agent(
        model=llm_model.get(tier=tier, provider=provider),
        system_prompt=build_personal_assistant_prompt(),
        tools=tools,
        backend=backend,
        memory=memory_sources,
        skills=skills,
        checkpointer=checkpointer,
        store=store,
        response_format=response_format,
    )

    # Expose backing store and backend references for external inspection/testing
    agent.store = store
    agent.backend = backend
    return agent


# Ready-to-invoke default agent instance
personal_assistant_agent = make_personal_assistant_agent()
