"""Graph state for P1's research graph: plan, route, one agent run per sub-question, claim check."""

import operator
from typing import Annotated, NotRequired, TypedDict

from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ResearchDraft,
    ResearchReport,
    SourceKind,
    join_text,
)


def merge_pages(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    """Reducer for ``pages``: the parallel runs' documents, one dict keyed by URL.

    Two runs that read different parts of one file both keep their part (``join_text``).
    """
    merged = dict(left)
    for url, text in right.items():
        merged[url] = join_text(merged[url], text) if url in merged else text
    return merged


def merge_kinds(
    left: dict[str, SourceKind], right: dict[str, SourceKind]
) -> dict[str, SourceKind]:
    """Reducer for ``kinds``: a URL's kind is the same in every run."""
    return {**left, **right}


class ResearchState(TypedDict):
    """State for researching one topic.

    ``drafts``, ``pages``, and ``problems`` have reducers because the sub-question runs write
    them in parallel; every other field has one writer.
    """

    topic: str
    options: ResearchOptions | None
    questions: NotRequired[list[str]]
    """The sub-questions researched: the topic itself when there is no plan."""
    cut: NotRequired[list[str]]
    """Sub-questions the plan's cap left out; reported, never dropped silently."""
    routes: NotRequired[dict[str, list[str]]]
    """The sources the router picked for each sub-question (``research_sources@1``)."""
    drafts: NotRequired[Annotated[list[ResearchDraft], operator.add]]
    pages: NotRequired[Annotated[dict[str, str], merge_pages]]
    """Every document the runs' source tools returned (URL to text): the claim check's evidence."""
    kinds: NotRequired[Annotated[dict[str, SourceKind], merge_kinds]]
    """Each document's kind (web, academic, corpus), keyed like ``pages``."""
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
