"""The research graph's source router: which sources each sub-question needs (R1 topic 3).

A decision point, ``research_sources@2``, on the ``decision_model`` seam. One judgment per
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

from collections.abc import Callable, Sequence
from typing import Any

from langchain_typesafe import Choice, ClassifierResponse, Question

from agentlab.configs.research_config import PROJECT_CORPUS
from agentlab.models import decision_model
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.state.research_state import ResearchState
from agentlab.tools.research_source_tool import corpus_description, research_sources
from agentlab.utils.failure_util import failure_kind

QUESTION_SET = "research_sources@2"
SKIP_THRESHOLD = 0.6

Decide = Callable[..., ClassifierResponse]

_WORLD_CRITERIA: dict[str, dict[str, str]] = {
    "web": {
        "yes": "Web pages would help: documentation, product or vendor pages, news, blogs, "
        "tutorials, official statistics, or practice in industry.",
        "no": "Only published research or this project's own files can answer it.",
    },
    "academic": {
        "yes": "Published research would help: studies, benchmarks, experiments, methods, "
        "surveys, or findings reported in papers.",
        "no": "Papers would not help: the answer is a product fact, a price, an event, a "
        "how-to, an opinion, or something only the corpus source holds. Mentioning a "
        "technical subject does not by itself make a question one for papers.",
    },
}


def _criteria(source: str, corpus: str) -> dict[str, str]:
    """The criteria for one source; the corpus source's depend on what it holds."""
    if source != "corpus":
        return _WORLD_CRITERIA[source]
    return {
        "yes": f"The question is about {corpus}, so those files would help.",
        "no": "The question is about something those files don't hold, even when its "
        "subject (a framework, a method, a product) is one they also mention.",
    }


_UNCLEAR = "The question gives too little to tell."


def _question(index: int, sub_question: str, source: str, corpus: str) -> Question:
    criteria: dict[str, Any] = {**_criteria(source, corpus), "unclear": _UNCLEAR}
    return Choice(
        instructions=(
            f"Sub-question {index}: {sub_question}\n"
            f"Would the {source} source help answer sub-question {index}?"
        ),
        criteria=criteria,
    )


def _state(questions: list[str], corpus: str) -> str:
    listed = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, start=1))
    return (
        "A research run splits a topic into sub-questions and searches sources for each. The "
        "sources: web (pages on the open web), academic (published research papers), and "
        f"corpus ({corpus}).\n\nSub-questions:\n" + listed
    )


def route_sources(
    questions: list[str],
    sources: Sequence[str],
    *,
    decide: Decide,
    corpus: str = PROJECT_CORPUS,
) -> dict[str, list[str]]:
    """The sources each sub-question needs, among ``sources`` (in their order).

    ``corpus`` says what the corpus source holds: this project, or the user's files.
    """
    if len(sources) <= 1:
        return {question: list(sources) for question in questions}
    asked = {
        f"q{i}_{source}": _question(i, question, source, corpus)
        for i, question in enumerate(questions, start=1)
        for source in sources
    }
    try:
        response = decide(_state(questions, corpus), asked, question_set=QUESTION_SET)
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


def make_route_node(decide: Decide | None = None) -> Callable[..., dict]:
    """Build the node that routes every sub-question to its sources.

    The sources come from the caller's options and what this environment can serve
    (``research_sources``); requested sources that can't be served are reported.
    """

    def route(state: ResearchState) -> dict:
        options = state.get("options") or ResearchOptions()
        sources, missing = research_sources(options)
        routes = route_sources(
            state["questions"],
            sources,
            decide=decide or decision_model.decide,
            corpus=corpus_description(options),
        )
        update: dict = {"routes": routes}
        if missing:
            update["problems"] = [
                "Not available here, so not searched: " + ", ".join(missing) + "."
            ]
        return update

    return route
