"""CLI for the P4 sandbox interpreter: ``lab-interpreter [session-mode]``."""

import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agentlab.agents.interpreter_agent import make_interpreter_agent
from agentlab.configs.interpreter_config import (
    DEFAULT_INTERRUPT_TOOLS,
    DEFAULT_THREAD_ID,
)
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.get_text_util import get_text
from agentlab.utils.run_with_hitl_util import run_with_hitl
from agentlab.utils.sandbox_util import (
    diff_sandbox_deliverables,
    snapshot_sandbox_deliverables,
)
from agentlab.utils.session_util import ResolvedSession, resolve_session


def _print_banner(session: ResolvedSession) -> None:
    print("=" * 60)
    print("[Interpreter] P4 Sandbox / Interpreter Agent")
    print("Workspace: out/sandbox/   Deliverables: out/sandbox/deliverables/")
    print(f"Approval required for: {', '.join(DEFAULT_INTERRUPT_TOOLS)}")
    print(
        "Persistence: "
        + ("in-memory (secret mode)" if session.is_secret else "SQLite checkpoints"),
    )
    print(f"Session: {session.mode_name} | thread {session.thread_id}")
    print("Type 'quit', 'exit' or 'q' to end the session.")
    print("=" * 60)


def main() -> None:
    """Run the interpreter REPL, resolving approvals over the CLI."""
    load_dotenv()
    configure_utf8_stdout()
    session = resolve_session(
        sys.argv[1] if len(sys.argv) > 1 else None,
        default_thread_id=DEFAULT_THREAD_ID,
        agent_factory=make_interpreter_agent,
        app_name="interpreter",
        cli_command_hint="uv run lab-interpreter step[<index>]",
    )
    agent, config = session.agent, session.config
    _print_banner(session)

    # A previous process may have exited while an approval was pending.
    if not session.is_secret and agent.get_state(config).next:
        print("\n[Notice] Resuming an action left pending by a previous session...")
        result = run_with_hitl(agent, None, config)
        if result.get("messages"):
            print(f"\n{get_text(result['messages'][-1])}")

    while True:
        try:
            prompt = input("\nsandbox> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting session.")
            break
        if not prompt:
            continue
        if prompt.lower() in {"quit", "q", "exit"}:
            break

        before = snapshot_sandbox_deliverables()
        result = run_with_hitl(
            agent,
            {"messages": [HumanMessage(content=prompt)]},
            config,
        )
        print(f"\n{get_text(result['messages'][-1])}")

        changes = diff_sandbox_deliverables(before)
        if changes:
            print("\n[Generated Deliverables]:")
            for tag, deliverable in changes:
                size_kb = (deliverable.size_bytes or 0) / 1024
                print(
                    f"  * [{tag.upper()}] {deliverable.path} ({size_kb:.1f} KB) [{deliverable.deliverable_type}]",
                )


if __name__ == "__main__":
    main()
