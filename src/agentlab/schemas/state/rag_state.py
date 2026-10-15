"""Graph state for the P2 RAG graph."""

import operator
from typing import Annotated, Literal, NotRequired, TypedDict

from langchain_core.documents import Document

from agentlab.schemas.output.rag_output_schema import RagReport
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SideEffect,
    SpecialistResult,
)


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

    report: NotRequired[RagReport | None]
    problems: NotRequired[Annotated[list[str], operator.add]]
    provenance: NotRequired[Annotated[list[Provenance], operator.add]]
    side_effects: NotRequired[Annotated[list[SideEffect], operator.add]]
    result: NotRequired[SpecialistResult[RagReport]]
