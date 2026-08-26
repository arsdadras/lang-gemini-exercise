"""Middleware factory that retries a failed model call within the same capability tier.

Reads the same tier config as `models.llm_model.chain()` — the same
retry-on-failure behavior applies whether a model is used inside an agent
(via this middleware) or invoked directly in a raw graph node (via
`llm_model.chain()`). Reusable as-is across any `create_deep_agent`/
`create_agent` in any project — pass the tier that agent's own `model=` was
built with, e.g. `middleware=[retry_on_failure("low")]`.
"""

from typing import Callable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse, wrap_model_call

from configs.models import DEFAULT_TIER
from models import llm_model


def retry_on_failure(tier: str = DEFAULT_TIER, *, cascade: bool = False) -> AgentMiddleware:
    """Build middleware that retries a failed model call against `tier`'s other providers.

    `cascade=True` extends the fallback chain into lower tiers once `tier`'s
    own providers are exhausted — see `LLMRegistry.cascade_fallback_models`.
    """

    @wrap_model_call
    def _retry_on_failure(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        try:
            return handler(request)
        except Exception:
            fallbacks = (
                llm_model.cascade_fallback_models(tier)
                if cascade
                else llm_model.fallback_models(tier)
            )
            for i, fallback in enumerate(fallbacks):
                try:
                    return handler(request.override(model=fallback))
                except Exception:
                    if i == len(fallbacks) - 1:
                        raise
            raise

    return _retry_on_failure
