"""System prompts for subagents and other delegated workers."""

from agentlab.prompts.agents_prompt import (
    INTERPRETER_CONSTRAINTS,
    INTERPRETER_MISSION,
    INTERPRETER_OUTPUT_FORMAT,
    INTERPRETER_TOOLS,
)
from agentlab.prompts.template.worker import build_worker_prompt

RESEARCHER_SUBAGENT_PROMPT = (
    "You are a focused researcher. Use web_search to answer the "
    "exact sub-question you were given. Do not go off-topic. "
    "Return your findings with real source URLs."
)


def build_interpreter_worker_prompt() -> str:
    """The interpreter's prompt when a coordinator delegates to it: same job, no chat persona."""
    return build_worker_prompt(
        name="Interpreter Worker",
        role="a sandboxed computational and code execution worker",
        mission=INTERPRETER_MISSION,
        tools=INTERPRETER_TOOLS,
        output_format=INTERPRETER_OUTPUT_FORMAT,
        constraints=INTERPRETER_CONSTRAINTS,
    )
