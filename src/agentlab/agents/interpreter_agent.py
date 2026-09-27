"""P4 Sandbox / Interpreter agent: writes, runs, and verifies scripts in an isolated workspace."""

from collections.abc import Sequence

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from agentlab.configs.interpreter_config import DEFAULT_INTERRUPT_TOOLS
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_interpreter_agent_prompt
from agentlab.utils.sandbox_util import make_sandbox_backend


def make_interpreter_agent(
    checkpointer: BaseCheckpointSaver | None = None,
    *,
    tier: str = "medium",  # paid tier only: tool-calling loop, not opensource/free (ADR-0014)
    backend: LocalShellBackend | None = None,
    interrupt_tools: Sequence[str] = DEFAULT_INTERRUPT_TOOLS,
    response_format: type[BaseModel] | None = None,
) -> CompiledStateGraph:
    """Build the interpreter agent.

    Args:
        checkpointer: State persistence; defaults to the shared SQLite checkpointer
            so pending approvals survive a restart.
        tier: Capability tier from the model catalog.
        backend: Shell and filesystem backend; defaults to the sandbox under ``out/sandbox``.
        interrupt_tools: Tools that pause for human approval. Pass ``()`` only when
            the caller owns the approval policy.
        response_format: Optional schema for a structured final answer.
    """
    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_interpreter_agent_prompt(),
        backend=backend if backend is not None else make_sandbox_backend(),
        checkpointer=checkpointer
        if checkpointer is not None
        else get_sqlite_checkpointer(),
        middleware=[make_model_fallback(tier)],
        interrupt_on={tool: True for tool in interrupt_tools} or None,
        response_format=response_format,
    )
