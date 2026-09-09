import sys

from dotenv import load_dotenv

from graphs.rag_graph import build_rag_graph
from utils.session_util import resolve_session

load_dotenv()


def main() -> None:
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else None
    session = resolve_session(
        raw_arg,
        default_thread_id="rag_session_001",
        agent_factory=lambda _saver: build_rag_graph(),
        app_name="rag",
    )
    graph = session.agent
    config = session.config

    print("Ask questions about the indexed corpus. Type 'quit' to exit.")

    while True:
        question = input("\n> ")
        if question.strip().lower() in {"quit", "q", "exit"}:
            break

        if question.strip().lower() == "history":
            for i, snap in enumerate(graph.get_state_history(config)):
                print(f"index {i}: next={snap.next}")
            continue

        if question.strip().lower().startswith("replay "):
            try:
                step_idx = int(question.lower().split()[1])
                snap = list(graph.get_state_history(config))[step_idx]
                result = graph.invoke(None, config=snap.config)
                print("\nFinal Answer:\n")
                print(result.get("generation"))
            except (ValueError, IndexError):
                print("Invalid step index.")
            continue

        generation = None
        for update in graph.stream(
            {
                "question": question,
                "search_query": question,
                "retries": 0,
            },
            config=config,
            stream_mode="updates",
        ):
            for delta in update.values():
                if not delta:
                    continue
                if "documents" in delta:
                    print(f"-> Retrieved {len(delta['documents'])} documents.")
                if "search_query" in delta:
                    print(f"-> Rewritten query: {delta['search_query']}")
                generation = delta.get("generation", generation)

        print("\nFinal Answer:\n")
        print(generation)


if __name__ == "__main__":
    main()
