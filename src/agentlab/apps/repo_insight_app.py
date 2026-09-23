"""CLI for the P2 repo-insight coordinator: ``lab-repo-insight [session-mode]``."""

import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agentlab.agents.repo_insight_agent import make_repo_insight_agent
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.get_text_util import get_text
from agentlab.utils.session_util import resolve_session
from agentlab.utils.streaming_util import stream_agent_with_observability


def main() -> None:
    """Answer questions about this repository, streaming delegation progress."""
    load_dotenv()
    configure_utf8_stdout()
    session = resolve_session(
        sys.argv[1] if len(sys.argv) > 1 else None,
        default_thread_id="repo_insight_session_001",
        agent_factory=make_repo_insight_agent,
        app_name="repo_insight",
        cli_command_hint="uv run lab-repo-insight step[<index>]",
    )
    print("Ask questions about this repository. Type 'quit' to exit.")

    while True:
        try:
            question = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not question:
            continue
        if question.lower() in {"quit", "q", "exit"}:
            break

        result = stream_agent_with_observability(
            session.agent,
            {"messages": [HumanMessage(content=question)]},
            config=session.config,
        )
        last_message = result["last_message"]
        print(
            f"\n{get_text(last_message) if last_message else 'No final answer was produced.'}",
        )


if __name__ == "__main__":
    main()
