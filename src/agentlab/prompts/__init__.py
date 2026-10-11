"""Prompt text, split by architectural role: agents, subagents, graph nodes, middlewares."""

from agentlab.prompts.agents_prompt import (
    build_coding_coordinator_prompt,
    build_interpreter_agent_prompt,
    build_personal_assistant_prompt,
    build_repo_insight_prompt,
    build_researcher_prompt,
)
from agentlab.prompts.middlewares_prompt import (
    MEMORY_WRITE_POLICY,
    SECURITY_GUARD_PROMPT,
)
from agentlab.prompts.nodes.code_review_prompt import (
    REVIEW_PROMPT,
    TEST_FIX_PROMPT,
    TEST_GEN_PROMPT,
)
from agentlab.prompts.nodes.rag_prompt import (
    GENERATE_FROM_WEB_PROMPT,
    GENERATE_PROMPT,
    GRADE_PROMPT,
    HALLUCINATION_PROMPT,
    REWRITE_PROMPT,
)
from agentlab.prompts.subagents_prompt import (
    RESEARCHER_SUBAGENT_PROMPT,
    build_interpreter_worker_prompt,
)
from agentlab.prompts.template.builder import build_system_prompt
from agentlab.prompts.template.template import DEFAULTS

__all__ = [
    "DEFAULTS",
    "GENERATE_FROM_WEB_PROMPT",
    "GENERATE_PROMPT",
    "GRADE_PROMPT",
    "HALLUCINATION_PROMPT",
    "MEMORY_WRITE_POLICY",
    "RESEARCHER_SUBAGENT_PROMPT",
    "REVIEW_PROMPT",
    "REWRITE_PROMPT",
    "SECURITY_GUARD_PROMPT",
    "TEST_FIX_PROMPT",
    "TEST_GEN_PROMPT",
    "build_coding_coordinator_prompt",
    "build_interpreter_agent_prompt",
    "build_interpreter_worker_prompt",
    "build_personal_assistant_prompt",
    "build_repo_insight_prompt",
    "build_researcher_prompt",
    "build_system_prompt",
]
