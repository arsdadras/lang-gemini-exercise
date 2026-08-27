from langchain_core.documents import Document


def get_docs_context(documents: list[Document]) -> str:
    """Format a list of documents into a single prompt-ready context string."""
    context = "\n\n".join(
        f"[{doc.metadata['source']}]\n{doc.page_content}" for doc in documents
    )
    return context
