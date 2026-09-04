"""Application entry point — runs the P2 repo-insight coordinator agent."""

from agents.repo_insight_agent import repo_insight_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from utils.get_text_util import get_text

load_dotenv()


def main() -> None:
    """Launch the P2 repo-insight coordinator agent."""
    agent = repo_insight_agent
    config = {"configurable": {"thread_id": "repo_insight_session_001"}}

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
