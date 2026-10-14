"""Tests for P1 researcher CLI app (argument parsing and error handling)."""

from unittest.mock import MagicMock, patch

import pytest

from agentlab.apps.research_app import main, parse_args


def test_parse_args_defaults() -> None:
    args = parse_args([])
    assert args.session is None
    assert args.depth == "standard"
    assert args.corpus == []


def test_parse_args_with_options() -> None:
    args = parse_args(["new", "--depth", "quick", "--corpus", "doc1.txt", "doc2.md"])
    assert args.session == "new"
    assert args.depth == "quick"
    assert args.corpus == ["doc1.txt", "doc2.md"]


def test_main_rejects_invalid_corpus_files(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch(
            "agentlab.apps.research_app.parse_args",
            return_value=parse_args(["--corpus", "nonexistent_file_12345.xyz"]),
        ),
    ):
        main()

    output = capsys.readouterr().out
    assert "Cannot use these files:" in output


def test_main_handles_empty_topic_input(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with (
        patch("agentlab.apps.research_app.parse_args", return_value=parse_args([])),
        patch(
            "agentlab.apps.research_app.resolve_session",
            return_value=MagicMock(),
        ),
        patch("builtins.input", return_value="   "),
    ):
        main()

    output = capsys.readouterr().out
    assert "No topic given." in output
