"""Config-driven chat model registry: capability tier x provider.

Callers ask for a capability tier instead of importing named model instances;
the registry builds each concrete model on first use and caches it.

- ``get()`` returns a plain ``BaseChatModel``. Agents need this (DeepAgents calls
  ``bind_tools`` on it); pair it with ``middlewares.make_model_fallback``.
- ``chain()`` returns a fallback-wrapped ``Runnable`` for direct calls in graph
  nodes or middleware.

Fallback stays inside the requested tier by default: a failed call changes
provider, never capability. ``cascade=True`` opts into falling through to lower
tiers.
"""

import os
from collections.abc import Callable, Mapping
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from agentlab.configs.models_config import (
    DEFAULT_TIER,
    MODEL_TIERS,
    TEST_MODE_ENV,
    TEST_TIER,
    TIER_CASCADE_ORDER,
    ModelSpec,
)

_TRUTHY = frozenset({"1", "true", "yes"})


def is_test_mode_enabled() -> bool:
    """Read ``LLM_TEST_MODE`` at call time (``.env`` may be loaded after import)."""
    return os.getenv(TEST_MODE_ENV, "false").strip().lower() in _TRUTHY


def build_chat_model(spec: ModelSpec) -> BaseChatModel:
    """Build a chat model from a spec, resolving credentials from the environment."""
    kwargs: dict[str, Any] = {
        "model": spec.model,
        "model_provider": spec.model_provider,
        "api_key": os.getenv(spec.api_key_env),
        "temperature": spec.temperature,
    }
    base_url = spec.base_url or (
        os.getenv(spec.base_url_env) if spec.base_url_env else None
    )
    if base_url:
        kwargs["base_url"] = base_url
    if spec.top_p is not None:
        kwargs["top_p"] = spec.top_p
    return init_chat_model(**kwargs)


class LLMRegistry:
    """Resolve chat models by capability tier, with same-tier fallback built in."""

    def __init__(
        self,
        tiers: Mapping[str, Mapping[str, ModelSpec]] = MODEL_TIERS,
        *,
        default_tier: str = DEFAULT_TIER,
        cascade_order: tuple[str, ...] = TIER_CASCADE_ORDER,
        test_tier: str = TEST_TIER,
        test_mode: Callable[[], bool] = is_test_mode_enabled,
        model_builder: Callable[[ModelSpec], BaseChatModel] = build_chat_model,
    ) -> None:
        self._tiers = tiers
        self._default_tier = default_tier
        self._cascade_order = cascade_order
        self._test_tier = test_tier
        self._test_mode = test_mode
        self._build = model_builder
        self._cache: dict[tuple[str, str], BaseChatModel] = {}

    def resolve_tier(self, tier: str | None = None) -> str:
        """Apply test-mode substitution, then the default tier, then validate."""
        resolved = self._test_tier if self._test_mode() else (tier or self._default_tier)
        if resolved not in self._tiers:
            msg = f"Unknown tier {resolved!r}; expected one of {sorted(self._tiers)}"
            raise ValueError(msg)
        return resolved

    def resolve_provider(self, tier: str | None = None, provider: str | None = None) -> str:
        """Return ``provider`` if the tier offers it, else the tier's primary.

        Asking a tier for a provider it doesn't offer is an error, except in test
        mode, where the request was substituted with another tier on purpose.
        """
        resolved = self.resolve_tier(tier)
        providers = list(self._tiers[resolved])
        if provider is None or provider in providers:
            return provider or providers[0]
        if self._test_mode():
            return providers[0]
        msg = f"Tier {resolved!r} has no provider {provider!r}; expected one of {providers}"
        raise ValueError(msg)

    def spec(self, tier: str | None = None, provider: str | None = None) -> ModelSpec:
        """Return the spec that ``get(tier, provider)`` would build."""
        resolved = self.resolve_tier(tier)
        return self._tiers[resolved][self.resolve_provider(resolved, provider)]

    def get(self, tier: str | None = None, provider: str | None = None) -> BaseChatModel:
        """Return the cached plain model for ``tier`` (and optional ``provider``)."""
        resolved = self.resolve_tier(tier)
        name = self.resolve_provider(resolved, provider)
        key = (resolved, name)
        if key not in self._cache:
            self._cache[key] = self._build(self._tiers[resolved][name])
        return self._cache[key]

    def fallback_models(
        self,
        tier: str | None = None,
        *,
        primary: str | None = None,
        cascade: bool = False,
    ) -> list[BaseChatModel]:
        """Return fallbacks for a model built with ``get(tier, primary)``.

        Same-tier providers other than ``primary`` come first. With ``cascade=True``
        every provider of each lower tier follows, in ``TIER_CASCADE_ORDER``.
        """
        resolved = self.resolve_tier(tier)
        primary_name = self.resolve_provider(resolved, primary)
        models = [
            self.get(resolved, name) for name in self._tiers[resolved] if name != primary_name
        ]
        if cascade and not self._test_mode() and resolved in self._cascade_order:
            start = self._cascade_order.index(resolved) + 1
            for lower_tier in self._cascade_order[start:]:
                models.extend(self.get(lower_tier, name) for name in self._tiers[lower_tier])
        return models

    def chain(
        self,
        tier: str | None = None,
        *,
        structured: type[BaseModel] | None = None,
        provider: str | None = None,
        cascade: bool = False,
    ) -> Runnable:
        """Return the tier's primary model (or the pinned ``provider``) wrapped with its fallbacks.

        Structured output is bound to each model *before* wrapping, because
        ``RunnableWithFallbacks`` has no ``with_structured_output`` of its own.
        """
        primary: Runnable = self.get(tier, provider)
        fallbacks: list[Runnable] = list(self.fallback_models(tier, primary=provider, cascade=cascade))
        if structured is not None:
            primary = self.get(tier, provider).with_structured_output(structured)
            fallbacks = [
                model.with_structured_output(structured)
                for model in self.fallback_models(tier, primary=provider, cascade=cascade)
            ]
        return primary.with_fallbacks(fallbacks) if fallbacks else primary


llm_model = LLMRegistry()
