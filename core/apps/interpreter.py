"""Application entry point — interactive REPL loop for the P4 Sandbox / Interpreter agent."""

from dotenv import load_dotenv

load_dotenv()

from agents.interpreter import interpreter_agent
from langchain_core.messages import HumanMessage
from utils.get_text import get_text


def main() -> None:
    """Launch the interactive REPL session for the P4 Sandbox / Interpreter agent."""
    agent = interpreter_agent
    config = {"configurable": {"thread_id": "interpreter_session_001"}}

    print("=" * 60)
    print("💻 P4 Sandbox / Interpreter Agent (DeepAgents)")
    print("Isolated workspace: out/sandbox/")
    print("Type 'quit', 'exit' or 'q' to end session.")
    print("=" * 60)

    while True:
        try:
            user_prompt = input("\nsandbox> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting session.")
            break

        if not user_prompt:
            continue

        if user_prompt.lower() in {"quit", "q", "exit"}:
            print("Session ended.")
            break

        result = agent.invoke(
            {"messages": [HumanMessage(content=user_prompt)]},
            config=config,
        )
        print(f"\n{get_text(result['messages'][-1])}")


if __name__ == "__main__":
    main()
