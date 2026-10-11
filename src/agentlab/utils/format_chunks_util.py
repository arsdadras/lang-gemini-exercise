"""Chunks as the RAG prompts read them: each chunk's source, then its text."""

from langchain_core.documents import Document


def format_chunks(chunks: list[Document]) -> str:
    """Return a string representation of the chunks."""
    if not chunks:
        return "No chunks found."
    context = "\n\n".join(
        f"[{chunk.metadata['source']}]\n{chunk.page_content}" for chunk in chunks
    )
    return context
