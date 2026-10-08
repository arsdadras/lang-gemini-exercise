"""P4 Phase C coding coordinator: plans, then delegates research, sandboxed execution, and code review."""

from collections.abc import Sequence

from deepagents import CompiledSubAgent, SubAgent
from langchain.agents.middleware import TodoListMiddleware
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.interpreter_agent import make_interpreter_agent
from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_coding_coordinator_prompt
from agentlab.subagents.code_review_subagent import make_code_review_subagent
from agentlab.subagents.interpreter_subagent import make_interpreter_subagent
from agentlab.subagents.research_subagent import make_researcher_subagent
from agentlab.utils.deep_agent_util import create_deep_agent


def make_coding_coordinator_agent(
    checkpointer: BaseCheckpointSaver | None = None,
    *,
    tier: str = "low",  # paid tier only: tool-calling loop, not opensource/free (ADR-0014)
    interpreter_subagent: CompiledSubAgent | None = None,
    code_review_subagent: CompiledSubAgent | None = None,
    extra_subagents: Sequence[SubAgent | CompiledSubAgent] = (),
) -> CompiledStateGraph:
    """Build the coordinator over the P4 interpreter, P3 code review, and P1 researcher.

    The default interpreter subagent runs shell commands without per-command
    approval, because the coordinator's CLI loop has no handling for approvals
    raised inside a subagent yet (planned for P7 Phase B, Capstone I). Its shell still gets
    only the allow-listed environment, so it never sees API keys.
    """
    if interpreter_subagent is None:
        interpreter_subagent = make_interpreter_subagent(
            make_interpreter_agent(
                get_sqlite_checkpointer(checkpoint_db_path(DELEGATIONS_APP)),
                tier=tier,
                interrupt_tools=(),
                worker=True,
            ),
        )
    if code_review_subagent is None:
        code_review_subagent = make_code_review_subagent()

    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_coding_coordinator_prompt(),
        checkpointer=checkpointer
        if checkpointer is not None
        else get_sqlite_checkpointer(checkpoint_db_path("coding_coordinator")),
        subagents=[
            interpreter_subagent,
            code_review_subagent,
            make_researcher_subagent(),
            *extra_subagents,
        ],
        middleware=[*make_model_fallback(tier), TodoListMiddleware()],
    )
