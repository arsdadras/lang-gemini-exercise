"""Tests for the tier x provider model registry (models are stubbed; no network)."""

import pytest
from langchain_core.runnables import RunnableLambda

from agentlab.configs.models_config import ModelSpec
from agentlab.models.registry_model import LLMRegistry

TIERS = {
    "high": {
        "a": ModelSpec("high-a", "openai", "KEY"),
        "b": ModelSpec("high-b", "openai", "KEY"),
    },
    "low": {
        "c": ModelSpec("low-c", "openai", "KEY"),
        "d": ModelSpec("low-d", "openai", "KEY"),
    },
}


def make_registry(
    *,
    test_mode: bool = False,
    built: list[str] | None = None,
) -> LLMRegistry:
    def build(spec: ModelSpec) -> str:
        if built is not None:
            built.append(spec.model)
        return spec.model

    return LLMRegistry(
        TIERS,
        default_tier="low",
        cascade_order=("high", "low"),
        test_tier="low",
        test_mode=lambda: test_mode,
        model_builder=build,  # type: ignore[arg-type]
    )


def test_get_returns_primary_and_caches_models() -> None:
    built: list[str] = []
    registry = make_registry(built=built)

    assert registry.get("high") == "high-a"
    assert registry.get("high") == "high-a"
    assert registry.get() == "low-c"
    assert registry.get("high", "b") == "high-b"
    assert built == ["high-a", "low-c", "high-b"]


def test_fallbacks_stay_in_tier_and_skip_the_pinned_primary() -> None:
    registry = make_registry()

    assert registry.fallback_models("high") == ["high-b"]
    assert registry.fallback_models("high", primary="b") == ["high-a"]


def test_chain_with_a_pinned_provider_falls_back_to_the_rest_of_the_tier() -> None:
    registry = LLMRegistry(
        TIERS,
        default_tier="low",
        model_builder=lambda spec: RunnableLambda(lambda _, name=spec.model: name),
    )

    chain = registry.chain("high", provider="b")

    assert chain.invoke("hi") == "high-b"
    assert [fallback.invoke("hi") for fallback in chain.fallbacks] == ["high-a"]


def test_cascade_appends_lower_tiers_in_order() -> None:
    assert make_registry().fallback_models("high", cascade=True) == [
        "high-b",
        "low-c",
        "low-d",
    ]


def test_test_mode_routes_every_request_to_the_test_tier() -> None:
    registry = make_registry(test_mode=True)

    assert registry.get("high") == "low-c"
    assert registry.get("high", "a") == "low-c"
    assert registry.fallback_models("high", cascade=True) == ["low-d"]


def test_unknown_tier_or_provider_is_rejected() -> None:
    registry = make_registry()

    with pytest.raises(ValueError, match="Unknown tier"):
        registry.get("ultra")
    with pytest.raises(ValueError, match="no provider"):
        registry.get("low", "a")
