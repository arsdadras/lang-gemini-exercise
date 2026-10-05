"""P1 research constants shared by the page reader, the claim check, and the research budgets."""

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
