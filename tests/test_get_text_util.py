"""Tests for text extraction, chunk formatting, and console helpers."""

import io
import sys
from unittest.mock import MagicMock

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.format_chunks_util import format_chunks
from agentlab.utils.get_text_util import get_text


def test_get_text_from_plain_string() -> None:
    message = HumanMessage(content="Hello world")
    assert get_text(message) == "Hello world"


def test_get_text_from_list_of_content_blocks() -> None:
    # Gemini and Claude provider style: content blocks with type "text"
    message = AIMessage(
        content=[  # type: ignore[arg-type]
            {"type": "text", "text": "Part 1. "},
            {"type": "text", "text": "Part 2."},
        ]
    )
    assert get_text(message) == "Part 1. Part 2."


def test_get_text_ignores_non_text_blocks_and_invalid_parts() -> None:
    message = AIMessage(
        content=[  # type: ignore[arg-type]
            {"type": "image_url", "image_url": "https://example.com/img.png"},
            {"type": "text", "text": "Only text matters."},
            "raw_string_item",
            {"other": "data"},
        ]
    )
    assert get_text(message) == "Only text matters."


def test_get_text_falls_back_to_str_for_other_types() -> None:
    class CustomPayload:
        def __str__(self) -> str:
            return "custom_payload_string"

    msg = ToolMessage(content=CustomPayload(), tool_call_id="call_1")  # type: ignore[arg-type]
    assert get_text(msg) == "custom_payload_string"


def test_format_chunks_empty_and_populated() -> None:
    assert format_chunks([]) == "No chunks found."

    docs = [
        Document(page_content="Text 1", metadata={"source": "file1.py"}),
        Document(page_content="Text 2", metadata={"source": "file2.py"}),
    ]
    formatted = format_chunks(docs)
    assert "[file1.py]\nText 1" in formatted
    assert "[file2.py]\nText 2" in formatted


def test_configure_utf8_stdout_reconfigures_when_supported() -> None:
    fake_stdout = MagicMock()
    fake_stdout.reconfigure = MagicMock()

    original_stdout = sys.stdout
    try:
        sys.stdout = fake_stdout
        configure_utf8_stdout()
        fake_stdout.reconfigure.assert_called_once_with(encoding="utf-8")
    finally:
        sys.stdout = original_stdout


def test_configure_utf8_stdout_suppresses_unsupported_operation() -> None:
    fake_stdout = MagicMock()
    fake_stdout.reconfigure.side_effect = io.UnsupportedOperation("cannot reconfigure")

    original_stdout = sys.stdout
    try:
        sys.stdout = fake_stdout
        # Must not raise
        configure_utf8_stdout()
    finally:
        sys.stdout = original_stdout
