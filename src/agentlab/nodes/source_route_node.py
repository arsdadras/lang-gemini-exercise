"""The research graph's source router: which sources each sub-question needs (R1 topic 3).

A decision point, ``research_sources@1``, on the ``decision_model`` seam. One judgment per
(sub-question, source): "would this source help answer this sub-question?", answered ``yes``,
``no``, or ``unclear``, all asked in one request with every question naming its sub-question.
Code combines the answers:

- a source is skipped only on a sure ``no`` (``SKIP_THRESHOLD``); ``unclear`` keeps it, because a
  wrong skip loses evidence while a wrong keep costs at most that source's search budget;
- a sub-question no source fits gets the web, the general source;
- a decider outage keeps every source for every sub-question (fail open: this point routes
  work, it guards nothing), and the runs' budgets bound what that costs.

The threshold is provisional until the labeled set (``evals/datasets/research_sources.json``)
is measured per model version (``decision-models.md``).
"""

from collections.abc import Callable

from langchain_typesafe import Choice, ClassifierResponse, Question

from agentlab.models import decision_model
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.state.research_state import ResearchState
from agentlab.tools.research_source_tool import research_sources
from agentlab.utils.failure_util import failure_kind

QUESTION_SET = "research_sources@1"
SKIP_THRESHOLD = 0.6

Decide = Callable[..., ClassifierResponse]

_CRITERIA: dict[str, dict[str, str]] = {
    "web": {
        "yes": "Web pages would help: documentation, product or vendor pages, news, blogs, "
        "tutorials, official statistics, or practice in industry.",
        "no": "Only published research or this project's own files can answer it.",
    },
    "academic": {
        "yes": "Published research would help: studies, benchmarks, experiments, methods, "
        "surveys, or findings reported in papers.",
        "no": "Papers would not help: the answer is a product fact, a price, an event, a "
        "how-to, an opinion, or something about this project's own files. Mentioning a "
        "technical subject does not by itself make a question one for papers.",
    },
    "private": {
        "yes": "The question is about agentlab itself, this teaching project on agentic AI "
        "(its design decisions, architecture, conventions, code, roadmap, or lessons), so "
        "its own files would help.",
        "no": "The question is about the world outside this project, even when its subject "
        "(LangChain, LangGraph, agents, RAG) is one the project also uses.",
    },
}
_UNCLEAR = "The question gives too little to tell."


def _question(index: int, sub_question: str, source: str) -> Question:
    criteria = {**_CRITERIA[source], "unclear": _UNCLEAR}
    return Choice(
        instructions=(
            f"Sub-question {index}: {sub_question}\n"
            f"Would the {source} source help answer sub-question {index}?"
        ),
        criteria=criteria,
    )


def _state(questions: list[str]) -> str:
    listed = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, start=1))
    return (
        "A research run splits a topic into sub-questions and searches sources for each. The "
        "sources: web (pages on the open web), academic (published research papers), and "
        "private (agentlab's own documentation and code).\n\nSub-questions:\n" + listed
    )


def route_sources(
    questions: list[str], sources: list[str], *, decide: Decide
) -> dict[str, list[str]]:
    """The sources each sub-question needs, among ``sources`` (in their order)."""
    if len(sources) <= 1:
        return {question: list(sources) for question in questions}
    asked = {
        f"q{i}_{source}": _question(i, question, source)
        for i, question in enumerate(questions, start=1)
        for source in sources
    }
    try:
        response = decide(_state(questions), asked, question_set=QUESTION_SET)
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return {question: list(sources) for question in questions}
    routes: dict[str, list[str]] = {}
    for i, question in enumerate(questions, start=1):
        chosen = []
        for source in sources:
            answer = response.choices[f"q{i}_{source}"]
            sure_no = (
                answer.choice == "no"
                and answer.probabilities.get("no", 0.0) >= SKIP_THRESHOLD
            )
            if not sure_no:
                chosen.append(source)
        routes[question] = chosen or (["web"] if "web" in sources else list(sources))
    return routes


def make_route_node(decide: Decide | None = None) -> Callable[[ResearchState], dict]:
    """Build the node that routes every sub-question to its sources.

    The sources come from the caller's options and what this environment can serve
    (``research_sources``); requested sources that can't be served are reported.
    """

    def route(state: ResearchState) -> dict:
        options = state.get("options") or ResearchOptions()
        sources, missing = research_sources(options.sources)
        routes = route_sources(
            state["questions"], sources, decide=decide or decision_model.decide
        )
        update: dict = {"routes": routes}
        if missing:
            update["problems"] = [
                "Not available here, so not searched: " + ", ".join(missing) + "."
            ]
        return update

    return route
