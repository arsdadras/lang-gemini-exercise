from graphs.rag import build_rag_graph
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    graph = build_rag_graph()
    question = input("what do you want to ask about the indexed corpus? ")

    result = graph.invoke({"question": question})

    print(result["generation"])


if __name__ == "__main__":
    main()
