"""Nodes of P1's research graph (``graphs/research_graph.py``): plan, then one run per sub-question.

- ``make_plan_node`` splits a broad topic into sub-questions with ``plan_research``.
- ``fan_out`` sends each sub-question to its own run of the research node, in parallel, with the
  sources the router picked for it (``source_route_node.py``).
- ``make_research_node`` runs the researcher agent on one sub-question, limited to its sources,
  and returns its draft and the documents its source tools returned, or the problem it met.
- ``read_research_run`` reads one run's outcome from the researcher agent's final state.

The claim check that follows lives in ``claim_check_node.py``.

The planner: the depth's budget caps the number of sub-questions; ``quick`` never plans (one run
on the topic). Code, not the model, enforces the cap, drops blanks and exact repeats (they carry
nothing new), and falls back to the topic itself when the plan comes back empty. The planner
lists its sub-questions most important first. A plan over the cap gets one re-plan, told what it
did, because a re-plan can merge sub-questions where a cut can only drop them; if it is still
over, the cap cuts the least important, and the cut ones are reported, never dropped silently.
"""

from collections.abc import Callable, Mapping
from typing import Any, NamedTuple

from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.config import get_config
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, Send, interrupt

from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.models import llm_model
from agentlab.prompts.nodes.research_plan_prompt import (
    RESEARCH_PLAN_PROMPT,
    RESEARCH_REPLAN_FEEDBACK,
)
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ResearchDraft,
    ResearchPlan,
    SourceDocument,
)
from agentlab.schemas.state.research_state import ResearchState, SubQuestionState
from agentlab.tools.research_source_tool import documents_read
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals

RESEARCH_NODE = "research"


class ResearchRun(NamedTuple):
    """What one finished researcher run produced."""

    draft: ResearchDraft | None
    """The structured report, or None when the run ended without one."""
    documents: dict[str, SourceDocument]
    """Every document the run's source tools returned (``documents_read``)."""
    evidence_enough: bool | None
    """The stop condition's last judgment (R1 topic 4); None when it never judged."""


def read_research_run(state: Mapping[str, Any]) -> ResearchRun:
    """Read a finished run's final state: the one place that knows its keys."""
    return ResearchRun(
        draft=state.get("structured_response"),
        documents=documents_read(state.get("messages", [])),
        evidence_enough=state.get("evidence_enough"),
    )


def plan_research(
    topic: str,
    options: ResearchOptions,
    *,
    plan_chain: Runnable[Any, ResearchPlan] | None = None,
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


def make_plan_node(
    plan_chain: Runnable[Any, ResearchPlan] | None = None,
) -> Callable[..., dict]:
    """Build the node that turns the topic into the sub-questions to research.

    Without options the topic is researched as it is: one run, no plan, no model call.
    """

    def plan(state: ResearchState) -> dict:
        options = state.get("options")
        if options is None:
            return {"questions": [state["topic"]], "cut": []}
        questions, cut = plan_research(state["topic"], options, plan_chain=plan_chain)
        update: dict = {"questions": questions, "cut": cut}
        if cut:
            update["problems"] = [
                f"{len(cut)} sub-questions over the cap of {len(questions)} were not "
                "researched: " + "; ".join(f"'{question}'" for question in cut) + "."
            ]
        return update

    return plan


def fan_out(state: ResearchState) -> list[Send]:
    """One ``Send`` per sub-question: the research node runs once for each, in parallel.

    Each payload is the run's ``SubQuestionState``, built by name so the type checker holds
    it to the research node's input.
    """
    questions = state["questions"]
    routes = state.get("routes", {})
    return [
        Send(
            RESEARCH_NODE,
            SubQuestionState(
                question=question,
                sources=routes.get(question, ["web"]),
                label=f"'{question}': " if len(questions) > 1 else "",
            ),
        )
        for question in questions
    ]


def _parent_has_checkpointer() -> bool:
    """True when the enclosing ``research_graph`` was compiled with a checkpointer."""
    try:
        conf = get_config().get("configurable", {})
    except RuntimeError:
        return False
    return conf.get("__pregel_checkpointer") is not None


def _parent_thread_id() -> str:
    """Thread id of the enclosing ``research_graph``, or ``""`` when unconfigured."""
    try:
        conf = get_config().get("configurable", {})
    except RuntimeError:
        return ""
    return str(conf.get("thread_id", ""))


def make_research_node(agent: CompiledStateGraph) -> Callable[..., dict]:
    """Build the node that researches one sub-question with the injected P1 agent.

    Each run gets a fresh thread, so its messages hold only the documents its own tools
    returned, and the claim check later judges each claim against those. The run's ``sources``
    go in its input, where ``SourceRouteMiddleware`` limits the agent to their tools.
    When the parent ``research_graph`` has a checkpointer, outbound search approvals are
    propagated via ``interrupt()`` and resumed onto the child thread; in an uncheckpointed
    one-shot run, a paused search or external failure becomes a problem so other runs go on.
    """
    active_runs: dict[
        tuple[str, str], tuple[RunnableConfig, dict[str, Any], list[Any]]
    ] = {}

    def research(task: SubQuestionState) -> dict:
        label = task["label"]
        run_key = (_parent_thread_id(), task["question"])
        if run_key in active_runs:
            child_config, outcome, history = active_runs[run_key]
            for past_value in history:
                interrupt(past_value)
        else:
            child_config = new_delegation_config()
            history = []
            try:
                outcome = agent.invoke(
                    {
                        "messages": [HumanMessage(content=task["question"])],
                        "sources": task["sources"],
                    },
                    config=child_config,
                )
            except Exception as error:
                if failure_kind(error) is None:
                    raise
                return {"problems": [label + failure_reason(error)]}

        if outcome.get("__interrupt__") and _parent_has_checkpointer():
            active_runs[run_key] = (child_config, outcome, history)
            while outcome.get("__interrupt__"):
                pending_value = outcome["__interrupt__"][0].value
                decision = interrupt(pending_value)
                history.append(pending_value)
                try:
                    outcome = agent.invoke(
                        Command(resume=decision), config=child_config
                    )
                except Exception as error:
                    active_runs.pop(run_key, None)
                    if failure_kind(error) is None:
                        raise
                    return {"problems": [label + failure_reason(error)]}
                active_runs[run_key] = (child_config, outcome, history)
            active_runs.pop(run_key, None)

        if waiting := pending_approvals(outcome):
            return {
                "problems": [
                    f"{label}Stopped before finishing: waiting for approval of {waiting}."
                ]
            }
        run = read_research_run(outcome)
        if run.draft is None:
            return {"problems": [label + "No report was produced."]}
        update: dict = {"drafts": [run.draft], "documents": run.documents}
        if run.evidence_enough is False:
            update["problems"] = [
                f"{label}The search budget ran out before the evidence was enough."
            ]
        return update

    return research
