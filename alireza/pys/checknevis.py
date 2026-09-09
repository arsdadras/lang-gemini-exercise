from dotenv import load_dotenv
from langgraph.checkpoint.base import BaseCheckpointSaver

from agents import make_interpreter_agent
from data import get_sqlite_checkpointer
from middlewares import retry_on_failure
from prompts import build_coding_coordinator_prompt
from subagents import make_interpreter_subagent, code_review_subagent, researcher_subagent

load_dotenv()

from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import InterruptOnConfig
from configs.interpreter_config import (
    DEFAULT_EXECUTE_TIMEOUT,
    DEFAULT_INHERIT_ENV,
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_SANDBOX_DIR,
    DEFAULT_VIRTUAL_MODE,
)
from typing import Any, Sequence
from deepagents.backends import LocalShellBackend
from prompts.agents_prompt import build_interpreter_agent_prompt
from models.registry_model import llm_model
from langchain_core.messages import HumanMessage
from utils import get_text
from deepagents import create_deep_agent, CompiledSubAgent
from utils.run_with_hitl_util import run_with_hitl

def make_coordinator_agent(
        *,
        tier: str = "low",
        checkpointer: BaseCheckpointSaver[Any]|None = None,
        interpreter_hitl: bool = False,
        interpreter_sbag: CompiledSubAgent|None = None,
        extra_sbags: Sequence[CompiledSubAgent]|None = None,
):

    """
    Create a coordinator agent that manages the execution of sub-agents.

    Args:
        tier (str): The tier of the agent, which can affect its capabilities.
        checkpointer (BaseCheckpointSaver[Any]): A checkpoint saver for saving the state of the agent.
        interpreter_hitl (bool): Whether to enable human-in-the-loop (HITL)
        interpreter_sbag (CompiledSubAgent): The compiled sub-agent for the interpreter.
        extra_sbag (Sequence[CompiledSubAgent]): A sequence of additional compiled sub-agents.
    Returns:
        A coordinator agent that can manage the execution of sub-agents.
    """


    if checkpointer is None:
        checkpointer = get_sqlite_checkpointer()

    if interpreter_sbag is None:
        interpreter = make_interpreter_agent(hitl=interpreter_hitl)
        interpreter_sbag = make_interpreter_subagent(interpreter)

    subagents=[
        interpreter_sbag,
        code_review_subagent,
        researcher_subagent
    ]

    if extra_sbags is not None:
        subagents.extend(extra_sbags)

    return create_deep_agent(
        name="coordinator",
        model=llm_model(tier=tier),
        system_prompt=build_coding_coordinator_prompt(),
        subagents=subagents,
        checkpointer=checkpointer,
        middleware=[retry_on_failure(tier)]
    )


coding_coordinator = make_coordinator_agent(tier="low", interpreter_hitl=False)