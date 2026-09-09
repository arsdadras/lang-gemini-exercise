"""P4 Sandbox / Interpreter agent — executes and verifies Python scripts in an isolated workspace."""

from collections.abc import Sequence
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langchain.agents.middleware import InterruptOnConfig

from configs.interpreter_config import (
    DEFAULT_ARTIFACTS_DIR,
    DEFAULT_EXECUTE_TIMEOUT,
    DEFAULT_INHERIT_ENV,
    DEFAULT_INTERRUPT_TOOLS,
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_SANDBOX_DIR,
    DEFAULT_VIRTUAL_MODE,
)
from data.sqlite_db_data import get_sqlite_checkpointer
from models import llm_model
from prompts.agents_prompt import build_interpreter_agent_prompt
from utils.sandbox_util import SandboxBackend


def make_interpreter_agent(
    backend: LocalShellBackend | None = None,
    checkpointer: Any | None = None,
    tier: str = "medium",
    response_format: type | None = None,
    hitl: bool = True,
    interrupt_tools: Sequence[str] | dict[str, bool | InterruptOnConfig] | None = None,
):
    """Build and return an autonomous Sandbox / Interpreter agent."""
    DEFAULT_SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    if backend is None:
        backend = SandboxBackend(
            root_dir=DEFAULT_SANDBOX_DIR,
            virtual_mode=DEFAULT_VIRTUAL_MODE,
            inherit_env=DEFAULT_INHERIT_ENV,
            timeout=DEFAULT_EXECUTE_TIMEOUT,
            max_output_bytes=DEFAULT_MAX_OUTPUT_BYTES,
        )

    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None
    if hitl:
        if interrupt_tools is None:
            interrupt_on = {tool: True for tool in DEFAULT_INTERRUPT_TOOLS}
        elif isinstance(interrupt_tools, dict):
            interrupt_on = interrupt_tools
        else:
            interrupt_on = {tool: True for tool in interrupt_tools}

    if checkpointer is None:
        checkpointer = get_sqlite_checkpointer()

    agent = create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_interpreter_agent_prompt(),
        backend=backend,
        checkpointer=checkpointer,
        response_format=response_format,
        interrupt_on=interrupt_on,
    )
    # Expose configured interrupt tool names for introspection by callers/apps
    agent.interrupt_tools = list(interrupt_on.keys()) if interrupt_on else []
    return agent


# Ready-to-invoke default agent instance
interpreter_agent = make_interpreter_agent()
