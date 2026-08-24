"""Structured output schemas."""

from output_schemas.rag import GradeDocument
from output_schemas.research import ResearchReport, ResearchFindings, Source

__all__ = ["GradeDocument", "ResearchFindings", "ResearchReport", "Source"]
