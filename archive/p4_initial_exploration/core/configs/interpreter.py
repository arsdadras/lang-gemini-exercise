"""Configuration constants for the P4 interpreter agent subsystem."""

from pathlib import Path

DEFAULT_INTERPRETER_TIMEOUT: int = 30
MAX_INTERPRETER_OUTPUT_CHARS: int = 4000

DEFAULT_SANDBOX_DIR: Path = Path("out/sandbox")
