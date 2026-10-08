"""Model-router constants: which tiers it chooses among, how it reads Jev's answers (ADR-0031).

The router asks a decision model how demanding a task is and what a mistake would cost; code
maps the answers to one of the catalog's tiers. Every threshold here is provisional until the
labeled set (``evals/datasets/model_routes.json``) is measured per decider version
(``library/architecture/decision-models.md``).
"""

QUESTION_SET = "model_route@1"

# The tiers the router may choose, cheapest first. ``opensource`` is left out until it is
# measured (RSK-08); the opt-in tiers (test-mode rungs, ``local``) never are routed to.
ROUTED_TIERS: tuple[str, ...] = ("low", "medium", "high")

# What the router uses when the decider fails or is unsure of everything: the middle, because a
# wrong answer costs a little either way, where "low" risks a poor answer and "high" the bill.
FALLBACK_TIER = "medium"

# The decider reads this as the policy. Model names are filled in from the catalog, so a model
# change in ``models_config`` is a change here too, with no second list to keep in step.
TIER_PROFILES: dict[str, str] = {
    "low": (
        "Fast, cheap models. Good at extraction, classification, rewording, formatting, short "
        "answers from text that is given, and simple lookups. Weak at several dependent steps, "
        "subtle code, and long chains of reasoning."
    ),
    "medium": (
        "Balanced models. Good at ordinary coding, summarizing and combining several passages, "
        "analysis in a few steps, writing, and tool use. Weak at novel design, subtle bugs, and "
        "reasoning where an early slip compounds."
    ),
    "high": (
        "Frontier models, slow and the most expensive. Good at hard reasoning, architecture and "
        "design, subtle debugging, long-horizon planning, and work where a mistake is costly. "
        "Wasted on anything a cheaper model does as well."
    ),
}

# How demanding the task is for the model that will do it: the levels of the ``difficulty``
# score, in order (level 0 first).
DIFFICULTY_LEVELS: tuple[str, ...] = (
    "Trivial: a lookup, a rewording, a yes or no, a format change, a one-line answer.",
    (
        "Ordinary: one clear step or a few independent ones: summarize a passage, answer from "
        "the text given, a small edit, a routine function."
    ),
    (
        "Demanding: several dependent steps, combining sources, non-trivial code or analysis, "
        "tight constraints to respect together."
    ),
    (
        "Expert: deep multi-step reasoning, a design with trade-offs, subtle debugging, a "
        "proof, or work where an early slip ruins everything after it."
    ),
)

STAKES_QUESTION = (
    "Would a wrong or careless answer be costly or hard to undo: changes to production or to "
    "data, money, security, legal or medical advice, or something a person will rely on without "
    "checking?"
)

# "low" needs this much probability on the two easy levels together: going down a tier is the
# risky move, so it takes evidence, and a doubtful task stays in the middle.
LOW_MASS = 0.8
# "high" needs this much on the expert level alone: hard is earned, never assumed.
HIGH_MASS = 0.5
# At or above this probability of "costly", the tier is at least ``STAKES_FLOOR_TIER``. Stakes
# lift a task off "low"; they never buy "high" alone.
STAKES_THRESHOLD = 0.5
STAKES_FLOOR_TIER = "medium"

# A task text longer than this goes to the decider as its opening plus, mostly, its end (the
# ask is usually last), and the router never routes it below ``LARGE_TASK_FLOOR_TIER``.
TASK_MAX_CHARS = 6_000
TASK_HEAD_CHARS = 2_000
LARGE_TASK_CHARS = 120_000  # about 30k tokens
LARGE_TASK_FLOOR_TIER = "medium"
