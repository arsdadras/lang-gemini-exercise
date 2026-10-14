"""Record current git HEAD as the latest reviewed checkpoint for the Consultant role."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_PATH = ROOT / "mentor" / ".consultant_checkpoint.json"


def record_checkpoint(
    checkpoint_path: Path = CHECKPOINT_PATH,
    summary: str = "",
    root_dir: Path = ROOT,
) -> str:
    """Save current HEAD commit to checkpoint_path."""
    head_rev = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=root_dir,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    data = {
        "last_consulted_commit": head_rev,
        "timestamp": datetime.now(UTC).isoformat(),
        "summary": summary or f"Checkpoint recorded at {head_rev}",
    }
    checkpoint_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return head_rev


def main() -> int:
    summary = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    head = record_checkpoint(summary=summary)
    print(
        f"Recorded consultant checkpoint at {head} -> {CHECKPOINT_PATH.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
