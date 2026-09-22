"""Typed contracts, grouped by role rather than by construction method:

- ``output/``  Pydantic response contracts (``response_format``, node/subagent payloads).
- ``state/``   graph-state TypedDicts.
- ``context/`` runtime context passed via ``context=`` (e.g. user identity).

Import the specific submodule directly (e.g. ``agentlab.schemas.output.rag_output_schema``)
or use this barrel for the common names.
"""

from agentlab.schemas.context import UserContext
from agentlab.schemas.output import (
    ArtifactMetadata,
    ArtifactType,
    CodeIssue,
    FinglishLines,
    GradeDocument,
    GradeHallucination,
    GroundednessVerdict,
    GuardVerdict,
    MemoryEdit,
    MemoryEdits,
    ResearchFindings,
    ResearchReport,
    ReviewResult,
    Source,
    TestCase,
    TestExecutionResult,
    TestSuite,
)
from agentlab.schemas.state import CodeReviewState, MemoryConsolidationState, RAGState

__all__ = [
    "ArtifactMetadata",
    "ArtifactType",
    "CodeIssue",
    "CodeReviewState",
    "FinglishLines",
    "GradeDocument",
    "GradeHallucination",
    "GroundednessVerdict",
    "GuardVerdict",
    "MemoryConsolidationState",
    "MemoryEdit",
    "MemoryEdits",
    "RAGState",
    "ResearchFindings",
    "ResearchReport",
    "ReviewResult",
    "Source",
    "TestCase",
    "TestExecutionResult",
    "TestSuite",
    "UserContext",
]
