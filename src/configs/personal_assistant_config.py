"""Configuration constants for Project P5: Memory-Rich Personal Assistant."""

from pathlib import Path

# Routing and path constants
MEMORIES_ROUTE_PREFIX: str = "/memories/"
DEFAULT_USER_PROFILE_PATH: str = "/memories/user_profile.md"
SKILLS_ROUTE_PREFIX: str = "/skills/"
SKILLS_NAMESPACE: tuple[str, ...] = ("skills",)
SKILLS_DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data" / "skills"

# Session and tenant defaults
DEFAULT_USER_ID: str = "default_user"
DEFAULT_ASSISTANT_THREAD_ID: str = "pa_session_001"

# Model tiers and providers
DEFAULT_ASSISTANT_TIER: str = "low"
DEFAULT_ASSISTANT_PROVIDER: str = "openai"  # Resolves to gpt-5.6-luna
DEFAULT_CONSOLIDATION_TIER: str = "medium"
