"""CLI for the P4 multi-agent coding coordinator: ``lab-coordinator [session-mode]``."""

import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agentlab.agents.coordinators.coding_coordinator_agent import (
    make_coding_coordinator_agent,
)
from agentlab.configs.coordinator_config import DEFAULT_COORDINATOR_THREAD_ID
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.get_text_util import get_text
from agentlab.utils.session_util import ResolvedSession, resolve_session
from agentlab.utils.streaming_util import stream_agent_with_observability


def _print_banner(session: ResolvedSession) -> None:
    print("=" * 60)
    print("[Coordinator] P4 Multi-Agent Coding Coordinator")
    print(
        "Subagents: code_interpreter (P4), code_review_subagent (P3), researcher (P1)",
    )
    print("Sandbox: out/sandbox/ -- shell commands run WITHOUT per-command approval;")
    print("         the shell environment is allow-listed and holds no API keys.")
    print(
        "Persistence: "
        + ("in-memory (secret mode)" if session.is_secret else "SQLite checkpoints"),
    )
    print(f"Session: {session.mode_name} | thread {session.thread_id}")
    print("Type 'quit', 'exit' or 'q' to end the session.")
    print("=" * 60)


def main() -> None:
    """Run the coordinator REPL with streaming progress."""
    load_dotenv()
    configure_utf8_stdout()
    session = resolve_session(
        sys.argv[1] if len(sys.argv) > 1 else None,
        default_thread_id=DEFAULT_COORDINATOR_THREAD_ID,
        agent_factory=make_coding_coordinator_agent,
        app_name="coding_coordinator",
        cli_command_hint="uv run lab-coordinator step[<index>]",
    )
    _print_banner(session)

    while True:
        try:
            user_input = input("\n[User]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession terminated.")
            break
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            break

        result = stream_agent_with_observability(
            session.agent,
            {"messages": [HumanMessage(content=user_input)]},
            config=session.config,
        )
        last_message = result["last_message"]
        answer = (
            get_text(last_message) if last_message else "No final answer was produced."
        )
        print(f"\n[Coordinator Response]:\n{answer}")


if __name__ == "__main__":
    main()
