"""End-to-end domain workflows (``run_*``) and ``Specialist`` descriptors (ADR-0033)."""

from agentlab.workflows.base import Specialist, WorkflowRunner
from agentlab.workflows.code_review_workflow import (
    CODE_REVIEW_SPECIALIST,
    make_code_review_specialist,
    render_outcome,
    run_code_review,
)
from agentlab.workflows.interpreter_workflow import (
    INTERPRETER_SPECIALIST,
    make_interpreter_specialist,
    render_interpreter_report,
    run_interpreter,
)
from agentlab.workflows.personal_brief_workflow import (
    brief_request,
    make_brief_researcher_agent,
    run_personal_brief,
)
from agentlab.workflows.personal_context_workflow import (
    PERSONAL_CONTEXT_SPECIALIST,
    make_personal_context_specialist,
    run_personal_context,
)
from agentlab.workflows.rag_workflow import (
    RAG_SPECIALIST,
    make_rag_specialist,
    render_rag_report,
    run_rag,
)
from agentlab.workflows.research_workflow import (
    RESEARCH_SPECIALIST,
    make_research_graph,
    make_research_specialist,
    render_research_report,
    run_research,
    verify_research,
)

__all__ = [
    "CODE_REVIEW_SPECIALIST",
    "INTERPRETER_SPECIALIST",
    "PERSONAL_CONTEXT_SPECIALIST",
    "RAG_SPECIALIST",
    "RESEARCH_SPECIALIST",
    "Specialist",
    "WorkflowRunner",
    "brief_request",
    "make_brief_researcher_agent",
    "make_code_review_specialist",
    "make_interpreter_specialist",
    "make_personal_context_specialist",
    "make_rag_specialist",
    "make_research_graph",
    "make_research_specialist",
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
