"""Documents a user hands to one research run: loaded, chunked, and searched in memory.

The default document source is this project's own docs and code, indexed ahead of time
(``index_retrieval.py``). A user can give a run its own files instead, plain text or Markdown
only (no extraction or conversion from other formats); they are embedded when the run first
searches them and kept in memory for that run, never written to the persisted index.
"""

from collections.abc import Sequence
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore, VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agentlab.configs.rag_config import RETRIEVER_TOP_K
from agentlab.configs.research_config import DOCUMENT_SUFFIXES
from agentlab.retrieval.index_retrieval import make_embeddings


def check_document_paths(paths: Sequence[str]) -> list[Path]:
    """The given paths as files a run can read; ``ValueError`` names every one it can't."""
    problems: list[str] = []
    files: list[Path] = []
    for raw in paths:
        path = Path(raw).expanduser()
        if path.suffix.lower() not in DOCUMENT_SUFFIXES:
            problems.append(
                f"{raw}: only {', '.join(DOCUMENT_SUFFIXES)} files are supported"
            )
        elif not path.is_file():
            problems.append(f"{raw}: no such file")
        else:
            files.append(path)
    if problems:
        raise ValueError("; ".join(problems))
    return files


def load_documents(paths: Sequence[str]) -> list[Document]:
    """Each file as one ``Document``, its ``source`` the path as given."""
    return [
        Document(
            page_content=path.read_text(encoding="utf-8"),
            metadata={"source": Path(raw).as_posix()},
        )
        for raw, path in zip(paths, check_document_paths(paths), strict=True)
    ]


def build_document_retriever(
    paths: Sequence[str], k: int = RETRIEVER_TOP_K
) -> VectorStoreRetriever:
    """Chunk and embed the given files in memory, and search them like the project index."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    store = InMemoryVectorStore(make_embeddings())
    store.add_documents(splitter.split_documents(load_documents(paths)))
    return store.as_retriever(search_kwargs={"k": k})
