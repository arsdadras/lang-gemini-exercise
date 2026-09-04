"""State schema for the P2 RAG agent's graph."""

from typing import TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    """Graph state for RAG research agent."""

    question: str
    search_query: str
    documents: list[Document]
    generation: str
    retries: int
