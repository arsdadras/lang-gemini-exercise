"""Configuration constants for the P4 Sandbox / Interpreter agent."""

from pathlib import Path

from agentlab.configs.paths_config import OUT_DIR

DEFAULT_SANDBOX_DIR: Path = OUT_DIR / "sandbox"
DEFAULT_DELIVERABLES_DIR: Path = DEFAULT_SANDBOX_DIR / "deliverables"

DEFAULT_EXECUTE_TIMEOUT: int = 60
DEFAULT_MAX_OUTPUT_BYTES: int = 100_000
DEFAULT_VIRTUAL_MODE: bool = True
DEFAULT_THREAD_ID: str = "interpreter_session_001"

# Tools that pause for human approval when the interpreter runs interactively.
DEFAULT_INTERRUPT_TOOLS: tuple[str, ...] = ("execute",)

# The only environment variables LLM-driven shell commands can see. Everything
# else, in particular every API key loaded from .env, is withheld.
SANDBOX_ENV_ALLOWLIST: tuple[str, ...] = (
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "SYSTEMDRIVE",
    "WINDIR",
    "COMSPEC",
    "TEMP",
    "TMP",
    "HOME",
    "USERPROFILE",
    "LANG",
    "VIRTUAL_ENV",
    "PYTHONIOENCODING",
)
