"""Application entry point — assembles and runs the P1 research agent."""

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from middleware import retry_on_failure, search_approval
from models import flash_model
from prompts import RESEARCH_SYSTEM_PROMPT
from schemas import ResearchReport
from tools import web_search

load_dotenv()


def main() -> None:
    """Build and launch the P1 research agent (Phase B: full stack)."""
    agent = create_deep_agent(
        model=flash_model,
        system_prompt=RESEARCH_SYSTEM_PROMPT,
        tools=[web_search],
        response_format=ResearchReport,
        middleware=[retry_on_failure, search_approval],
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": "research-session-1"}}
    topic = input("Research topic: ")
    result = agent.invoke({"messages": [{"role": "user", "content": topic}]}, config)

    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0]
        for request in interrupt.value["action_requests"]:
            print(f"\n{request['description']}")
            print(f"Tool: {request['tool_call']['name']}")
            print(f"Args: {request['tool_call']['args']}")

        decision = input("Approve this web_search call? [y/n]: ").strip().lower()
        resume = {"decisions": [{"type": "approve" if decision == "y" else "reject"}]}
        result = agent.invoke(Command(resume=resume), config)

    report: ResearchReport = result["structured_response"]
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
