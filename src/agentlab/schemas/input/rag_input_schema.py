"""What a caller asks of the P2 RAG specialist: ``RagInput``."""

from pydantic import BaseModel, Field


class RagInput(BaseModel):
    """Typed input for the P2 RAG specialist."""

    question: str = Field(
        description="The question to answer from the indexed corpus or web fallback."
    )
