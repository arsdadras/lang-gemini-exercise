"""P4 subagent adapter over ``workflows/interpreter_workflow.py`` (ADR-0033)."""

from pathlib import Path

from deepagents import CompiledSubAgent
from langgraph.graph.state import CompiledStateGraph

from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.workflows.interpreter_workflow import (
    DEFAULT_INTERPRETER_DESCRIPTION,
    InterpreterWorkflow,
)

DEFAULT_SUBAGENT_NAME = "code_interpreter"
DEFAULT_SUBAGENT_DESCRIPTION = DEFAULT_INTERPRETER_DESCRIPTION


def make_interpreter_subagent(
    agent: CompiledStateGraph | None = None,
    *,
    name: str = DEFAULT_SUBAGENT_NAME,
    description: str = DEFAULT_SUBAGENT_DESCRIPTION,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> CompiledSubAgent:
    """Wrap an interpreter agent as a ``CompiledSubAgent``; the envelope comes back as text."""
    return InterpreterWorkflow(agent, sandbox_dir=sandbox_dir).as_subagent(
        name=name,
        description=description,
    )
