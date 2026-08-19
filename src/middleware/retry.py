"""Middleware that retries a failed model call with a fallback model."""

from langchain.agents.middleware import ModelResponse, ModelRequest, wrap_model_call

from typing import Callable


from models import luna_model


@wrap_model_call
def retry_on_failure(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    try:
        return handler(request)

    except Exception:
        fallback_request = request.override(model=luna_model)
        return handler(fallback_request)
