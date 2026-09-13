"""Virtual memory backend utility for DeepAgents and LangGraph Store routing."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from deepagents.backends import (
    BackendProtocol,
    CompositeBackend,
    FilesystemBackend,
    StateBackend,
    StoreBackend,
)
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from configs.personal_assistant_config import (
    DEFAULT_USER_ID,
    MEMORIES_ROUTE_PREFIX,
    SKILLS_DATA_DIR,
    SKILLS_NAMESPACE,
    SKILLS_ROUTE_PREFIX,
)


def make_memory_namespace(runtime: Any | None = None) -> tuple[str, str]:
    """Resolve the per-user memory namespace tuple from the LangGraph execution runtime.

    Under the hood, DeepAgents StoreBackend executes this callable during file operations
    to determine which store partition (namespace) to write to or read from.

    If runtime is None (e.g. backend accessed outside of graph invoke) or configurable
    does not specify a user_id, falls back to DEFAULT_USER_ID.
    """
    user_id = DEFAULT_USER_ID
    if runtime is not None:
        config = getattr(runtime, "config", {}) or {}
        configurable = config.get("configurable", {})
        candidate = configurable.get("user_id")
        if candidate:
            user_id = str(candidate).strip()

    return user_id, "memories"


def make_skills_namespace(runtime: Any | None = None) -> tuple[str, ...]:
    """Resolve the shared skills namespace for procedural memory.

    Unlike user declarative memory (which dynamically partitions per user_id via
    runtime), procedural skills are operational SOPs shared across all users.
    The runtime argument is accepted to satisfy DeepAgents' NamespaceFactory
    contract, but ignored.
    """
    return SKILLS_NAMESPACE


def make_memory_composite_backend(
    store: BaseStore | None = None,
    default_backend: BackendProtocol | None = None,
    skills_backend: BackendProtocol | None = None,
    skills_dir: Path | str | None = None,
    namespace_factory: Callable[[Any | None], tuple[str, str]] = make_memory_namespace,
) -> CompositeBackend:
    """Build a CompositeBackend routing persistent /memories/ to StoreBackend and /skills/ to FilesystemBackend.

    - Default backend (unmatched paths, e.g. /workspace/, /temp.txt): StateBackend (ephemeral
      to the current conversation thread).
    - Routed path (/memories/): StoreBackend wired to the persistent LangGraph BaseStore
      scoped dynamically per-user via `namespace_factory`.
    - Routed path (/skills/): FilesystemBackend wired directly to the disk directory
      housing procedural SOP markdown files (e.g. `src/data/skills/`).

    Args:
        store: LangGraph BaseStore instance (e.g. InMemoryStore or SqliteStore). If None,
            defaults to an InMemoryStore for Phase A testing.
        default_backend: Fallback backend for non-memory paths. Defaults to StateBackend().
        skills_backend: Custom backend for skills. If None, instantiates FilesystemBackend.
        skills_dir: Disk directory path for skills. Defaults to SKILLS_DATA_DIR.
        namespace_factory: Callable receiving runtime and returning the namespace tuple.
            Defaults to `make_memory_namespace`.

    Returns:
        A ready-to-use CompositeBackend instance.
    """
    if store is None:
        store = InMemoryStore()

    if default_backend is None:
        default_backend = StateBackend()

    memory_store_backend = StoreBackend(
        namespace=namespace_factory,
        store=store,
    )

    if skills_backend is None:
        target_skills_dir = Path(skills_dir) if skills_dir is not None else SKILLS_DATA_DIR
        target_skills_dir.mkdir(parents=True, exist_ok=True)
        skills_backend = FilesystemBackend(root_dir=str(target_skills_dir))

    return CompositeBackend(
        default=default_backend,
        routes={
            MEMORIES_ROUTE_PREFIX: memory_store_backend,
            SKILLS_ROUTE_PREFIX: skills_backend,
        },
    )
