"""Application entry point — assembles and runs the P1 research agent."""

from deepagents import create_deep_agent
from dotenv import load_dotenv

from models import flash_model
from prompts import build_research_prompt
from tools import web_search

load_dotenv()


def main() -> None:
    """Build and launch the P1 research agent."""
    agent = create_deep_agent(
        model=flash_model,
        system_prompt=build_research_prompt(),
        tools=[web_search],
    )

    topic = input("Research topic: ")
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": topic}]},
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
