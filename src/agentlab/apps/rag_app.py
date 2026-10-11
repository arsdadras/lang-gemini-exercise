"""CLI for the raw P2 RAG graph: ``lab-rag [session-mode]``.

Commands besides questions: ``history`` (list checkpoints, 0 = most recent) and
``replay <index>`` (resume from that checkpoint, re-running only what came after).
"""

import sys

from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

from agentlab.graphs.rag_graph import RagGraph, build_rag_graph
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.session_util import resolve_session


def _print_history(graph: RagGraph, config: RunnableConfig) -> None:
    for index, snapshot in enumerate(graph.get_state_history(config)):
        print(f"index {index}: next={snapshot.next}")


def _replay(graph: RagGraph, config: RunnableConfig, raw_index: str) -> None:
    try:
        snapshot = list(graph.get_state_history(config))[int(raw_index)]
    except (ValueError, IndexError):
        print("Invalid checkpoint index.")
        return
    result = graph.invoke(None, config=snapshot.config)
    print(f"\nFinal Answer:\n\n{result.get('answer')}")


def _ask(graph: RagGraph, config: RunnableConfig, question: str) -> None:
    # search_query and retries have no reducer: reset them for every new question.
    inputs = {"question": question, "search_query": question, "retries": 0}
    answer = None
    for update in graph.stream(inputs, config=config, stream_mode="updates"):
        for delta in update.values():
            if not delta:
                continue
            if "chunks" in delta:
                print(f"-> Kept {len(delta['chunks'])} chunk(s).")
            if "search_query" in delta:
                print(f"-> Rewritten query: {delta['search_query']}")
            answer = delta.get("answer", answer)
    print(f"\nFinal Answer:\n\n{answer}")


def main() -> None:
    """Run the RAG REPL."""
    load_dotenv()
    configure_utf8_stdout()
    session = resolve_session(
        sys.argv[1] if len(sys.argv) > 1 else None,
        default_thread_id="rag_session_001",
        agent_factory=build_rag_graph,
        app_name="rag",
        cli_command_hint="uv run lab-rag step[<index>]",
    )
    graph, config = session.agent, session.config
    print("Ask about the indexed corpus. Commands: history, replay <index>, quit.")

    while True:
        try:
            question = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        command = question.lower()
        if not question:
            continue
        if command in {"quit", "q", "exit"}:
            break
        if command == "history":
            _print_history(graph, config)
        elif command.startswith("replay "):
            _replay(graph, config, command.removeprefix("replay ").strip())
        else:
            _ask(graph, config, question)


if __name__ == "__main__":
    main()
