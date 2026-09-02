"""Application entry point — runs the P1 web-researcher agent."""

from agents.web_researcher import web_researcher_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from output_schemas.research import ResearchReport
from utils.run_with_hitl import run_with_hitl

load_dotenv()


def main() -> None:
    """Launch the P1 web-researcher agent."""
    agent = web_researcher_agent

    config = {"configurable": {"thread_id": "research_1b3"}}

    topic = input("what is the topic u want to research? ")

    result = run_with_hitl(
        agent,
        {"messages": [HumanMessage(content=topic)]},
        config,
        assistant_prompt="Approve this web_search call? [y/n]: ",
    )

    report: ResearchReport = result["structured_response"]
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
