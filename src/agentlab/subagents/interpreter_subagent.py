"""Interpreter subagent: exposes an injected P4 interpreter agent to DeepAgents coordinators."""

import uuid
from pathlib import Path
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda

from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.output_schemas.interpreter_output_schema import ArtifactMetadata
from agentlab.utils.get_text_util import get_text
from agentlab.utils.sandbox_util import list_sandbox_artifacts

DEFAULT_SUBAGENT_NAME = "code_interpreter"
DEFAULT_SUBAGENT_DESCRIPTION = (
    "Executes Python scripts, computational tasks, data processing, and shell commands "
    "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
    "markdown reports) in artifacts/ and self-corrects on errors."
)


def _describe(tag: str, artifact: ArtifactMetadata) -> str:
    size = f" ({artifact.size_bytes / 1024:.1f} KB)" if artifact.size_bytes else ""
    description = f" - {artifact.description}" if artifact.description else ""
    return f"- `[{tag}]` `{artifact.path}`{size} [{artifact.artifact_type}]{description}"


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
        before = {a.path: (a.size_bytes, a.modified_at) for a in list_sandbox_artifacts(sandbox_dir)}
        config: RunnableConfig = {"configurable": {"thread_id": str(uuid.uuid4())}}
        result = agent.invoke(
            {"messages": [HumanMessage(content=get_text(state["messages"][-1]))]},
            config=config,
        )

        updates: list[str] = []
        for artifact in list_sandbox_artifacts(sandbox_dir):
            previous = before.get(artifact.path)
            if previous is None:
                updates.append(_describe("NEW", artifact))
            elif previous != (artifact.size_bytes, artifact.modified_at):
                updates.append(_describe("MODIFIED", artifact))

        parts = [get_text(result["messages"][-1])]
        if updates:
            parts.extend(["\n\n### Deliverables Update:", *updates])
        return {"messages": [AIMessage(content="\n".join(parts))]}

    return {"name": name, "description": description, "runnable": RunnableLambda(run)}
