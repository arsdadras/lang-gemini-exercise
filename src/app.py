"""Application entry point — assembles and runs the agent."""

from deepagents import create_deep_agent
from dotenv import load_dotenv

from models import flash_model
from prompts import build_system_prompt
from tools import web_search

load_dotenv()


def main() -> None:
    """Build and launch the P1 research agent (Phase A baseline)."""
    system_prompt = build_system_prompt(
        assistant_name="Research Agent",
        role="a focused web research assistant",
        domain="open-domain web research and source-grounded reporting",
        mission=(
            "Given a topic, search the web and produce a structured, "
            "clearly cited report. Never fabricate facts or sources."
        ),
        tools=(
            "Use `web_search` for any factual, current, or research "
            "question. Call it as many times as needed to cover distinct "
            "sub-questions before writing the final report."
        ),
        output_format=(
            "Structure the final answer with short headers, use bullet "
            "points for parallel facts, and cite each claim with the "
            "source URL it came from."
        ),
        constraints=(
            "- Never state a fact you did not retrieve via web_search.\n"
            "- If search results conflict, say so explicitly.\n"
            "- Keep the report focused on the user's actual topic."
        ),
    )

    agent = create_deep_agent(
        model=flash_model,
        system_prompt=system_prompt,
        tools=[web_search],
    )

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": input("Research topic: ")}]},
        stream_mode="values",
    ):
        last = chunk["messages"][-1]
        last.pretty_print()


if __name__ == "__main__":
    main()
