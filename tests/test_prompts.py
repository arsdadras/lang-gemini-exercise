"""Tests for the prompt builder."""

from agentlab.prompts import DEFAULTS, build_system_prompt


def test_build_system_prompt_returns_string() -> None:
    result = build_system_prompt()
    assert isinstance(result, str)
    assert len(result) > 0


def test_build_system_prompt_default_identity() -> None:
    result = build_system_prompt()
    assert DEFAULTS["assistant_name"] in result


def test_build_system_prompt_custom_name() -> None:
    result = build_system_prompt(assistant_name="Rafigh")
    assert "Rafigh" in result
    assert DEFAULTS["assistant_name"] not in result


def test_empty_sections_dropped() -> None:
    result = build_system_prompt(drop_empty_sections=True)
    # The <tools_policy> section should be dropped when tools="" (default)
    assert "<tools_policy>" not in result


def test_empty_sections_kept() -> None:
    result = build_system_prompt(drop_empty_sections=False)
    assert "<tools_policy>" in result
