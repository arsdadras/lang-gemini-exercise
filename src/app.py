"""Application entry point — assembles and runs the P1 research agent."""

from deepagents import create_deep_agent
from dotenv import load_dotenv

from middleware import retry_on_failure
from models import flash_model
from prompts import RESEARCH_SYSTEM_PROMPT
from schemas import ResearchReport
from tools import web_search

load_dotenv()


def main() -> None:
    """Build and launch the P1 research agent (Phase B: structured output + middleware)."""
    agent = create_deep_agent(
        model=flash_model,
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        tools=[web_search],
        response_format=ResearchReport,
        middleware=[retry_on_failure],
    )

    topic = input("Research topic: ")
    result = agent.invoke({"messages": [{"role": "user", "content": topic}]})

    report: ResearchReport = result["structured_response"]
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
