"""Middleware that retries a failed model call with a fallback model."""

<<<<<<< HEAD
from langchain.agents.middleware import ModelResponse, ModelRequest, wrap_model_call

from typing import Callable

=======
from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
>>>>>>> ac268283fa2050850887180009b388e00afa28e8

from models import luna_model


@wrap_model_call
def retry_on_failure(
<<<<<<< HEAD
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    try:
        return handler(request)

=======
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """Retry once with a fallback model if the primary call raises."""
    try:
        return handler(request)
>>>>>>> ac268283fa2050850887180009b388e00afa28e8
    except Exception:
        fallback_request = request.override(model=luna_model)
        return handler(fallback_request)
