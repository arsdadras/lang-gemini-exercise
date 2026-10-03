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
CHECKPOINT_DB_PATH: Path = STATE_DIR / "checkpoints.db"
CHROMA_DIR: Path = PROJECT_ROOT / ".chroma_index"

# Labeled decision-point datasets for the eval-lite harness (utils/eval_util.py).
EVAL_DATASETS_DIR: Path = PROJECT_ROOT / "evals" / "datasets"

# Packaged, read-only agent resources.
SKILLS_RESOURCES_DIR: Path = PACKAGE_ROOT / "resources" / "skills"
