"""Config-driven LLM registry — capability tier × provider, with same-tier fallback.

Replaces importing named model instances directly (`lite_model`, `flash_model`,
...) with a single `llm_model` handle keyed by capability tier ("low"/"medium"/
"high"/"free"), so the same fallback-on-failure behavior applies uniformly
wherever a model is used — a raw-graph node's `.invoke()` call, a
`create_deep_agent(model=...)`, or a middleware's own LLM call — without wiring
retry logic in separately at each site, and without a rate-limited call
silently downgrading to a cheaper tier (fallback stays within the same tier by
default, only the provider changes — cross-tier cascade is opt-in, see `chain`).
"""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from configs.models import (
    DEFAULT_TIER,
    MODEL_TIERS,
    TEST_MODE,
    TEST_TIER,
    TIER_CASCADE_ORDER,
    TIER_PROVIDER_ORDER,
)


class LLMRegistry:
    """Looks up chat models by capability tier, with same-tier fallback built in.

    Models are constructed lazily and cached — `init_chat_model(...)` isn't
    free, and every (tier, provider) pair is reused across many calls.
    """

    def __init__(
        self,
        tiers: dict[str, dict[str, dict]] = MODEL_TIERS,
        provider_order: dict[str, list[str]] = TIER_PROVIDER_ORDER,
        cascade_order: list[str] = TIER_CASCADE_ORDER,
        default_tier: str = DEFAULT_TIER,
        test_mode: bool = TEST_MODE,
        test_tier: str = TEST_TIER,
    ) -> None:
        self._tiers = tiers
        self._provider_order = provider_order
        self._cascade_order = cascade_order
        self._default_tier = default_tier
        self._test_mode = test_mode
        self._test_tier = test_tier
        self._model_cache: dict[tuple[str, str], BaseChatModel] = {}

    def _resolve_tier(self, tier: str | None) -> str:
        """Apply the default-tier and test-mode substitution rules."""
        tier = tier or self._default_tier
        return self._test_tier if self._test_mode else tier

    def _providers_for(self, tier: str) -> list[str]:
        return self._provider_order[tier]

    def get(self, tier: str | None = None, provider: str | None = None) -> BaseChatModel:
        """Return the plain (un-wrapped) model for `tier` (+ optional specific `provider`).

        Use this for `create_deep_agent(model=...)` and anywhere else that
        needs a real `BaseChatModel` (e.g. for `.bind_tools()`) rather than a
        fallback-wrapped `Runnable` — pair it with `middlewares.retry_on_failure(tier)`
        for agent-level fallback instead of `chain()`.
        """
        tier = self._resolve_tier(tier)
        provider = provider or self._providers_for(tier)[0]
        key = (tier, provider)
        if key not in self._model_cache:
            self._model_cache[key] = init_chat_model(**self._tiers[tier][provider])
        return self._model_cache[key]

    def fallback_models(self, tier: str | None = None) -> list[BaseChatModel]:
        """Return `tier`'s other providers only, in fallback order."""
        tier = self._resolve_tier(tier)
        return [self.get(tier, p) for p in self._providers_for(tier)[1:]]

    def cascade_fallback_models(self, tier: str | None = None) -> list[BaseChatModel]:
        """Return `tier`'s other providers, then every provider of each lower
        tier in `TIER_CASCADE_ORDER`, in order — a deliberate, opt-in
        "better a degraded answer than none" last resort, distinct from
        `fallback_models()`'s same-tier-only guarantee.
        """
        tier = self._resolve_tier(tier)
        models = self.fallback_models(tier)
        if tier in self._cascade_order:
            for lower_tier in self._cascade_order[self._cascade_order.index(tier) + 1 :]:
                models.extend(self.get(lower_tier, p) for p in self._providers_for(lower_tier))
        return models

    def chain(
        self,
        tier: str | None = None,
        *,
        structured: type[BaseModel] | None = None,
        cascade: bool = False,
    ) -> Runnable:
        """Return a fallback-wrapped model, optionally bound to a structured schema.

        Use for direct `.invoke()`/LCEL-chain usage (raw graph nodes,
        middleware LLM calls) — every call through the returned `Runnable`
        automatically retries on failure. `cascade=True` extends the fallback
        chain past this tier into lower tiers (see `cascade_fallback_models`)
        instead of stopping once this tier's own providers are exhausted.
        """
        tier = self._resolve_tier(tier)
        model = self.get(tier)
        fallback_models = self.cascade_fallback_models(tier) if cascade else self.fallback_models(tier)
        if structured is None:
            return model.with_fallbacks(fallback_models) if fallback_models else model

        structured_model: Runnable = model.with_structured_output(structured)
        structured_fallbacks: list[Runnable] = [
            fb.with_structured_output(structured) for fb in fallback_models
        ]
        return (
            structured_model.with_fallbacks(structured_fallbacks)
            if structured_fallbacks
            else structured_model
        )


llm_model = LLMRegistry()
