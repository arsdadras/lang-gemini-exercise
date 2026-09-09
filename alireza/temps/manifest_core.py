"""Agent manifest schema defining declarative metadata and contracts for agents."""

from typing import Literal

from pydantic import BaseModel, Field


class AgentManifest(BaseModel):
    """Declarative specification describing agent capabilities, roles, and boundaries."""

    name: str = Field(..., description="Unique slug for the agent")
    display_name: str
    description: str = Field(
        ..., description="Exposed to Supervisor / Coordinator LLM for delegation"
    )
    agent_type: Literal["pure", "supervisor"] = "pure"
    model_tier: Literal["low", "medium", "high", "free"] = "medium"
    tools: list[str] = Field(default_factory=list)
    subagent_names: list[str] = Field(default_factory=list)
