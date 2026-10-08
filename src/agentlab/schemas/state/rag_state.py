"""Graph state for the P2 RAG graph."""

from typing import Literal, NotRequired, TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    """State for answering one question.

    ``search_query`` and ``retries`` are per-question scratch fields with no
    reducer: nodes default them (``search_query`` falls back to ``question``,
    ``retries`` to 0), and a caller reusing a thread must reset them per question.
    """

    question: str
    search_query: NotRequired[str]
    chunks: NotRequired[list[Document]]
    answer: NotRequired[str]
    retries: NotRequired[int]
    answer_source: NotRequired[Literal["corpus", "web", "unverified", "none"]]
    """Where ``answer`` came from: the corpus (checked against its chunks), the web
    fallback, a disclaimer after the check failed, or nowhere."""
