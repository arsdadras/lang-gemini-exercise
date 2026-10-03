"""Tests for failure classes: real library exceptions, retry policy behavior, safe reasons."""

import operator
from collections.abc import Callable
from typing import Annotated, TypedDict

import anthropic
import httpx
import openai
import pytest
import requests
from google.genai import errors as genai_errors
from langchain_google_genai._common import GoogleGenerativeAIError
from langgraph.graph import END, START, StateGraph

from agentlab.tools.web_search_tool import WebSearchError, search_results
from agentlab.utils.failure_util import (
    TRANSIENT_RETRY,
    failure_kind,
    failure_reason,
    is_transient,
)

REQUEST = httpx.Request("POST", "https://api.example/v1")


def status_error(
    sdk_error: type[openai.APIStatusError], status: int
) -> openai.APIStatusError:
    return sdk_error(
        "failed", response=httpx.Response(status, request=REQUEST), body=None
    )


def raised_from(cause: Exception, wrapper: Exception) -> Exception:
    """``wrapper`` as a library raises it: ``raise wrapper from cause``."""
    try:
        try:
            raise cause
        except Exception as error:
            raise wrapper from error
    except type(wrapper) as wrapped:
        return wrapped


@pytest.mark.parametrize(
    ("error", "kind"),
    [
        (status_error(openai.RateLimitError, 429), "transient"),
        (status_error(anthropic.InternalServerError, 529), "transient"),
        (status_error(openai.AuthenticationError, 401), "permanent"),
        (status_error(anthropic.BadRequestError, 400), "permanent"),
        (
            raised_from(
                httpx.ReadTimeout("slow"), openai.APITimeoutError(request=REQUEST)
            ),
            "transient",
        ),
        (requests.ConnectionError("refused"), "transient"),
        (
            WebSearchError("Error 503: Service Unavailable", status_code=503),
            "transient",
        ),
    ],
)
def test_provider_errors_are_classified_by_status_or_network_failure(
    error: Exception, kind: str
) -> None:
    assert failure_kind(error) == kind


def call_openai(base_url: str, timeout: float) -> None:
    client = openai.OpenAI(
        api_key="test", base_url=base_url, max_retries=0, timeout=timeout
    )
    client.chat.completions.create(
        model="m", messages=[{"role": "user", "content": "hi"}]
    )


def call_anthropic(base_url: str, timeout: float) -> None:
    client = anthropic.Anthropic(
        api_key="test", base_url=base_url, max_retries=0, timeout=timeout
    )
    client.messages.create(
        model="m", max_tokens=1, messages=[{"role": "user", "content": "hi"}]
    )


@pytest.mark.parametrize(
    ("call", "sdk_error"),
    [
        (call_openai, openai.APITimeoutError),
        (call_anthropic, anthropic.APITimeoutError),
    ],
)
def test_a_real_sdk_timeout_is_transient(
    silent_server: str, call: Callable[[str, float], None], sdk_error: type[Exception]
) -> None:
    with pytest.raises(sdk_error) as raised:
        call(silent_server, 0.3)

    assert failure_kind(raised.value) == "transient"


def test_a_real_sdk_connection_refusal_is_transient(closed_port: str) -> None:
    with pytest.raises(openai.APIConnectionError) as raised:
        call_openai(closed_port, 5.0)

    assert failure_kind(raised.value) == "transient"


def test_a_wrapped_provider_error_is_classified_by_its_cause() -> None:
    client_error = genai_errors.ClientError(
        400, {"error": {"code": 400, "message": "API key not valid."}}
    )

    wrapped = raised_from(
        client_error, GoogleGenerativeAIError("Error embedding content")
    )

    assert failure_kind(wrapped) == "permanent"


def test_our_own_errors_are_bugs() -> None:
    assert failure_kind(TypeError("unsupported operand")) is None
    assert failure_kind(KeyError("generation")) is None


def test_a_bug_raised_while_handling_an_outage_is_still_a_bug() -> None:
    try:
        try:
            raise httpx.ConnectError("refused")
        except httpx.ConnectError:
            {}["missing"]
    except KeyError as bug:
        assert failure_kind(bug) is None


def test_reasons_are_one_line_and_redact_secrets() -> None:
    error = status_error(openai.AuthenticationError, 401)
    error.args = (
        "Incorrect API key provided: sk-proj-" + "a1B2c3D4" * 4 + "\nmore detail",
    )

    reason = failure_reason(error)

    assert reason.startswith("An external service rejected the request")
    assert "sk-proj-" not in reason and "\n" not in reason


class Counter(TypedDict):
    calls: Annotated[list[int], operator.add]


def graph_failing_with(error: Exception, times: int):
    """A one-node graph whose node raises ``error`` ``times`` times, then succeeds."""
    attempts = []

    def flaky(state: Counter) -> dict:
        attempts.append(1)
        if len(attempts) <= times:
            raise error
        return {"calls": [len(attempts)]}

    graph = StateGraph(Counter)
    graph.add_node(
        "flaky", flaky, retry_policy=TRANSIENT_RETRY._replace(initial_interval=0.01)
    )
    graph.add_edge(START, "flaky")
    graph.add_edge("flaky", END)
    return graph.compile(), attempts


def test_the_retry_policy_retries_an_outage_but_not_a_rejection() -> None:
    flaky, flaky_attempts = graph_failing_with(httpx.ConnectError("refused"), times=2)
    rejecting, rejecting_attempts = graph_failing_with(
        status_error(openai.AuthenticationError, 401), times=1
    )

    assert flaky.invoke({"calls": []})["calls"] == [3]
    with pytest.raises(openai.AuthenticationError):
        rejecting.invoke({"calls": []})
    assert (len(flaky_attempts), len(rejecting_attempts)) == (3, 1)
    assert is_transient(httpx.ConnectError("refused"))


def test_search_results_surfaces_what_tavily_returns_instead_of_raising() -> None:
    with pytest.raises(WebSearchError) as outage:
        search_results(
            {
                "error": ValueError(
                    "Error 401: Unauthorized: missing or invalid API key."
                )
            }
        )

    assert outage.value.status_code == 401
    assert search_results("No search results found for 'q'.") == []
    assert search_results({"results": [{"url": "u", "content": "c"}]}) == [
        {"url": "u", "content": "c"}
    ]
