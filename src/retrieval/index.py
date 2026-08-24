"""Build and load the local vector index the P2 RAG agent retrieves from.

Ingestion is a one-time (or on-demand) offline step, run with
``uv run python src/retrieval/index.py`` — kept out of the query-time graph
in ``graphs/rag.py`` on purpose. Indexing re-embeds the whole corpus, and
the corpus doesn't change per question, so it has no business running on
the request path.
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = REPO_ROOT / ".chroma_index"
COLLECTION_NAME = "repo_corpus"
EMBEDDING_MODEL = "gemini-embedding-2-preview"

DOC_FILES = ["ROADMAP.md", "AGENTS.md", "README.md", "MENTOR_HANDOFF.md"]
CODE_GLOB = "src/**/*.py"


def _embeddings() -> GoogleGenerativeAIEmbeddings:
    """Initialize the embedding model for re-embedding the corpus."""
    return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)


def _load_source_documents() -> list[Document]:
    """Load markdown and python source files from the repo root."""
    documents = [
        Document(
            page_content=(REPO_ROOT / name).read_text(encoding="utf-8"),
            metadata={"source": name},
        )
        for name in DOC_FILES
    ]
    for path in sorted(REPO_ROOT.glob(CODE_GLOB)):
        if "__pycache__" in path.parts:
            continue
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": str(path.relative_to(REPO_ROOT))},
            )
        )
    return documents


def build_index() -> Chroma:
    """Chunk every source document, embed it, and persist it to disk."""
    documents = _load_source_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    return Chroma.from_documents(
        documents=chunks,
        embedding=_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )


def get_retriever(k=3) -> VectorStoreRetriever:
    """Load the persisted index and return a retriever over it."""

    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Index not found at {CHROMA_DIR}. "
            "Run 'uv run python src/retrieval/index.py' first to build it."
        )

    store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=_embeddings(),
    )
    return store.as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    print(f"Building vector index at {CHROMA_DIR}...")
    index = build_index()
    print("Done! Index created successfully.")
