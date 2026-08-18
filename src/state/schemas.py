"""Typed state schemas for the agent runtime."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentSetup:
    """Arguments passed when constructing the agent."""

    tools: list[str] = field(default_factory=list)
    namespace: tuple[str, str, dict[str, Any]] = ("", "", {})


@dataclass
class AgentContext:
    """Per-request context available inside agent nodes."""

    user_id: str = ""
    workspace_id: str = ""
    db: Any = None
