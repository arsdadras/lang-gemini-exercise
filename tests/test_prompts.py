"""Tests for the prompt builder."""

from agentlab.prompts import (
    DEFAULTS,
    build_interpreter_agent_prompt,
    build_interpreter_worker_prompt,
    build_system_prompt,
)
from agentlab.prompts.template.worker import build_worker_prompt


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


def test_worker_prompt_has_no_chat_persona() -> None:
    worker = build_interpreter_worker_prompt()
    chat = build_interpreter_agent_prompt()

    for chat_only in ("Finglish", "user_profile", "response_modes"):
        assert chat_only in chat
        assert chat_only not in worker
    assert "Write in English" in worker


def test_worker_prompt_keeps_the_job_and_drops_empty_sections() -> None:
    worker = build_worker_prompt(name="W", role="a worker", mission="Do the thing.")

    assert "Do the thing." in worker
    assert "<tools_policy>" not in worker
    assert "<constraints>" not in worker
    assert build_interpreter_worker_prompt().count("`execute`") >= 1
