"""Configuration constants for P4 Sandbox / Interpreter Agent."""

from pathlib import Path

# Repository root anchor: core/configs/interpreter.py -> repo root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]
DEFAULT_SANDBOX_DIR: Path = REPO_ROOT / "out" / "sandbox"

DEFAULT_EXECUTE_TIMEOUT: int = 60
DEFAULT_MAX_OUTPUT_BYTES: int = 100_000
DEFAULT_INHERIT_ENV: bool = True
DEFAULT_VIRTUAL_MODE: bool = True
