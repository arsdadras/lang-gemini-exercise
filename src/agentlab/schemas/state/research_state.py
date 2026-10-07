"""Graph state for P1's research graph: plan, one agent run per sub-question, claim check."""

import operator
from typing import Annotated, NotRequired, TypedDict

from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import ResearchDraft, ResearchReport


def merge_pages(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    """Reducer for ``pages``: the parallel runs' pages, one dict keyed by URL."""
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
    drafts: NotRequired[Annotated[list[ResearchDraft], operator.add]]
    pages: NotRequired[Annotated[dict[str, str], merge_pages]]
    """Every page the runs actually read (URL to text): the claim check's evidence."""
    problems: NotRequired[Annotated[list[str], operator.add]]
    """Everything lost on the way, in words: becomes the envelope's ``reason``."""
    report: NotRequired[ResearchReport]


class SubQuestionState(TypedDict):
    """What ``Send`` hands one run of the research node."""

    question: str
    label: str
    """Prefix for this run's problems: the quoted question, or empty for a single run."""
