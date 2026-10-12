"""Typed contracts, grouped by role rather than by construction method:

- ``output/``  Pydantic response contracts (``response_format``, ``*Report``, ``SpecialistResult``, ``Specialist``).
- ``input/``   typed inputs a caller passes to a specialist (``*Input``, ``ResearchOptions``).
- ``state/``   graph-state TypedDicts.
- ``context/`` runtime context passed via ``context=`` (e.g. user identity).

Import the specific submodule directly (e.g. ``agentlab.schemas.output.rag_output_schema``)
or use this barrel for the common names.
"""

from agentlab.schemas.context import UserContext
from agentlab.schemas.input import (
    CodeReviewInput,
    Depth,
    InterpreterInput,
    PersonalContextInput,
    RagInput,
    ResearchInput,
    ResearchOptions,
)
from agentlab.schemas.output import (
    Citation,
    Claim,
    ClaimVerdict,
    CodeIssue,
    CodeReview,
    CodeReviewReport,
    Deliverable,
    DeliverableType,
    DraftClaim,
    Evidence,
    FinglishLines,
    GradeChunk,
    GradeHallucination,
    GuardVerdict,
    InterpreterReport,
    MemoryEdit,
    MemoryEdits,
    PersonalContextReport,
    Provenance,
    RagGroundingVerdict,
    RagReport,
    RagRetrievalMode,
    ResearchDraft,
    ResearchFindings,
    ResearchReport,
    SideEffect,
    Specialist,
    SpecialistResult,
    SpecialistStatus,
    TestCase,
    TestRun,
    TestSuite,
)
from agentlab.schemas.state import CodeReviewState, MemoryConsolidationState, RAGState

__all__ = [
    "Citation",
    "Claim",
    "ClaimVerdict",
    "CodeIssue",
    "CodeReview",
    "CodeReviewInput",
    "CodeReviewReport",
    "CodeReviewState",
    "Deliverable",
    "DeliverableType",
    "Depth",
    "DraftClaim",
    "Evidence",
    "FinglishLines",
    "GradeChunk",
    "GradeHallucination",
    "GuardVerdict",
    "InterpreterInput",
    "InterpreterReport",
    "MemoryConsolidationState",
    "MemoryEdit",
    "MemoryEdits",
    "PersonalContextInput",
    "PersonalContextReport",
    "Provenance",
    "RAGState",
    "RagGroundingVerdict",
    "RagInput",
    "RagReport",
    "RagRetrievalMode",
    "ResearchDraft",
    "ResearchFindings",
    "ResearchInput",
    "ResearchOptions",
    "ResearchReport",
    "SideEffect",
    "Specialist",
    "SpecialistResult",
    "SpecialistStatus",
    "TestCase",
    "TestRun",
    "TestSuite",
    "UserContext",
]
