# Part I, Definition of Specification:
from typing import Literal
from pydantic import BaseModel, Field

class AgentManifest(BaseModel):
    name: str = Field(..., description="Unique slug for the agent")
    display_name: str
    description: str = Field(..., description="Exposed to Supervisor LLM for delegation")
    agent_type: Literal["pure", "supervisor"] = "pure"
    model_tier: Literal["low", "medium", "high"] = "medium"
    # If agent_type is "pure", list of tool names it can use
    tools: list[str] = Field(default_factory=list)
    # If agent_type is "supervisor", list of subagent names it can delegate to
    subagent_names: list[str] = Field(default_factory=list)


# part II, Definition of Registration:
from _collections_abc import Callable
from typing import Any

