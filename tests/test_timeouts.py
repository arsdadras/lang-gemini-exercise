"""Every external client times out: real clients against a local server that never answers."""

import asyncio
from dataclasses import replace
from unittest.mock import patch

import pytest
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch

from agentlab.configs import timeouts_config
from agentlab.configs.models_config import EMBEDDING_SPEC, MODEL_TIERS, ModelSpec
from agentlab.graphs.rag_graph import build_rag_graph
from agentlab.models.registry_model import build_chat_model
from agentlab.retrieval import index_retrieval
from agentlab.tools import web_search_tool
from agentlab.tools.web_search_tool import (
    WebSearchError,
    _TimeoutSearchWrapper,
    search_results,
)
from agentlab.utils.failure_util import failure_kind
from agentlab.workflows.rag_workflow import run_rag
from tests.fakes import scripted_rag

SHORT = 0.3


def test_every_catalog_model_carries_a_timeout() -> None:
    specs = [spec for providers in MODEL_TIERS.values() for spec in providers.values()]

    assert all(spec.timeout_seconds > 0 for spec in specs)
    local = [spec for spec in specs if spec.model_provider == "ollama"]
    assert {spec.timeout_seconds for spec in local} == {
        timeouts_config.LOCAL_MODEL_TIMEOUT_SECONDS
    }
    hosted = [spec for spec in specs if spec.model_provider != "ollama"]
    assert {spec.timeout_seconds for spec in hosted} == {
        timeouts_config.CHAT_MODEL_TIMEOUT_SECONDS
    }


@pytest.mark.parametrize(
    ("provider", "key_env"),
    [("openai", "k"), ("google_genai", "k"), ("ollama", None)],
)
def test_a_chat_model_gives_up_on_a_silent_server(
    silent_server: str,
    provider: str,
    key_env: str | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_KEY", "k")
    spec = ModelSpec(
        model="m",
        model_provider=provider,
        api_key_env="TEST_KEY" if key_env else None,
        base_url=silent_server,
        timeout_seconds=SHORT,
    )
    model = build_chat_model(spec)
    if "max_retries" in type(model).model_fields:
        # The SDK's own retry layer would multiply the wait in this test.
        model.max_retries = 0

    with pytest.raises(Exception) as raised:
        model.invoke([HumanMessage("hi")])

    assert failure_kind(raised.value) == "transient"


def test_the_embedding_client_gives_up_on_a_silent_server(
    silent_server: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setenv("OPENROUTER_BASE_URL", silent_server)
    monkeypatch.setattr(
        index_retrieval,
        "EMBEDDING_SPEC",
        replace(EMBEDDING_SPEC, timeout_seconds=SHORT),
    )

    with pytest.raises(Exception) as raised:
        index_retrieval.make_embeddings().embed_query("hi")

    assert failure_kind(raised.value) == "transient"


def test_the_embedding_spec_carries_the_configured_timeout() -> None:
    assert EMBEDDING_SPEC.timeout_seconds == timeouts_config.EMBEDDING_TIMEOUT_SECONDS


def silent_search_tool(base_url: str) -> TavilySearch:
    wrapper = _TimeoutSearchWrapper(
        tavily_api_key="tvly-test",  # type: ignore[arg-type]
        api_base_url=base_url,
        timeout_seconds=SHORT,
    )
    return TavilySearch(api_wrapper=wrapper)


def test_the_search_tool_has_the_configured_timeout() -> None:
    with patch.dict("os.environ", {"TAVILY_API_KEY": "tvly-test"}):
        tool = web_search_tool.make_web_search_tool()

    assert (
        tool.api_wrapper.timeout_seconds == timeouts_config.WEB_SEARCH_TIMEOUT_SECONDS
    )  # type: ignore[attr-defined]


def test_a_search_gives_up_on_a_silent_server_and_surfaces_a_transient_failure(
    silent_server: str,
) -> None:
    response = silent_search_tool(silent_server).invoke({"query": "q"})

    with pytest.raises(WebSearchError) as raised:
        search_results(response)

    assert failure_kind(raised.value) == "transient"


def test_an_async_search_gives_up_on_a_silent_server(silent_server: str) -> None:
    response = asyncio.run(silent_search_tool(silent_server).ainvoke({"query": "q"}))

    with pytest.raises(WebSearchError) as raised:
        search_results(response)

    assert failure_kind(raised.value) == "transient"


def test_a_timed_out_web_search_surfaces_as_a_failed_envelope(
    silent_server: str,
) -> None:
    with scripted_rag(relevant=False, web_tool=silent_search_tool(silent_server)):
        result = run_rag(build_rag_graph(), "What is X?")

    assert result.reason.startswith(
        "An external service was unavailable, even after retries"
    )


def test_search_results_error_parsing_and_string_handling() -> None:
    # String response (such as "No results found") returns []
    assert search_results("No results found.") == []

    # Valid results return list
    valid = {"results": [{"title": "LangChain", "url": "https://langchain.com"}]}
    assert search_results(valid) == [
        {"title": "LangChain", "url": "https://langchain.com"}
    ]

    # Error with status code extracted
    with pytest.raises(WebSearchError) as exc_429:
        search_results({"error": Exception("Error 429: Too Many Requests")})
    assert exc_429.value.status_code == 429

    # Error without status code
    with pytest.raises(WebSearchError) as exc_generic:
        search_results({"error": Exception("DNS resolution failed")})
    assert exc_generic.value.status_code is None


def test_timeout_search_wrapper_raw_results_error_status() -> None:
    from unittest.mock import MagicMock

    wrapper = _TimeoutSearchWrapper(tavily_api_key="tvly-test")  # type: ignore[arg-type]

    # Sync non-200 response
    fake_resp = MagicMock()
    fake_resp.status_code = 401
    fake_resp.json.return_value = {"detail": {"error": "Invalid API key"}}

    with (
        patch("agentlab.tools.web_search_tool.requests.post", return_value=fake_resp),
        pytest.raises(ValueError, match="Error 401: Invalid API key"),
    ):
        wrapper.raw_results(query="test")

    # Sync non-200 with non-dict detail
    fake_resp.status_code = 500
    fake_resp.json.return_value = {"detail": "Server error string"}
    with (
        patch("agentlab.tools.web_search_tool.requests.post", return_value=fake_resp),
        pytest.raises(ValueError, match="Error 500: Unknown error"),
    ):
        wrapper.raw_results(query="test")
