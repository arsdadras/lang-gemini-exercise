from graphs.rag import build_rag_graph
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    graph = build_rag_graph()
    config = {"configurable": {"thread_id": "rag_session_001"}}

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
            for node_name, delta in update.items():
                # print(f"{node_name} running: ...")
                if not delta:
                    continue
                if "documents" in delta:
                    print(f'-> Retrieved {len(delta["documents"])} documents.')
                if "search_query" in delta:
                    print(f'-> Rewritten query: {delta["search_query"]}')
                generation = delta.get("generation", generation)

        print("\nFinal Answer:\n")
        print(generation)


if __name__ == "__main__":
    main()
