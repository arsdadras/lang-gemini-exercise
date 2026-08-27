from langchain_core.documents import Document
from typing import TypedDict
from .op_schema import ReviewResult, TestSuite


class RAGState(TypedDict):
    question: str
    documents: list[Document]
    generation: str


class CodeReviewState(TypedDict):
    code: str
    language: str
    file_path: str | None
    review: ReviewResult | None
    tests: TestSuite | None
    error: str | None
