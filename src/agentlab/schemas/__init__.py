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
    GradeDocument,
    GradeHallucination,
    GroundednessVerdict,
    GuardVerdict,
    ResearchFindings,
    ResearchReport,
    ReviewResult,
    Source,
    TestCase,
    TestExecutionResult,
    TestSuite,
)
from agentlab.schemas.state import CodeReviewState, RAGState

__all__ = [
    "ArtifactMetadata",
    "ArtifactType",
    "CodeIssue",
    "CodeReviewState",
    "GradeDocument",
    "GradeHallucination",
    "GroundednessVerdict",
    "GuardVerdict",
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
