"""P4 Interpreter Agent — executes and refines Python code in a stateful REPL."""

from data.sqlite_db import get_sqlite_checkpointer
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from models import llm_model
from prompts.agents import build_interpreter_agent_prompt
from tools.interpreter import python_interpreter


def make_interpreter_agent(checkpointer=None, tier: str = "medium"):
    """Build and return an autonomous Python Interpreter agent with explicit model tier."""
    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_interpreter_agent_prompt(),
        tools=[python_interpreter],
        checkpointer=checkpointer or InMemorySaver(),
    )



# Default ready-to-invoke agent instance for single-session use with SQLite persistence
interpreter_agent = make_interpreter_agent(checkpointer=get_sqlite_checkpointer())

