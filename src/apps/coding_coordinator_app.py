"""Application entry point — interactive REPL loop for the P4 Phase C Multi-Agent Coding Coordinator."""

from dotenv import load_dotenv

load_dotenv()

import contextlib
import io
import sys

from langchain_core.messages import HumanMessage

from agents.coding_coordinator_agent import (
    coding_coordinator_agent,
    make_coding_coordinator_agent,
)
from configs.coordinator_config import DEFAULT_COORDINATOR_THREAD_ID
from utils.get_text_util import get_text
from utils.session_util import resolve_session


def main() -> None:
    """Launch the interactive REPL session for the Coding Coordinator."""
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else None
    session = resolve_session(
        raw_arg,
        default_thread_id=DEFAULT_COORDINATOR_THREAD_ID,
        default_agent=coding_coordinator_agent,
        agent_factory=make_coding_coordinator_agent,
        app_name="coding_coordinator",
        cli_command_hint="python core/apps/coding_coordinator_app.py step[<index>]",
    )
    agent = session.agent
    thread_id = session.thread_id
    mode_name = session.mode_name
    is_secret = session.is_secret
    config = session.config

    if hasattr(sys.stdout, "reconfigure"):
        with contextlib.suppress(AttributeError, io.UnsupportedOperation):
            sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("[Coordinator] P4 Phase C Multi-Agent Coding Coordinator")
    print("Orchestrates: code_interpreter (P4), code_review (P3), researcher (P1)")
    print("Sandbox Workspace: out/sandbox/")
    if is_secret:
        print("Persistence: Secret Mode (In-Memory only — NOT saved to DB)")
    else:
        print("Persistence: SQLite checkpointer (checkpoints.db)")
    print(f"Session Mode: {mode_name}")
    print(f"Session Thread: {thread_id}")
    print("Type 'quit', 'exit' or 'q' to end session.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n[User]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession terminated.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break

        print("\n[Coordinator is thinking & orchestrating subagents...]")
        result = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )
        output_text = get_text(result["messages"][-1])
        print(f"\n[Coordinator Response]:\n{output_text}")


if __name__ == "__main__":
    main()
