from dotenv import load_dotenv

load_dotenv()

import sys

from langchain_core.messages import HumanMessage

from agents.repo_insight_agent import repo_insight_agent
from utils.get_text_util import get_text
from utils.session_util import resolve_session


def main() -> None:
    """Launch the P2 repo-insight coordinator agent."""
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else None
    session = resolve_session(
        raw_arg,
        default_thread_id="repo_insight_session_001",
        default_agent=repo_insight_agent,
        app_name="repo_insight",
    )
    agent = session.agent
    config = session.config

    print("Ask questions about this repo. Type 'quit' to exit.")

    while True:
        question = input("\n> ")
        if question.strip().lower() in {"quit", "q", "exit"}:
            break

        result = agent.invoke(
            {"messages": [HumanMessage(content=question)]},
            config=config,
        )
        print(f"\n{get_text(result['messages'][-1])}")


if __name__ == "__main__":
    main()
