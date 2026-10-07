"""Tests for the shared subagent adapter plumbing every subagents/*.py factory reuses."""

import re

from langchain_core.messages import AIMessage, HumanMessage

from agentlab.utils.subagent_util import (
    new_delegation_config,
    task_text_from_state,
    to_subagent_reply,
)

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def test_task_text_from_state_reads_the_last_message() -> None:
    state = {
        "messages": [HumanMessage(content="ignored"), HumanMessage(content="do this")],
    }

    assert task_text_from_state(state) == "do this"


def test_new_delegation_config_is_a_fresh_isolated_thread_each_call() -> None:
    first = new_delegation_config()
    second = new_delegation_config()

    assert _UUID_RE.match(first["configurable"]["thread_id"])
    assert first["configurable"]["thread_id"] != second["configurable"]["thread_id"]


def test_to_subagent_reply_wraps_a_single_ai_message() -> None:
    assert to_subagent_reply("final answer") == {
        "messages": [AIMessage(content="final answer")],
    }


def test_a_specialist_subagent_runs_the_task_and_replies_with_its_envelope() -> None:
    from langchain_core.messages import HumanMessage

    from agentlab.schemas.output.specialist_output_schema import SpecialistResult
    from agentlab.utils.subagent_util import specialist_subagent

    asked: list[str] = []

    def run(task: str) -> SpecialistResult[str]:
        asked.append(task)
        return SpecialistResult[str](
            specialist="echo", status="ok", output=task.upper()
        )

    spec = specialist_subagent("echo", "Echoes.", run, render=lambda out: f"<{out}>")
    reply = spec["runnable"].invoke({"messages": [HumanMessage(content="hi")]})

    assert (spec["name"], spec["description"], asked) == ("echo", "Echoes.", ["hi"])
    text = reply["messages"][-1].content
    assert text.startswith("[echo] status: ok") and text.endswith("<HI>")
