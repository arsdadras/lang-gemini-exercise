"""Configuration constants for the P5 memory-rich personal assistant."""

from pathlib import Path

from agentlab.configs.paths_config import SKILLS_RESOURCES_DIR

# Virtual filesystem routes (see utils/memory_backend_util.py).
MEMORIES_ROUTE_PREFIX: str = "/memories/"
DEFAULT_USER_PROFILE_PATH: str = "/memories/user_profile.md"
SKILLS_ROUTE_PREFIX: str = "/skills/"
SKILLS_DIR: Path = SKILLS_RESOURCES_DIR / "personal_assistant"

# CLI session defaults.
DEFAULT_USER_ID: str = "default_user"
DEFAULT_ASSISTANT_THREAD_ID: str = "pa_session_001"

# In Phase A, gemini-3.5-flash-lite claimed memory writes without calling any
# tool; gpt-5.6-luna (same tier) didn't, so the assistant pins that provider.
DEFAULT_ASSISTANT_TIER: str = "low"
DEFAULT_ASSISTANT_PROVIDER: str = "openai"
