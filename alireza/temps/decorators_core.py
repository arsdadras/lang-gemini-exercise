"""Core decorators for wrapping agent runnables as DeepAgents CompiledSubAgent specifications."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.runnables import RunnableLambda

from temps.manifest_core import AgentManifest


def as_subagent(
    manifest: AgentManifest,
) -> Callable[[Callable[..., Any]], CompiledSubAgent]:
    """Decorator converting a state handler or runnable into a DeepAgents CompiledSubAgent dict."""

    def decorator(fn: Callable[..., Any]) -> CompiledSubAgent:
        @wraps(fn)
        def wrapper(state: dict[str, Any]) -> dict[str, Any]:
            return fn(state)

        return {
            "name": manifest.name,
            "description": manifest.description,
            "runnable": RunnableLambda(wrapper),
        }

    return decorator
