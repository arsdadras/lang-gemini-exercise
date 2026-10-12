"""End-to-end domain workflows (``run_*``) and ``Specialist`` descriptors (ADR-0033)."""

from agentlab.workflows.code_review_workflow import (
    CODE_REVIEW_SPECIALIST,
    CODE_REVIEW_SPECIALIST_SPEC,
    render_outcome,
    run_code_review,
)
from agentlab.workflows.interpreter_workflow import (
    INTERPRETER_SPECIALIST,
    INTERPRETER_SPECIALIST_SPEC,
    render_interpreter_report,
    run_interpreter,
)
from agentlab.workflows.personal_brief_workflow import (
    brief_request,
    make_brief_researcher_agent,
    run_personal_brief,
)
from agentlab.workflows.personal_context_workflow import (
    PERSONAL_CONTEXT_SPECIALIST_SPEC,
    run_personal_context,
)
from agentlab.workflows.rag_workflow import (
    RAG_SPECIALIST,
    RAG_SPECIALIST_SPEC,
    render_rag_report,
    run_rag,
)
from agentlab.workflows.research_workflow import (
    RESEARCH_SPECIALIST,
    RESEARCH_SPECIALIST_SPEC,
    render_research_report,
    run_research,
    verify_research,
)

__all__ = [
    "CODE_REVIEW_SPECIALIST",
    "CODE_REVIEW_SPECIALIST_SPEC",
    "INTERPRETER_SPECIALIST",
    "INTERPRETER_SPECIALIST_SPEC",
    "PERSONAL_CONTEXT_SPECIALIST_SPEC",
    "RAG_SPECIALIST",
    "RAG_SPECIALIST_SPEC",
    "RESEARCH_SPECIALIST",
    "RESEARCH_SPECIALIST_SPEC",
    "brief_request",
    "make_brief_researcher_agent",
    "render_interpreter_report",
    "render_outcome",
    "render_rag_report",
    "render_research_report",
    "run_code_review",
    "run_interpreter",
    "run_personal_brief",
    "run_personal_context",
    "run_rag",
    "run_research",
    "verify_research",
]
