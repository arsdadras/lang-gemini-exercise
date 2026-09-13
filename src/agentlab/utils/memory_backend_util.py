"""Long-term memory wiring for the P5 assistant: virtual filesystem routes over a LangGraph store."""

from pathlib import Path

from deepagents.backends import (
    BackendProtocol,
    CompositeBackend,
    FilesystemBackend,
    StateBackend,
    StoreBackend,
)
from langgraph.runtime import Runtime

from agentlab.configs.personal_assistant_config import (
    MEMORIES_ROUTE_PREFIX,
    SKILLS_DIR,
    SKILLS_ROUTE_PREFIX,
)
from agentlab.schemas.context.user_context_schema import UserContext

MEMORIES_NAMESPACE_KIND = "memories"


def user_memory_namespace(runtime: Runtime[UserContext] | None) -> tuple[str, str]:
    """Store namespace for the current user's long-term memories: ``(user_id, "memories")``.

    ``StoreBackend`` calls this on every file operation with the LangGraph
    ``Runtime`` of the running graph. Identity must come from ``runtime.context``
    (set with ``agent.invoke(..., context=UserContext(...))``): ``Runtime`` has no
    ``config``, so reading ``configurable`` here would silently put every user in
    one namespace. Missing identity is an error, never a shared default.
    """
    context = runtime.context if runtime is not None else None
    if not isinstance(context, UserContext) or not context.user_id.strip():
        msg = "User memory requires context=UserContext(user_id=...) on the invocation"
        raise ValueError(msg)
    return context.user_id.strip(), MEMORIES_NAMESPACE_KIND


def make_memory_composite_backend(
    skills_dir: Path = SKILLS_DIR,
    default: BackendProtocol | None = None,
) -> CompositeBackend:
    """Route the assistant's virtual paths to the right storage.

    - ``/memories/`` -> ``StoreBackend``: durable, one namespace per user. The store
      itself is the one compiled into the running agent (``create_deep_agent(store=...)``).
    - ``/skills/`` -> ``FilesystemBackend`` over the packaged skill files.
    - anything else -> ``StateBackend``: scratch files that live only in the thread's state.
    """
    return CompositeBackend(
        default=default if default is not None else StateBackend(),
        routes={
            MEMORIES_ROUTE_PREFIX: StoreBackend(namespace=user_memory_namespace),
            SKILLS_ROUTE_PREFIX: FilesystemBackend(root_dir=skills_dir, virtual_mode=True),
        },
    )
