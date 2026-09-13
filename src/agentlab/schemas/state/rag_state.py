"""Graph state for the P2 RAG graph."""

from typing import NotRequired, TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    """State for answering one question.

    ``search_query`` and ``retries`` are per-question scratch fields with no
    reducer: nodes default them (``search_query`` falls back to ``question``,
    ``retries`` to 0), and a caller reusing a thread must reset them per question.
    """

    question: str
    search_query: NotRequired[str]
    documents: NotRequired[list[Document]]
    generation: NotRequired[str]
    retries: NotRequired[int]
