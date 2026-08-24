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

        result = graph.invoke(
            {"question": question, "search_query": question, "retries": 0},
            config=config,
        )

        print(result["generation"])


if __name__ == "__main__":
    main()
