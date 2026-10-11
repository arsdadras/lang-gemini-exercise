"""Timeouts, in seconds, for every external client: a hung call fails instead of waiting forever.

A timeout is a transient failure (``utils/failure_util.py``): the node or tool retry layer
retries it once over, and a specialist boundary reports what remains as a ``failed`` envelope.
"""

# One request to a hosted chat model, structured output and reasoning models included. The
# provider SDKs apply it per connect, read, and write, so a response that streams slowly is
# not cut off, but a connection that goes silent is.
CHAT_MODEL_TIMEOUT_SECONDS: float = 120.0
# Per-provider SDK retry cap before falling over to the backup gateway (with_fallbacks /
# ModelFallbackMiddleware). Default SDK max_retries=2 meant 3 x 120 s = 360 s on one silent host.
CHAT_MODEL_MAX_RETRIES: int = 1
# The local tier takes 90-360 s per structured call (EV-2026-09-23-local-ollama-qwen).
LOCAL_MODEL_TIMEOUT_SECONDS: float = 600.0
# One embedding request (a paced batch of EMBED_BATCH_SIZE chunks).
EMBEDDING_TIMEOUT_SECONDS: float = 30.0
# One Tavily search request.
WEB_SEARCH_TIMEOUT_SECONDS: float = 20.0

# One Exa academic search request (it returns each paper's text with the result).
ACADEMIC_SEARCH_TIMEOUT_SECONDS: float = 30.0

# A decision (Jev) answers in about 0.5 s end to end; the ceiling is for a bad network day.
DECISION_MODEL_TIMEOUT_SECONDS: float = 10.0
