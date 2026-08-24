"""Application entry point — assembles and runs the P1 research agent."""

from subagents import researcher_subagent
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from tools.search import web_search
from models.llm import lite_model
from prompts.research import build_research_prompt
from deepagents import create_deep_agent
from dotenv import load_dotenv
from output_schemas.research import ResearchReport
from middlewares.retry import retry_on_failure
from middlewares.hitl import search_approval
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


def main() -> None:
    """build and launch the p1 research agent"""
    agent = create_deep_agent(
        model=lite_model,
        system_prompt=build_research_prompt(),
        tools=[web_search],
        checkpointer=InMemorySaver(),
        response_format=ResearchReport,
        middleware=[retry_on_failure, search_approval],
        subagents=[researcher_subagent],
    )

    config = {"configurable": {"thread_id": "research_1b3"}}

    topic = input("what is the topic u want to research? ")

    result = agent.invoke({"messages": [HumanMessage(content=topic)]}, config)

    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0]
        for request in interrupt.value["action_requests"]:
            print(f"\n{request['description']}")
            print(f"Tool: {request['name']}")
            print(f"Args: {request['args']}")

        decision = input("Approve this web_search call? [y/n]: ").strip().lower()
        resume = {"decisions": [{"type": "approve" if decision == "y" else "reject"}]}
        result = agent.invoke(Command(resume=resume), config)

    report: ResearchReport = result["structured_response"]
    print(report.model_dump_json(indent=2))
    # for chunk in agent.stream(
    #     {
    #         "messages": [HumanMessage(content=topic)],
    #     },
    #     stream_mode="values",
    # ):
    #     chunk["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
