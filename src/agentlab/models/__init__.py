"""LLM and decision-model instances and configuration."""

from agentlab.models.decision_model import DecisionRegistry, decision_model
from agentlab.models.registry_model import LLMRegistry, llm_model
from agentlab.models.router_model import ModelRouter, model_router

__all__ = [
    "DecisionRegistry",
    "LLMRegistry",
    "ModelRouter",
    "decision_model",
    "llm_model",
    "model_router",
]
