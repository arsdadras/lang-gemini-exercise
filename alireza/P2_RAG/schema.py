from dataclasses import dataclass
from typing import TypedDict
from pydantic import Field
from typing import Literal
from pydantic import BaseModel
from langchain_core.documents import Document


class GradeDocument(BaseModel):
    binary_score: Literal["Yes", "No"] = Field(
        description="yes if the retrieved document is relevent, else no"
    )


class AnswerGeneration(BaseModel):
    answer: str = Field(description="The generated answer to the question")
    citations: dict = Field(description="The citations for the generated answer")


@dataclass
class DocsContext:
    content: str = Field(description="The content of the retrieved document")
    metadata: dict = Field(
        description="The metadata of the retrieved document from sources"
    )


class RAGState(TypedDict):
    question: str
    documents: list[Document]
    generation: str


# The new State for the Alireza Node
class RAGStateAlireza(TypedDict):
    question: str
    documents: list[DocsContext]
    generation: AnswerGeneration
