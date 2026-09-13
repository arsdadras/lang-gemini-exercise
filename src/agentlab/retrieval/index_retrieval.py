"""Offline index build and query-time retriever for the P2 RAG graph.

Indexing re-embeds the whole corpus, so it runs on demand, never on the request path:
``uv run python -m agentlab.retrieval.index_retrieval``
"""

import time

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agentlab.configs.paths_config import CHROMA_DIR, PROJECT_ROOT
from agentlab.configs.rag_config import (
    CODE_GLOB,
    COLLECTION_NAME,
    DOC_FILES,
    EMBED_BATCH_DELAY_SECONDS,
    EMBED_BATCH_SIZE,
    EMBEDDING_MODEL,
    RETRIEVER_TOP_K,
)


def _open_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL),
    )


def _load_source_documents() -> list[Document]:
    """Load the configured docs and every source file, tagged with repo-relative paths."""
    documents = [
        Document(page_content=(PROJECT_ROOT / name).read_text(encoding="utf-8"), metadata={"source": name})
        for name in DOC_FILES
    ]
    for path in sorted(PROJECT_ROOT.glob(CODE_GLOB)):
        if "__pycache__" in path.parts:
            continue
        documents.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": path.relative_to(PROJECT_ROOT).as_posix()},
            )
        )
    return documents


def build_index() -> Chroma:
    """Rebuild the collection from scratch, embedding in paced batches."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(_load_source_documents())
    store = _open_store()
    store.reset_collection()
    for start in range(0, len(chunks), EMBED_BATCH_SIZE):
        store.add_documents(chunks[start : start + EMBED_BATCH_SIZE])
        if start + EMBED_BATCH_SIZE < len(chunks):
            time.sleep(EMBED_BATCH_DELAY_SECONDS)
    return store


def get_retriever(k: int = RETRIEVER_TOP_K) -> VectorStoreRetriever:
    """Open the persisted index as a retriever."""
    if not CHROMA_DIR.exists():
        msg = (
            f"Index not found at {CHROMA_DIR}. Build it first: "
            "uv run python -m agentlab.retrieval.index_retrieval"
        )
        raise FileNotFoundError(msg)
    return _open_store().as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    load_dotenv()
    print(f"Building vector index at {CHROMA_DIR} ...")
    build_index()
    print("Done.")
