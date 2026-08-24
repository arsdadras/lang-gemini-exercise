"""Middleware that retries a failed model call with a fallback model."""

from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

from models import luna_model


@wrap_model_call
def retry_on_failure(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Retry once with a fallback model if the primary call raises."""
    try:
        return handler(request)
    except Exception:
        fallback_request = request.override(model=luna_model)
        return handler(fallback_request)
