"""Interpreter Subagent — wraps an injected P4 Sandbox/Interpreter agent for delegation from DeepAgents multi-agent coordinators.

Follows Pure Dependency Injection: does NOT instantiate or import from core/agents/,
preventing layer inversion and circular import issues.
"""

import uuid
from pathlib import Path
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda

from output_schemas.interpreter_output_schema import ArtifactMetadata
from utils.get_text_util import get_text
from utils.sandbox_util import list_sandbox_artifacts

DEFAULT_SUBAGENT_NAME = "code_interpreter"
DEFAULT_SUBAGENT_DESCRIPTION = (
    "Executes Python scripts, computational tasks, data processing, and shell commands "
    "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
    "markdown reports) in artifacts/ and self-corrects on errors."
)


def make_interpreter_subagent(
    agent: Runnable,
    *,
    name: str = DEFAULT_SUBAGENT_NAME,
    description: str = DEFAULT_SUBAGENT_DESCRIPTION,
    sandbox_dir: Path | None = None,
) -> CompiledSubAgent:
    """Wraps an existing compiled interpreter agent into a coordinator-compatible subagent.

    Pure Dependency Injection:
    Receives any Runnable (real compiled agent or a test mock) and optional sandbox_dir
    from the caller layer (src/agents/ or src/apps/), ensuring modular layering without coupling.

    Args:
        agent: Compiled agent runnable (e.g. from make_interpreter_agent(hitl=False)).
        name: Subagent tool name exposed to the coordinator LLM.
        description: Delegation instructions helping the coordinator route tasks.
        sandbox_dir: Optional sandbox root path for multi-tenant or test workspace isolation.

    Returns:
        CompiledSubAgent TypedDict ready for registration with create_deep_agent(subagents=[...]).
    """

    def _run_interpreter_subagent(state: dict[str, Any]) -> dict[str, Any]:
        """Adapter closure: invokes the injected agent and tracks created/modified deliverables."""
        task_text = get_text(state["messages"][-1])
        thread_id = str(uuid.uuid4())
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        # 1. Snapshot existing artifacts prior to execution: path -> (size_bytes, modified_at)
        prev_artifacts = {
            a.path: (a.size_bytes, a.modified_at)
            for a in list_sandbox_artifacts(sandbox_dir=sandbox_dir)
        }

        # 2. Invoke the injected agent Runnable
        result = agent.invoke(
            {"messages": [HumanMessage(content=task_text)]},
            config=config,
        )

        output_text = get_text(result["messages"][-1])

        # 3. Detect new deliverables and modified deliverables
        current_artifacts = list_sandbox_artifacts(sandbox_dir=sandbox_dir)
        new_artifacts: list[ArtifactMetadata] = []
        modified_artifacts: list[ArtifactMetadata] = []

        for a in current_artifacts:
            if a.path not in prev_artifacts:
                new_artifacts.append(a)
            else:
                prev_size, prev_mtime = prev_artifacts[a.path]
                has_size_changed = a.size_bytes != prev_size
                has_time_changed = (
                    a.modified_at is not None
                    and prev_mtime is not None
                    and a.modified_at > prev_mtime
                )
                if has_size_changed or has_time_changed:
                    modified_artifacts.append(a)

        parts = [output_text]
        if new_artifacts or modified_artifacts:
            parts.append("\n\n### Deliverables Update:")
            for artifact in new_artifacts:
                size_kb = (
                    f" ({artifact.size_bytes / 1024:.1f} KB)"
                    if artifact.size_bytes
                    else ""
                )
                desc = f" - {artifact.description}" if artifact.description else ""
                parts.append(
                    f"- `[NEW]` `{artifact.path}`{size_kb} [{artifact.artifact_type}]{desc}"
                )

            for artifact in modified_artifacts:
                size_kb = (
                    f" ({artifact.size_bytes / 1024:.1f} KB)"
                    if artifact.size_bytes
                    else ""
                )
                desc = f" - {artifact.description}" if artifact.description else ""
                parts.append(
                    f"- `[MODIFIED]` `{artifact.path}`{size_kb} [{artifact.artifact_type}]{desc}"
                )

        return {
            "messages": [AIMessage(content="\n".join(parts))],
            "thread_id": thread_id,
        }

    return {
        "name": name,
        "description": description,
        "runnable": RunnableLambda(_run_interpreter_subagent),
    }
