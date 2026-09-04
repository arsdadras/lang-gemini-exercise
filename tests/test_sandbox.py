"""Unit tests for SandboxBackend path normalization."""

import tempfile
from pathlib import Path

from utils.sandbox_util import SandboxBackend


def test_sandbox_backend_resolve_path_normalization():
    """Verify SandboxBackend normalizes virtual paths to sandbox root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = SandboxBackend(root_dir=Path(tmpdir), virtual_mode=True)

        assert backend._resolve_path("/workspace/test.py") == Path(tmpdir) / "test.py"
        assert backend._resolve_path("workspace/test.py") == Path(tmpdir) / "test.py"
        assert backend._resolve_path("test.py") == Path(tmpdir) / "test.py"
        assert backend._resolve_path("/workspace") == Path(tmpdir)
        assert backend._resolve_path("workspace") == Path(tmpdir)
