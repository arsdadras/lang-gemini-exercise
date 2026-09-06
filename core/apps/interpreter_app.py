"""Application entry point — interactive REPL loop for the P4 Sandbox / Interpreter agent."""

from dotenv import load_dotenv

load_dotenv()

import contextlib
import io
import sys

from agents.interpreter_agent import interpreter_agent, make_interpreter_agent
from configs.interpreter_config import DEFAULT_THREAD_ID
from langchain_core.messages import HumanMessage
from utils.get_text_util import get_text
from utils.run_with_hitl_util import run_with_hitl
from utils.sandbox_util import list_sandbox_artifacts
from utils.session_util import resolve_session


def main() -> None:
    """Launch the interactive REPL session for the P4 Sandbox / Interpreter agent."""
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else None
    session = resolve_session(
        raw_arg,
        default_thread_id=DEFAULT_THREAD_ID,
        default_agent=interpreter_agent,
        agent_factory=make_interpreter_agent,
        app_name="interpreter",
        cli_command_hint="python core/apps/interpreter_app.py step[<index>]",
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
    print("[Interpreter] P4 Sandbox / Interpreter Agent (DeepAgents)")
    print("Isolated workspace: out/sandbox/")
    print("Artifacts: out/sandbox/artifacts/")
    interrupt_tools = getattr(agent, "interrupt_tools", [])
    if interrupt_tools:
        tools_str = ", ".join(interrupt_tools)
        print(f"Governance: HITL approval required for: {tools_str}")
    else:
        print("Governance: Autonomous (No HITL approval required)")
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
                    "\n[Notice] Resuming pending interrupted action from previous session..."
                )
                result = run_with_hitl(
                    agent,
                    None,
                    config=config,
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

        prev_artifact_paths = {a["path"] for a in list_sandbox_artifacts()}

        result = run_with_hitl(
            agent,
            {"messages": [HumanMessage(content=user_prompt)]},
            config=config,
        )
        print(f"\n{get_text(result['messages'][-1])}")

        new_artifacts = [
            a for a in list_sandbox_artifacts() if a["path"] not in prev_artifact_paths
        ]
        if new_artifacts:
            print("\n[Generated Artifacts]:")
            for art in new_artifacts:
                size_kb = art["size_bytes"] / 1024
                print(f"  * {art['path']} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
