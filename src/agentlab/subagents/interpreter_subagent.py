"""Interpreter subagent: exposes an injected P4 interpreter agent to DeepAgents coordinators."""

from pathlib import Path
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable, RunnableLambda

from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.schemas.output.interpreter_output_schema import ArtifactMetadata
from agentlab.utils.get_text_util import get_text
from agentlab.utils.sandbox_util import (
    diff_sandbox_artifacts,
    snapshot_sandbox_artifacts,
)
from agentlab.utils.subagent_util import (
    new_delegation_config,
    task_text_from_state,
    to_subagent_reply,
)

DEFAULT_SUBAGENT_NAME = "code_interpreter"
DEFAULT_SUBAGENT_DESCRIPTION = (
    "Executes Python scripts, computational tasks, data processing, and shell commands "
    "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
    "markdown reports) in artifacts/ and self-corrects on errors."
)


def _describe(tag: str, artifact: ArtifactMetadata) -> str:
    size = f" ({artifact.size_bytes / 1024:.1f} KB)" if artifact.size_bytes else ""
    description = f" - {artifact.description}" if artifact.description else ""
    return (
        f"- `[{tag}]` `{artifact.path}`{size} [{artifact.artifact_type}]{description}"
    )


def make_interpreter_subagent(
    agent: Runnable,
    *,
    name: str = DEFAULT_SUBAGENT_NAME,
    description: str = DEFAULT_SUBAGENT_DESCRIPTION,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> CompiledSubAgent:
    """Wrap an interpreter agent as a ``CompiledSubAgent`` that reports its deliverables.

    The agent is injected (built by the caller, e.g. ``make_interpreter_agent``),
    so this module never depends on ``agents/``. After each delegation the
    adapter diffs ``artifacts/`` (new files and size/mtime changes) and appends
    the result, giving the coordinator exact file paths instead of a summary.
    """

    def run(state: dict[str, Any]) -> dict[str, Any]:
        before = snapshot_sandbox_artifacts(sandbox_dir)
        result = agent.invoke(
            {"messages": [HumanMessage(content=task_text_from_state(state))]},
            config=new_delegation_config(),
        )

        changes = diff_sandbox_artifacts(before, sandbox_dir)
        parts = [get_text(result["messages"][-1])]
        if changes:
            parts.append("\n\n### Deliverables Update:")
            parts.extend(_describe(tag.upper(), artifact) for tag, artifact in changes)
        return to_subagent_reply("\n".join(parts))

    return {"name": name, "description": description, "runnable": RunnableLambda(run)}
