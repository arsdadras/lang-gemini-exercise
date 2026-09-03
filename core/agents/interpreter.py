"""P4 Sandbox / Interpreter agent — executes and verifies Python scripts in an isolated workspace."""

from typing import Any

from configs.interpreter import (
    DEFAULT_EXECUTE_TIMEOUT,
    DEFAULT_INHERIT_ENV,
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_SANDBOX_DIR,
    DEFAULT_VIRTUAL_MODE,
)
from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langgraph.checkpoint.memory import InMemorySaver
from models import llm_model
from prompts.agents import build_interpreter_agent_prompt


def make_interpreter_agent(
    backend: LocalShellBackend | None = None,
    checkpointer: Any | None = None,
    tier: str = "medium",
    response_format: type | None = None,
):
    """Build and return an autonomous Sandbox / Interpreter agent."""
    if backend is None:
        DEFAULT_SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
        backend = LocalShellBackend(
            root_dir=DEFAULT_SANDBOX_DIR,
            virtual_mode=DEFAULT_VIRTUAL_MODE,
            inherit_env=DEFAULT_INHERIT_ENV,
            timeout=DEFAULT_EXECUTE_TIMEOUT,
            max_output_bytes=DEFAULT_MAX_OUTPUT_BYTES,
        )

    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_interpreter_agent_prompt(),
        backend=backend,
        checkpointer=checkpointer or InMemorySaver(),
        response_format=response_format,
    )


# Ready-to-invoke default agent instance
interpreter_agent = make_interpreter_agent()
