"""Configuration constants for the P5 memory-rich personal assistant."""

from pathlib import Path

from agentlab.configs.paths_config import SKILLS_RESOURCES_DIR, STATE_DIR

# Virtual filesystem routes (see utils/memory_backend_util.py).
MEMORIES_ROUTE_PREFIX: str = "/memories/"
DEFAULT_USER_PROFILE_PATH: str = "/memories/user_profile.md"
SKILLS_ROUTE_PREFIX: str = "/skills/"
# Skills published by the skill designer, shared by every user (stored in the long-term store).
PUBLISHED_SKILLS_ROUTE_PREFIX: str = "/published-skills/"
PUBLISHED_SKILLS_NAMESPACE: tuple[str, str] = ("shared", "skills")
SKILLS_DIR: Path = SKILLS_RESOURCES_DIR / "personal_assistant"

# Durable state of the P5 app, apart from the other apps' shared checkpoint database.
ASSISTANT_CHECKPOINT_DB_PATH: Path = STATE_DIR / "personal_assistant_checkpoints.db"
ASSISTANT_STORE_DB_PATH: Path = STATE_DIR / "personal_assistant_store.db"

# A conversation is consolidated mid-way once its unconsolidated transcript reaches this size,
# so a long thread is consolidated in segments instead of one huge transcript.
LONG_THREAD_CONSOLIDATION_CHARS: int = 8000

# CLI session defaults.
DEFAULT_USER_ID: str = "default_user"
DEFAULT_ASSISTANT_THREAD_ID: str = "pa_session_001"

# In Phase A, gemini-3.5-flash-lite claimed memory writes without calling any
# tool; gpt-5.6-luna (same tier) didn't, so the assistant pins that provider. A qualitative
# observation with no run count (EV-undated-flash-lite-false-memory-claims).
DEFAULT_ASSISTANT_TIER: str = "low"
DEFAULT_ASSISTANT_PROVIDER: str = "openai"

# The memory consolidator must notice a new fact that contradicts an old one under another
# heading (a new diet vs. an old food preference). Measured on 2026-09-19, 3 runs per case:
# claude-sonnet-5 resolved 6/6, gpt-5.6-terra 4/6; gemini-3.8-flash was rate-limited
# (EV-2026-09-19-consolidator-model-comparison, reconstructed from this comment; not re-run).
CONSOLIDATOR_TIER: str = "medium"
CONSOLIDATOR_PROVIDER: str = "anthropic"
