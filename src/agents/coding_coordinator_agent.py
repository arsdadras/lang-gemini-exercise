"""P4 Phase C Coding Coordinator Agent — orchestrates sandbox execution, code review, and technical research via specialized subagents."""

from collections.abc import Sequence
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents.middleware import TodoListMiddleware

from agents.interpreter_agent import make_interpreter_agent
from data.sqlite_db_data import get_sqlite_checkpointer
from middlewares.retry_middleware import retry_on_failure
from models import llm_model
from prompts.agents_prompt import build_coding_coordinator_prompt
from subagents import (
    make_code_review_subagent,
    make_interpreter_subagent,
    researcher_subagent,
)


def make_coding_coordinator_agent(
    *,
    tier: str = "medium",
    checkpointer: Any | None = None,
    interpreter_hitl: bool = False,
    interpreter_sub: CompiledSubAgent | None = None,
    code_review_sub: CompiledSubAgent | None = None,
    extra_subagents: Sequence[CompiledSubAgent] | None = None,
    enable_planning: bool = True,
) -> Any:
    """Builds the multi-agent Coding Coordinator DeepAgent.

    Pure Clean Architecture & Composition:
    Assembles P4 interpreter_subagent, P3 code_review_subagent, and P1 researcher_subagent
    via standardized Function Factories and Dependency Injection.

    Args:
        tier: Model capability tier ("low", "medium", "high").
        checkpointer: State checkpointer (defaults to SQLite persistent checkpointer).
        interpreter_hitl: Whether the underlying interpreter requires HITL approval on shell commands.
        interpreter_sub: Pre-built interpreter subagent (if customized sandbox_dir or mock is needed).
        code_review_sub: Pre-built code review subagent (if customized mock graph is needed).
        extra_subagents: Optional additional CompiledSubAgent instances to attach.

    Returns:
        Compiled DeepAgent runnable with multi-agent delegation capabilities.
    """
    if checkpointer is None:
        checkpointer = get_sqlite_checkpointer()

    if interpreter_sub is None:
        # Dependency Injection: Assemble the P4 interpreter agent
        interpreter = make_interpreter_agent(hitl=interpreter_hitl, tier=tier)
        interpreter_sub = make_interpreter_subagent(agent=interpreter)

    if code_review_sub is None:
        # Dependency Injection: Assemble the P3 code review subagent
        code_review_sub = make_code_review_subagent()

    subagents: list[CompiledSubAgent] = [
        interpreter_sub,
        code_review_sub,
        researcher_subagent,
    ]
    if extra_subagents:
        subagents.extend(extra_subagents)

    middleware = [retry_on_failure(tier)]
    if enable_planning:
        middleware.append(TodoListMiddleware())

    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_coding_coordinator_prompt(),
        checkpointer=checkpointer,
        subagents=subagents,
        middleware=middleware,
    )


# Ready-to-invoke default agent instance
coding_coordinator_agent = make_coding_coordinator_agent()
