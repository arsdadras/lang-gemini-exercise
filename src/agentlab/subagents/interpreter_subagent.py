"""P4 subagent adapter over ``workflows/interpreter_workflow.py`` (ADR-0033)."""

from pathlib import Path
from typing import Any

from deepagents import CompiledSubAgent

from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.utils.subagent_util import specialist_subagent
from agentlab.workflows.interpreter_workflow import (
    DEFAULT_INTERPRETER_DESCRIPTION,
    INTERPRETER_SPECIALIST,
    INTERPRETER_SPECIALIST_SPEC,
    render_interpreter_report,
    run_interpreter,
)

DEFAULT_SUBAGENT_NAME = "code_interpreter"
DEFAULT_SUBAGENT_DESCRIPTION = DEFAULT_INTERPRETER_DESCRIPTION


def make_interpreter_subagent(
    agent: Any = None,
    *,
    name: str = DEFAULT_SUBAGENT_NAME,
    description: str = DEFAULT_SUBAGENT_DESCRIPTION,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> CompiledSubAgent:
    """Wrap an interpreter agent as a ``CompiledSubAgent``; the envelope comes back as text."""
    return specialist_subagent(
        name,
        description,
        lambda task: run_interpreter(task, agent=agent, sandbox_dir=sandbox_dir),
        render=render_interpreter_report,
    )


__all__ = [
    "DEFAULT_SUBAGENT_DESCRIPTION",
    "DEFAULT_SUBAGENT_NAME",
    "INTERPRETER_SPECIALIST",
    "INTERPRETER_SPECIALIST_SPEC",
    "make_interpreter_subagent",
    "render_interpreter_report",
    "run_interpreter",
]
