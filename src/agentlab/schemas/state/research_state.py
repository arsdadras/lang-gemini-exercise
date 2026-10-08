"""Graph state for P1's research graph: plan, route, one agent run per sub-question, claim check."""

import operator
from typing import Annotated, NotRequired, TypedDict

from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ResearchDraft,
    ResearchReport,
    SourceDocument,
    join_text,
)


def merge_documents(
    left: dict[str, SourceDocument], right: dict[str, SourceDocument]
) -> dict[str, SourceDocument]:
    """Reducer for ``documents``: the parallel runs' documents, one dict keyed by URL.

    Two reads of one URL that returned different parts of it both keep their part
    (``join_text``); the same text read twice is kept once.
    """
    merged = dict(left)
    for url, document in right.items():
        if earlier := merged.get(url):
            document = document.model_copy(
                update={"text": join_text(earlier.text, document.text)}
            )
        merged[url] = document
    return merged


class ResearchState(TypedDict):
    """State for researching one topic.

    ``drafts``, ``documents``, and ``problems`` have reducers because the sub-question runs write
    them in parallel; every other field has one writer.
    """

    topic: str
    options: ResearchOptions | None
    questions: NotRequired[list[str]]
    """The sub-questions researched: the topic itself when there is no plan."""
    cut: NotRequired[list[str]]
    """Sub-questions the plan's cap left out; reported, never dropped silently."""
    routes: NotRequired[dict[str, list[str]]]
    """The sources the router picked for each sub-question (``research_sources@2``)."""
    drafts: NotRequired[Annotated[list[ResearchDraft], operator.add]]
    documents: NotRequired[Annotated[dict[str, SourceDocument], merge_documents]]
    """Every document the runs' source tools returned, keyed by URL: the claim check's evidence."""
    problems: NotRequired[Annotated[list[str], operator.add]]
    """Everything lost on the way, in words: becomes the envelope's ``reason``."""
    report: NotRequired[ResearchReport]


class SubQuestionState(TypedDict):
    """What ``Send`` hands one run of the research node."""

    question: str
    sources: list[str]
    """The sources routed to this sub-question; the run sees only their tools."""
    label: str
    """Prefix for this run's problems: the quoted question, or empty for a single run."""
