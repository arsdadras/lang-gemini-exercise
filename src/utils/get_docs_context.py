"""docs context utility for the RAG agent: returns a string representation of the documents in the state."""

from langchain_core.documents import Document


def get_docs_context(documents: list[Document]) -> str:
    """Return a string representation of the documents."""
    if not documents:
        return "No documents found."
    context = "\n\n".join(
        f"[{doc.metadata['source']}]\n{doc.page_content}" for doc in documents
    )
    return context
