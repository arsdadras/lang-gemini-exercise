"""End-to-end domain workflows (``run_*``) and ``Specialist`` descriptors (ADR-0033)."""

from typing import TYPE_CHECKING, Any

from agentlab.workflows.specialist_workflow import (
    ResultNode,
    SpecialistSpec,
    Workflow,
    WorkflowOutputState,
    WorkflowOverallState,
    WorkflowRunner,
)

if TYPE_CHECKING:
    from agentlab.workflows.code_review_workflow import (
        CODE_REVIEW_SPECIALIST,
        CodeReviewWorkflow,
        make_code_review_specialist,
        render_outcome,
        run_code_review,
    )
    from agentlab.workflows.interpreter_workflow import (
        INTERPRETER_SPECIALIST,
        InterpreterWorkflow,
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
        PersonalContextWorkflow,
        make_personal_context_specialist,
        run_personal_context,
    )
    from agentlab.workflows.rag_workflow import (
        RAG_SPECIALIST,
        RagWorkflow,
        make_rag_specialist,
        render_rag_report,
        run_rag,
    )
    from agentlab.workflows.research_workflow import (
        RESEARCH_SPECIALIST,
        ResearchWorkflow,
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
    "CodeReviewWorkflow",
    "InterpreterWorkflow",
    "PersonalContextWorkflow",
    "RagWorkflow",
    "ResearchWorkflow",
    "ResultNode",
    "SpecialistSpec",
    "Workflow",
    "WorkflowOutputState",
    "WorkflowOverallState",
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

_SUBMODULE_MAP = {
    "CODE_REVIEW_SPECIALIST": "agentlab.workflows.code_review_workflow",
    "CodeReviewWorkflow": "agentlab.workflows.code_review_workflow",
    "make_code_review_specialist": "agentlab.workflows.code_review_workflow",
    "render_outcome": "agentlab.workflows.code_review_workflow",
    "run_code_review": "agentlab.workflows.code_review_workflow",
    "INTERPRETER_SPECIALIST": "agentlab.workflows.interpreter_workflow",
    "InterpreterWorkflow": "agentlab.workflows.interpreter_workflow",
    "make_interpreter_specialist": "agentlab.workflows.interpreter_workflow",
    "render_interpreter_report": "agentlab.workflows.interpreter_workflow",
    "run_interpreter": "agentlab.workflows.interpreter_workflow",
    "brief_request": "agentlab.workflows.personal_brief_workflow",
    "make_brief_researcher_agent": "agentlab.workflows.personal_brief_workflow",
    "run_personal_brief": "agentlab.workflows.personal_brief_workflow",
    "PERSONAL_CONTEXT_SPECIALIST": "agentlab.workflows.personal_context_workflow",
    "PersonalContextWorkflow": "agentlab.workflows.personal_context_workflow",
    "make_personal_context_specialist": "agentlab.workflows.personal_context_workflow",
    "run_personal_context": "agentlab.workflows.personal_context_workflow",
    "RAG_SPECIALIST": "agentlab.workflows.rag_workflow",
    "RagWorkflow": "agentlab.workflows.rag_workflow",
    "make_rag_specialist": "agentlab.workflows.rag_workflow",
    "render_rag_report": "agentlab.workflows.rag_workflow",
    "run_rag": "agentlab.workflows.rag_workflow",
    "RESEARCH_SPECIALIST": "agentlab.workflows.research_workflow",
    "ResearchWorkflow": "agentlab.workflows.research_workflow",
    "make_research_graph": "agentlab.workflows.research_workflow",
    "make_research_specialist": "agentlab.workflows.research_workflow",
    "render_research_report": "agentlab.workflows.research_workflow",
    "run_research": "agentlab.workflows.research_workflow",
    "verify_research": "agentlab.workflows.research_workflow",
}


def __getattr__(name: str) -> Any:
    if name in _SUBMODULE_MAP:
        module = __import__(_SUBMODULE_MAP[name], fromlist=[name])
        val = getattr(module, name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
