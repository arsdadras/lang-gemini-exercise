"""Config-driven LLM registry with a shared fallback chain.

Replaces importing named model instances directly (`lite_model`, `flash_model`,
...) with a single `llm_model` handle, so the same fallback-on-failure behavior
applies uniformly wherever a model is used — a raw-graph node's `.invoke()`
call, a `create_deep_agent(model=...)`, or a middleware's own LLM call —
without having to remember to wire retry logic in separately at each site.
"""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import Runnable
from pydantic import BaseModel

from configs.models import DEFAULT_ROLE, FALLBACK_CHAIN, MODEL_REGISTRY


class LLMRegistry:
    """Looks up chat models by role, with fallback wrapping built in.

    Models are constructed lazily and cached — `init_chat_model(...)` isn't
    free, and every role/fallback is reused across many calls.
    """

    def __init__(
        self,
        registry: dict[str, dict] = MODEL_REGISTRY,
        fallback_chain: list[dict] = FALLBACK_CHAIN,
    ) -> None:
        self._registry = registry
        self._fallback_chain = fallback_chain
        self._model_cache: dict[str, BaseChatModel] = {}
        self._fallback_models_cache: list[BaseChatModel] | None = None

    def get(self, role: str = DEFAULT_ROLE) -> BaseChatModel:
        """Return the plain (un-wrapped) model for `role`.

        Use this for `create_deep_agent(model=...)` and anywhere else that
        needs a real `BaseChatModel` (e.g. for `.bind_tools()`) rather than a
        fallback-wrapped `Runnable` — pair it with `middlewares.retry_on_failure`
        for agent-level fallback instead of `chain()`.
        """
        if role not in self._model_cache:
            self._model_cache[role] = init_chat_model(**self._registry[role])
        return self._model_cache[role]

    def fallback_models(self) -> list[BaseChatModel]:
        """Return the shared fallback chain's models, constructed once."""
        if self._fallback_models_cache is None:
            self._fallback_models_cache = [
                init_chat_model(**cfg) for cfg in self._fallback_chain
            ]
        return self._fallback_models_cache

    def chain(
        self, role: str = DEFAULT_ROLE, *, structured: type[BaseModel] | None = None
    ) -> Runnable:
        """Return a fallback-wrapped model, optionally bound to a structured schema.

        Use for direct `.invoke()`/LCEL-chain usage (raw graph nodes,
        middleware LLM calls) — every call through the returned `Runnable`
        automatically retries against the shared fallback chain on failure.
        """
        primary = self.get(role)
        fallbacks = self.fallback_models()
        if structured is not None:
            primary = primary.with_structured_output(structured)
            fallbacks = [fb.with_structured_output(structured) for fb in fallbacks]
        return primary.with_fallbacks(fallbacks) if fallbacks else primary


llm_model = LLMRegistry()
