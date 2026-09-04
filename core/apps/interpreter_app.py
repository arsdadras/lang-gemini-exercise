"""Application entry point — interactive REPL loop for the P4 Sandbox / Interpreter agent."""

from dotenv import load_dotenv

load_dotenv()

import contextlib
import io
import re
import sys
import uuid
from typing import Any

from agents.interpreter_agent import interpreter_agent, make_interpreter_agent
from configs.interpreter_config import DEFAULT_THREAD_ID
from data.sqlite_db_data import get_recent_threads
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from utils.get_text_util import get_text
from utils.run_with_hitl_util import run_with_hitl


def resolve_session(raw_arg: str | None) -> tuple[Any, str, str, bool]:
    """Resolve CLI argument into (agent, thread_id, mode_name, is_secret)."""
    arg = (raw_arg or "").strip()

    if not arg or arg.lower() == "default":
        return interpreter_agent, DEFAULT_THREAD_ID, "default", False

    if arg.lower() == "new":
        tid = f"interpreter_{uuid.uuid4().hex[:6]}"
        return interpreter_agent, tid, "new", False

    if arg.lower() == "secret":
        tid = f"secret_{uuid.uuid4().hex[:6]}"
        secret_agent = make_interpreter_agent(checkpointer=InMemorySaver())
        return secret_agent, tid, "secret (in-memory)", True

    if arg.lower() in {"list", "history"}:
        threads = get_recent_threads(limit=15)
        if not threads:
            print("No recorded sessions found in database.")
        else:
            print("=" * 60)
            print("Recorded Sessions (0-indexed, most recent first):")
            for i, tid in enumerate(threads):
                tag = " (latest)" if i == 0 else ""
                print(f"  step[{i}]: {tid}{tag}")
            print("=" * 60)
            print("To resume: python core/apps/interpreter_app.py step[<index>]")
        sys.exit(0)

    if arg.lower() == "resume":
        threads = get_recent_threads()
        if threads:
            return interpreter_agent, threads[0], f"resume ({threads[0]})", False
        print("[Notice] No previous sessions found in database. Using default.")
        return interpreter_agent, DEFAULT_THREAD_ID, "default (no prior sessions)", False

    step_match = re.match(r"^step\[?(\d+)\]?$", arg, re.IGNORECASE)
    if step_match:
        idx = int(step_match.group(1))
        threads = get_recent_threads()
        if not threads:
            print("[Error] No recorded sessions found in database.")
            sys.exit(1)
        if 0 <= idx < len(threads):
            selected = threads[idx]
            return interpreter_agent, selected, f"step[{idx}] ({selected})", False

        print(f"[Error] Index {idx} out of range. Available: step[0] to step[{len(threads) - 1}].")
        print("Recent sessions:")
        for i, tid in enumerate(threads[:5]):
            print(f"  step[{i}]: {tid}")
        sys.exit(1)

    # Custom named thread
    return interpreter_agent, arg, f"custom ({arg})", False


def main() -> None:
    """Launch the interactive REPL session for the P4 Sandbox / Interpreter agent."""
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else None
    agent, thread_id, mode_name, is_secret = resolve_session(raw_arg)
    config = {"configurable": {"thread_id": thread_id}}

    if hasattr(sys.stdout, "reconfigure"):
        with contextlib.suppress(AttributeError, io.UnsupportedOperation):
            sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("[Interpreter] P4 Sandbox / Interpreter Agent (DeepAgents)")
    print("Isolated workspace: out/sandbox/")
    print("Governance: HITL approval required for shell execution")
    if is_secret:
        print("Persistence: Secret Mode (In-Memory only — NOT saved to DB)")
    else:
        print("Persistence: SQLite checkpointer (checkpoints.db)")
    print(f"Session Mode: {mode_name}")
    print(f"Session Thread: {thread_id}")
    print("Type 'quit', 'exit' or 'q' to end session.")
    print("=" * 60)

    # Startup recovery: resolve any pending interrupt before accepting fresh input
    if not is_secret:
        state = agent.get_state(config)
        if state.next:
            pending_interrupts = (
                [i for t in state.tasks for i in t.interrupts] if state.tasks else []
            )
            if pending_interrupts:
                print(
                    "\n[Notice] Resuming pending interrupted shell execution from previous session..."
                )
                result = run_with_hitl(
                    agent,
                    None,
                    config=config,
                    assistant_prompt="\nApprove shell command execution? [y/n]: ",
                )
                if result.get("messages"):
                    print(f"\n{get_text(result['messages'][-1])}")

    while True:
        try:
            user_prompt = input("\nsandbox> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting session.")
            break

        if not user_prompt:
            continue

        if user_prompt.lower() in {"quit", "q", "exit"}:
            print("Session ended.")
            break

        result = run_with_hitl(
            agent,
            {"messages": [HumanMessage(content=user_prompt)]},
            config=config,
            assistant_prompt="\nApprove shell command execution? [y/n]: ",
        )
        print(f"\n{get_text(result['messages'][-1])}")


if __name__ == "__main__":
    main()
