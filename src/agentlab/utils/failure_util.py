"""Failure classes for specialist runs: what to retry, what to report, and what to let crash.

An external service can fail two ways. A transient failure (rate limit, timeout, 5xx) may
pass on a retry; a permanent one (bad key, bad request) won't. Anything that isn't an
external failure is a bug in our code, and it must crash instead of becoming a quiet
``failed`` envelope.
"""

from collections.abc import Iterator
from typing import Literal

import httpx
import httpx2
import requests
from langgraph.types import RetryPolicy

from agentlab.utils.secret_redaction_util import redact_secrets

FailureKind = Literal["transient", "permanent"]

_TRANSIENT_STATUSES = frozenset({408, 429})
# Each HTTP stack an external client uses: httpx2 (openai 3.x, anthropic 1.x), httpx
# (google-genai), and requests (Tavily). An SDK upgrade can move a client to another stack.
_NETWORK_ERRORS = (
    TimeoutError,
    ConnectionError,
    httpx2.TimeoutException,
    httpx2.NetworkError,
    httpx.TimeoutException,
    httpx.NetworkError,
    requests.ConnectionError,
    requests.Timeout,
)


def _explicit_chain(error: BaseException) -> Iterator[BaseException]:
    """``error``, then each exception it was raised ``from``.

    Libraries wrap the provider's error (``raise XError(...) from e``), so the status often
    sits one or two links down. Implicit context (an error raised while handling another)
    is not followed: a bug inside an ``except`` block would inherit the other error's class.
    """
    current: BaseException | None = error
    while current is not None:
        yield current
        current = current.__cause__


def _http_status(error: BaseException) -> int | None:
    """The HTTP error status an exception carries, under any of the names libraries use."""
    response = getattr(error, "response", None)
    for candidate in (
        getattr(error, "status_code", None),  # openai, anthropic
        getattr(error, "code", None),  # google-genai
        getattr(response, "status_code", None),  # httpx, requests
    ):
        if isinstance(candidate, int) and 400 <= candidate < 600:
            return candidate
    return None


def failure_kind(error: BaseException) -> FailureKind | None:
    """Classify ``error`` as a transient or permanent external failure, or ``None`` for a bug."""
    for link in _explicit_chain(error):
        status = _http_status(link)
        if status is not None:
            transient = status in _TRANSIENT_STATUSES or status >= 500
            return "transient" if transient else "permanent"
        if isinstance(link, _NETWORK_ERRORS):
            return "transient"
    return None


def is_transient(error: Exception) -> bool:
    """``retry_on`` for retry policies: retry only what a retry can fix."""
    return failure_kind(error) == "transient"


# One retry layer, on nodes whose external call has none of its own (model SDKs already
# retry, and the model fallback switches providers).
TRANSIENT_RETRY = RetryPolicy(max_attempts=3, retry_on=is_transient)


def failure_reason(error: BaseException) -> str:
    """A one-line ``reason`` for a ``failed`` envelope, safe to show a model or a trace."""
    what = (
        "was unavailable, even after retries"
        if failure_kind(error) == "transient"
        else "rejected the request"
    )
    first_line = (str(error).splitlines() or [type(error).__name__])[0]
    return f"An external service {what}: {redact_secrets(first_line[:200])[0]}"
