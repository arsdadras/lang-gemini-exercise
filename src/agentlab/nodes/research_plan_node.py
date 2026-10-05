"""R1 topic 2's planner: a broad topic split into sub-questions, each researched on its own run.

The depth's budget caps the number of sub-questions; ``quick`` never plans (one run on the
topic). Code, not the model, enforces the cap, drops blanks and exact repeats (they carry
nothing new), and falls back to the topic itself when the plan comes back empty. The planner
lists its sub-questions most important first. A plan over the cap gets one re-plan, told what
it did, because a re-plan can merge sub-questions where a cut can only drop them; if it is still
over, the cap cuts the least important, and the cut ones are returned for the caller to report,
never dropped silently.
"""

from langchain_core.runnables import Runnable

from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.models import llm_model
from agentlab.prompts.nodes.research_plan_prompt import (
    RESEARCH_PLAN_PROMPT,
    RESEARCH_REPLAN_FEEDBACK,
)
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import ResearchPlan


def plan_research(
    topic: str, options: ResearchOptions, *, plan_chain: Runnable | None = None
) -> tuple[list[str], list[str]]:
    """The sub-questions to research for ``topic`` (at least one, at most the depth's cap), and
    the ones the cap cut."""
    limit = DEPTH_BUDGETS[options.depth].sub_questions
    if limit <= 1:
        return [topic], []
    chain = plan_chain or RESEARCH_PLAN_PROMPT | llm_model.chain(
        "low", structured=ResearchPlan
    )
    inputs = {"topic": topic, "max_sub_questions": limit, "language": options.language}
    questions = _distinct(chain.invoke({**inputs, "feedback": ""}))
    if len(questions) > limit:
        feedback = RESEARCH_REPLAN_FEEDBACK.format(
            count=len(questions),
            limit=limit,
            previous="\n".join(f"- {question}" for question in questions),
        )
        questions = _distinct(chain.invoke({**inputs, "feedback": feedback}))
    return questions[:limit] or [topic], questions[limit:]


def _distinct(plan: ResearchPlan) -> list[str]:
    """The plan's sub-questions without blanks or exact repeats, in the planner's order."""
    return list(dict.fromkeys(q.strip() for q in plan.sub_questions if q.strip()))
