from dotenv import load_dotenv

load_dotenv()

import sys

from agents.web_researcher_agent import web_researcher_agent
from langchain_core.messages import HumanMessage
from output_schemas.research_output_schema import ResearchReport
from utils.run_with_hitl_util import run_with_hitl
from utils.session_util import resolve_session


def main() -> None:
    """Launch the P1 web-researcher agent."""
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else None
    session = resolve_session(
        raw_arg,
        default_thread_id="research_1b3",
        default_agent=web_researcher_agent,
        app_name="research",
    )
    agent = session.agent
    config = session.config

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
