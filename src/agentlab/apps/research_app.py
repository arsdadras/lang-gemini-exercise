"""CLI for the P1 web researcher: ``lab-research [session-mode]``."""

import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agentlab.agents.web_researcher_agent import make_web_researcher_agent
from agentlab.output_schemas.research_output_schema import ResearchReport
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.run_with_hitl_util import run_with_hitl
from agentlab.utils.session_util import resolve_session


def main() -> None:
    """Research one topic, approving each web search, and print the structured report."""
    load_dotenv()
    configure_utf8_stdout()
    session = resolve_session(
        sys.argv[1] if len(sys.argv) > 1 else None,
        default_thread_id="research_session_001",
        agent_factory=make_web_researcher_agent,
        app_name="research",
        cli_command_hint="uv run lab-research step[<index>]",
    )

    topic = input("Topic to research: ").strip()
    if not topic:
        print("No topic given.")
        return

    result = run_with_hitl(
        session.agent,
        {"messages": [HumanMessage(content=topic)]},
        session.config,
        assistant_prompt="Approve this web_search call? [y/n]: ",
    )
    report: ResearchReport = result["structured_response"]
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
