"""Application entry point — assembles and runs the agent."""

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from dotenv import load_dotenv

from models import lite_model
from prompts import build_system_prompt

load_dotenv()


def main() -> None:
    """Build and launch the deep agent."""
    system_prompt = build_system_prompt()

    # TODO: wire up real tools and namespace from config / CLI args
    tools: list = []
    namespace = ("", "", {})

    create_deep_agent(
        model=lite_model,
        system_prompt=system_prompt,
        tools=tools,
        backend=CompositeBackend(
            default=StateBackend(),
            routes={
                "/memories/": StoreBackend(namespace=namespace),
            },
        ),
    )


if __name__ == "__main__":
    main()
