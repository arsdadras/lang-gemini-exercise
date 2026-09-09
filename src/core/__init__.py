"""Core architecture package: contracts, registry, and declarative wrappers."""

from core.decorators_core import as_subagent
from core.manifest_core import AgentManifest
from core.registry_core import AgentRegistry, agent_registry

__all__ = [
    "AgentManifest",
    "AgentRegistry",
    "agent_registry",
    "as_subagent",
]
