"""P4 Interpreter Agent — executes and refines Python code in a stateful REPL."""

from data.sqlite_db import get_sqlite_checkpointer
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from models import llm_model
from prompts.agents import build_interpreter_agent_prompt
from tools.file_ops import list_files, read_file, write_file
from tools.interpreter import python_interpreter


def make_interpreter_agent(checkpointer=None, tier: str = "medium", response_format=None):
    """Build and return an autonomous Python Interpreter agent with explicit model tier."""
    kwargs = {}
    if response_format is not None:
        kwargs["response_format"] = response_format

    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_interpreter_agent_prompt(),
        tools=[python_interpreter, write_file, read_file, list_files],
        checkpointer=checkpointer or InMemorySaver(),
        **kwargs,
    )


# Default ready-to-invoke agent instance for single-session use with SQLite persistence
interpreter_agent = make_interpreter_agent(checkpointer=get_sqlite_checkpointer())
