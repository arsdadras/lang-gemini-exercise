"""Middleware that retries a failed model call against the shared fallback chain.

Reads the same fallback chain as `models.llm_model.chain()` — the same
retry-on-failure behavior applies whether a model is used inside an agent
(via this middleware) or invoked directly in a raw graph node (via
`llm_model.chain()`). Reusable as-is across any `create_deep_agent`/
`create_agent` in any project — no per-project fallback model to hardcode.
"""

from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

from models import llm_model


@wrap_model_call
def retry_on_failure(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Retry a failed model call against each fallback model in order."""
    try:
        return handler(request)
    except Exception:
        fallbacks = llm_model.fallback_models()
        for i, fallback in enumerate(fallbacks):
            try:
                return handler(request.override(model=fallback))
            except Exception:
                if i == len(fallbacks) - 1:
                    raise
        raise
