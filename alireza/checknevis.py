from dotenv import load_dotenv

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
from typing import Any
from deepagents.backends import LocalShellBackend
from prompts.agents import build_interpreter_agent_prompt
from models.registry import llm_model
from langchain_core.messages import HumanMessage
from utils import get_text
from deepagents import create_deep_agent
from utils.run_with_hitl import run_with_hitl


# def make_interpreter_agent(
#     tier: str = "medium",
#     backend: LocalShellBackend | None = None,
#     checkpointer: Any | None = None,
#     response_format: type | None = None,
#     hitl: bool = True,
# ):
#     DEFAULT_SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
#     if backend is None:
#         backend = LocalShellBackend(
#             root_dir=DEFAULT_SANDBOX_DIR,
#             virtual_mode=DEFAULT_VIRTUAL_MODE,
#             inherit_env=DEFAULT_INHERIT_ENV,
#             timeout=DEFAULT_EXECUTE_TIMEOUT,
#             max_output_bytes=DEFAULT_MAX_OUTPUT_BYTES,
#         )

#     interrupt_on: dict[str, bool | InterruptOnConfig] | None = (
#         {"execute": True} if hitl else None
#     )
#     checkpointer = InMemorySaver()

#     return create_deep_agent(
#         model=llm_model.get(tier),
#         system_prompt=build_interpreter_agent_prompt(),
#         backend=backend,
#         checkpointer=checkpointer,
#         response_format=response_format,
#         interrupt_on=interrupt_on,
#     )


# def run_interpreter_agent():
#     interpreter_agent = make_interpreter_agent()
#     config = {"configurable": {"thread_id": "interpreter_session_001"}}

#     while True:
#         try:
#             user_msg = input("\nsandbox> ").strip()
#         except (EOFError, KeyboardInterrupt):
#             print("\nExiting session.")
#             break

#         if not user_msg:
#             continue

#         if user_msg in ["q", "quit", "exit"]:
#             print("Session ended.")
#             break

#         result = run_with_hitl(
#             agent=interpreter_agent,
#             initial_input={
#                 "messages": [HumanMessage(content=user_msg)],
#             },
#             config=config,
#         )

#         print(f"\n{get_text(result["messages"][-1])}")


# if __name__ == "__main__":
#     run_interpreter_agent()
