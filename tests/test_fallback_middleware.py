"""Agent fallback middleware: test mode builds every agent, production tiers must have a fallback."""

from unittest.mock import patch

import pytest
from langchain.agents.middleware import ModelFallbackMiddleware
from langchain_core.language_models import FakeListChatModel

from agentlab.configs.models_config import ModelSpec
from agentlab.middlewares import fallback_middleware
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.models.registry_model import LLMRegistry

TIERS = {
    "low": {
        "a": ModelSpec("low-a", "openai", "KEY"),
        "b": ModelSpec("low-b", "openai", "KEY"),
    },
    "free": {"g": ModelSpec("free-g", "google_genai", "KEY")},
}


def registry(*, test_mode: bool) -> LLMRegistry:
    return LLMRegistry(
        TIERS,
        default_tier="low",
        cascade_order=("low",),
        test_tier="free",
        test_mode=lambda: test_mode,
        model_builder=lambda spec: FakeListChatModel(responses=[spec.model]),
    )


def test_a_tier_with_two_providers_gets_one_fallback_middleware() -> None:
    with patch.object(fallback_middleware, "llm_model", registry(test_mode=False)):
        middleware = make_model_fallback("low")

    assert len(middleware) == 1
    assert isinstance(middleware[0], ModelFallbackMiddleware)


def test_a_single_provider_test_tier_builds_the_agent_without_fallback() -> None:
    with patch.object(fallback_middleware, "llm_model", registry(test_mode=True)):
        assert make_model_fallback("low") == []


def test_a_production_tier_without_a_fallback_is_a_catalog_error() -> None:
    with (
        patch.object(fallback_middleware, "llm_model", registry(test_mode=False)),
        pytest.raises(ValueError, match="'free' has no fallback"),
    ):
        make_model_fallback("free")
