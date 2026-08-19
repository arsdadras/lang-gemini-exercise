"""Application entry point — assembles and runs the P1 research agent."""

from models import luna_model
from langchain_core.messages import HumanMessage
from tools.search import web_search
from models.llm import lite_model, flash_model
from prompts.research import build_research_prompt
from deepagents import create_deep_agent
from dotenv import load_dotenv
import os

load_dotenv()


def main() -> None:
    """build and luch the p1 research agent"""
    agent = create_deep_agent(
        model=luna_model,
        system_prompt=build_research_prompt(),
        tools=[web_search],
    )

    topic = input("what is the topic u want to research? ")

    for chunk in agent.stream(
        {
            "messages": [HumanMessage(content=topic)],
        },
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
