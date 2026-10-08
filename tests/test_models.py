"""Tests for the tier x provider model registry (models are stubbed; no network)."""

import pytest
from langchain_core.runnables import RunnableLambda

from agentlab.configs.models_config import MODEL_TIERS, ModelSpec
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


def test_a_spec_caps_output_tokens_and_its_env_var_overrides_the_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from agentlab.models.registry_model import build_chat_model

    monkeypatch.setenv("ROUTER_KEY", "test-key")
    monkeypatch.setenv("ROUTER_URL", "http://127.0.0.1:9/v1")
    spec = ModelSpec(
        model="vendor/model",
        model_provider="openai",
        api_key_env="ROUTER_KEY",
        base_url="https://router.example/v1",
        base_url_env="ROUTER_URL",
        max_tokens=4096,
    )

    model = build_chat_model(spec)

    assert model.max_tokens == 4096
    assert model.openai_api_base == "http://127.0.0.1:9/v1"


def test_each_provider_is_followed_by_its_backup_gateway() -> None:
    def via_gateway(model: str) -> ModelSpec:
        return ModelSpec(
            model, "openai", "KEY", backup=ModelSpec(f"{model}@router", "openai", "KEY")
        )

    registry = LLMRegistry(
        {"high": {"a": via_gateway("high-a"), "b": via_gateway("high-b")}},
        default_tier="high",
        cascade_order=("high",),
        test_tier="high",
        test_mode=lambda: False,
        model_builder=lambda spec: spec.model,  # type: ignore[arg-type,return-value]
    )

    assert registry.get("high") == "high-a"
    assert registry.fallback_models("high") == [
        "high-a@router",
        "high-b",
        "high-b@router",
    ]
    assert registry.fallback_models("high", primary="b") == [
        "high-b@router",
        "high-a",
        "high-a@router",
    ]


def ladder(tier: str) -> list[tuple[str, str]]:
    """The models a test-mode tier tries, in order, as (model, gateway key variable)."""
    registry = LLMRegistry(
        MODEL_TIERS,
        test_tier="free",
        test_mode=lambda: False,
        model_builder=lambda spec: spec,  # type: ignore[arg-type,return-value]
    )
    primary = registry.get(tier)
    chain = [primary, *registry.fallback_models(tier)]
    return [(spec.model, spec.api_key_env or "") for spec in chain]  # type: ignore[attr-defined]


def test_test_mode_ladder_free_is_flash_lite_on_google_then_gapgpt_then_openrouter() -> None:
    assert ladder("free") == [
        ("gemini-3.5-flash-lite", "GOOGLE_API_KEY"),
        ("gemini-3.5-flash-lite", "GAPGPT_API_KEY"),
        ("google/gemini-3.5-flash-lite", "OPENROUTER_API_KEY"),
    ]


def test_test_mode_ladder_strong_is_haiku_then_luna_each_on_gapgpt_then_openrouter() -> (
    None
):
    assert ladder("strong") == [
        ("claude-haiku-5-5", "GAPGPT_API_KEY"),
        ("anthropic/claude-haiku-5.5", "OPENROUTER_API_KEY"),
        ("gpt-6-luna", "GAPGPT_API_KEY"),
        ("openai/gpt-6-luna", "OPENROUTER_API_KEY"),
    ]


def test_test_mode_ladder_strongest_is_flash_sonnet_sol_gateways_only() -> None:
    assert ladder("strongest") == [
        ("gemini-3.8-flash", "GAPGPT_API_KEY"),
        ("google/gemini-3.8-flash", "OPENROUTER_API_KEY"),
        ("claude-sonnet-5-5", "GAPGPT_API_KEY"),
        ("anthropic/claude-sonnet-5.5", "OPENROUTER_API_KEY"),
        ("gpt-6.1-sol", "GAPGPT_API_KEY"),
        ("openai/gpt-6.1-sol", "OPENROUTER_API_KEY"),
    ]


def test_only_flash_lite_is_ever_called_on_googles_api() -> None:
    from agentlab.configs.models_config import MODEL_TIERS as tiers

    google = {
        spec.model
        for providers in tiers.values()
        for spec in providers.values()
        if spec.model_provider == "google_genai"
    }

    assert google == {"gemini-3.5-flash-lite"}


def test_the_test_profiles_map_the_ladder_and_opt_in_tiers_stay_out_of_the_cascade() -> (
    None
):
    from agentlab.configs.models_config import TEST_MODE_PROFILES, TIER_CASCADE_ORDER

    assert TEST_MODE_PROFILES == {
        "default": "free",
        "strong": "strong",
        "strongest": "strongest",
        "local": "local",
    }
    assert {"free", "strong", "strongest", "last_resort"}.isdisjoint(TIER_CASCADE_ORDER)
