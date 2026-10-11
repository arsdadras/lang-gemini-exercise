"""Filesystem locations shared across projects.

Anchored to this file's location, so every path resolves the same way no matter
which working directory an app is launched from.
"""

from pathlib import Path

PACKAGE_ROOT: Path = Path(__file__).resolve().parents[1]
PROJECT_ROOT: Path = PACKAGE_ROOT.parents[1]

# Runtime output (gitignored): sandbox workspace, checkpoints, vector index.
OUT_DIR: Path = PROJECT_ROOT / "out"
STATE_DIR: Path = OUT_DIR / "state"
CHROMA_DIR: Path = PROJECT_ROOT / ".chroma_index"

# Labeled decision-point datasets for the eval-lite harness (utils/eval_util.py).
EVAL_DATASETS_DIR: Path = PROJECT_ROOT / "evals" / "datasets"

# Packaged, read-only agent resources.
SKILLS_RESOURCES_DIR: Path = PACKAGE_ROOT / "resources" / "skills"

# Delegated one-shot runs (subagent threads nobody resumes) live apart from every app's sessions.
DELEGATIONS_APP: str = "delegations"


def checkpoint_db_path(app: str) -> Path:
    """The checkpoint database of one app: its session list shows only its own threads."""
    return STATE_DIR / f"{app}_checkpoints.db"
