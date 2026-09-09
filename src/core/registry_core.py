"""Universal registry for agents and subagents with lazy factory instantiation."""

import importlib
from collections.abc import Callable
from typing import Any

from core.manifest_core import AgentManifest


class AgentRegistry:
    """Registry maintaining agent and subagent factory functions and manifests."""

    def __init__(self) -> None:
        self._registry: dict[str, Callable[..., Any]] = {}
        self._manifests: dict[str, AgentManifest] = {}

    def register(
        self, name: str, manifest: AgentManifest | None = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register an agent or subagent factory function."""

        def decorator(factory_fn: Callable[..., Any]) -> Callable[..., Any]:
            if name in self._registry:
                raise ValueError(f"Agent '{name}' is already registered!")
            self._registry[name] = factory_fn
            if manifest is not None:
                self._manifests[name] = manifest
            return factory_fn

        return decorator

    def get(self, name: str, **kwargs: Any) -> Any:
        """Lazy instantiation of registered factory with automatic discovery fallback."""
        if name not in self._registry:
            # Attempt lazy auto-import of candidate modules if not yet loaded
            candidate_modules = [
                f"agents.{name}_agent",
                f"subagents.{name}_subagent",
                f"agents.{name}",
                f"subagents.{name}",
            ]
            for module_name in candidate_modules:
                try:
                    importlib.import_module(module_name)
                except ImportError:
                    pass
                if name in self._registry:
                    break

        if name not in self._registry:
            available = list(self._registry.keys())
            raise KeyError(f"Agent '{name}' not found! Available: {available}")
        factory = self._registry[name]
        return factory(**kwargs)

    def get_manifest(self, name: str) -> AgentManifest | None:
        """Retrieve manifest metadata for a registered agent if available."""
        return self._manifests.get(name)

    def list_agents(self) -> list[str]:
        """List names of all registered agents."""
        return list(self._registry.keys())

    def list_manifests(self) -> dict[str, AgentManifest]:
        """Return a copy of all registered manifests."""
        return dict(self._manifests)


# Central singleton instance
agent_registry = AgentRegistry()
