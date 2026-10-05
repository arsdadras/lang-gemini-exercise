"""``read_page``: a page's text, cut, with failures that classify like any external failure."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentlab.tools import read_page_tool
from agentlab.tools.read_page_tool import MAX_PAGE_CHARS, make_read_page_tool, read_page
from agentlab.tools.web_search_tool import WebSearchError
from agentlab.utils.failure_util import failure_kind


def reply(status: int, body: dict[str, Any]) -> MagicMock:
    response = MagicMock()
    response.status_code = status
    response.json.return_value = body
    return response


@pytest.fixture(autouse=True)
def tavily_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")


def test_the_page_comes_back_with_its_url_first_and_its_text_cut() -> None:
    body = {"results": [{"raw_content": "x" * (MAX_PAGE_CHARS + 500)}]}
    with patch.object(read_page_tool.requests, "post", return_value=reply(200, body)):
        text = read_page("https://a.example")

    url, _, page = text.partition("\n\n")
    assert url == "https://a.example"
    assert len(page) == MAX_PAGE_CHARS


def test_a_page_with_no_text_is_an_error_the_model_can_act_on() -> None:
    with (
        patch.object(
            read_page_tool.requests, "post", return_value=reply(200, {"results": []})
        ),
        pytest.raises(WebSearchError, match="Try another page"),
    ):
        read_page("https://a.example")


@pytest.mark.parametrize(
    ("status", "kind"), [(429, "transient"), (502, "transient"), (401, "permanent")]
)
def test_http_failures_carry_their_status_so_they_classify(
    status: int, kind: str
) -> None:
    with (
        patch.object(read_page_tool.requests, "post", return_value=reply(status, {})),
        pytest.raises(WebSearchError) as caught,
    ):
        read_page("https://a.example")

    assert failure_kind(caught.value) == kind


def test_a_silent_server_times_out_instead_of_hanging(
    silent_server: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(read_page_tool, "TAVILY_API_URL", silent_server)
    monkeypatch.setattr(read_page_tool, "WEB_SEARCH_TIMEOUT_SECONDS", 0.3)

    with pytest.raises(Exception) as caught:
        read_page("https://a.example")

    assert failure_kind(caught.value) == "transient"


def test_the_tool_hands_a_failed_read_back_to_the_model_as_text() -> None:
    tool = make_read_page_tool()
    with patch.object(read_page_tool.requests, "post", return_value=reply(500, {})):
        message = tool.invoke({"url": "https://a.example"})

    assert "500" in message


def test_a_missing_key_says_which_variable_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TAVILY_API_KEY")

    with pytest.raises(WebSearchError, match="TAVILY_API_KEY"):
        read_page("https://a.example")
