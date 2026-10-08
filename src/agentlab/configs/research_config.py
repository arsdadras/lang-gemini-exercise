"""P1 research constants: the page reader, the claim check, the budgets, and the sources."""

from dataclasses import dataclass

# What the agent reads of a page and what the claim check is shown. One number for both: a claim
# the check can't see is a claim it can never support.
MAX_PAGE_CHARS = 12_000


@dataclass(frozen=True)
class ResearchBudget:
    """What one research run may spend (R1 topic 2, closes MN-023's unbounded reads and claims).

    ``searches`` and ``reads`` are per sub-question run; ``claims`` caps the merged report.
    """

    sub_questions: int
    searches: int
    reads: int
    claims: int


# Provisional numbers, to be measured on real broad runs (MN-023).
DEPTH_BUDGETS: dict[str, ResearchBudget] = {
    "quick": ResearchBudget(sub_questions=1, searches=2, reads=3, claims=6),
    "standard": ResearchBudget(sub_questions=3, searches=5, reads=8, claims=15),
    "deep": ResearchBudget(sub_questions=5, searches=6, reads=10, claims=30),
}


# Sources (R1 topic 3). Each source is a kind of evidence and the tools that fetch it; the router
# (``research_sources@1``) picks the sources a sub-question needs, and the agent sees only theirs.
SOURCE_TOOLS: dict[str, tuple[str, ...]] = {
    "web": ("web_search", "read_page"),
    "academic": ("academic_search",),
    "documents": ("search_documents",),
}

# Academic search: Exa's research-paper index (arXiv, journals, conference papers), which returns
# each paper's text with the result, so no separate read step is needed.
EXA_SEARCH_URL = "https://api.exa.ai/search"
EXA_KEY_ENV = "EXA_API_KEY"
ACADEMIC_RESULTS = 5
# What the agent and the claim check see of one paper: smaller than a web page, because five
# papers arrive in one result.
ACADEMIC_TEXT_CHARS = 3_000

# Documents: this project's own docs and code through P2's index by default, or the files a user
# gives one run (plain text and Markdown only: no extraction or conversion from other formats).
CORPUS_RESULTS = 6
DOCUMENT_SUFFIXES: tuple[str, ...] = (".txt", ".md")
PROJECT_DOCUMENTS = (
    "agentlab, this teaching project on agentic AI: its design decisions, architecture, "
    "conventions, code, roadmap, and lessons"
)
