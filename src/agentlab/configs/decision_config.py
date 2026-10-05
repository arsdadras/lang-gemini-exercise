"""Decision-model constants: which decider, where it lives, what it costs.

A decision model answers typed questions about a state with a probability per option
(ADR-0021). The model ID is pinned to the versioned snapshot, not the ``jev-latest`` alias,
because thresholds are fitted per model version. The API rejects the short ``jev-1.13``
(HTTP 400, checked 2026-10-05); ``jev-latest`` resolves to ``jev-1.13.0`` today.
"""

DECISION_MODEL_ID = "jev-1.13.0"
DECISION_API_KEY_ENV = "TYPESAFE_API_KEY"
DECISION_BASE_URL = "https://api.typesafe.ai"

# Output is free; input is billed per million tokens (docs.typesafe.ai, read 2026-09-26).
DECISION_USD_PER_MILLION_INPUT_TOKENS = 0.042
