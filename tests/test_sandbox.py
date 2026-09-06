"""Unit tests for SandboxBackend path normalization."""

import tempfile
from pathlib import Path

import pytest
from output_schemas.interpreter_output_schema import ArtifactMetadata, ExecutionManifest
from utils.sandbox_util import SandboxBackend, get_artifact_path, list_sandbox_artifacts


def test_sandbox_backend_resolve_path_normalization():
    """Verify SandboxBackend normalizes virtual paths to sandbox root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = SandboxBackend(root_dir=Path(tmpdir), virtual_mode=True)

        assert backend._resolve_path("/workspace/test.py") == Path(tmpdir) / "test.py"
        assert backend._resolve_path("workspace/test.py") == Path(tmpdir) / "test.py"
        assert backend._resolve_path("test.py") == Path(tmpdir) / "test.py"
        assert backend._resolve_path("/workspace") == Path(tmpdir)
        assert backend._resolve_path("workspace") == Path(tmpdir)
        assert (
            backend._resolve_path("/workspace/artifacts/report.csv")
            == Path(tmpdir) / "artifacts" / "report.csv"
        )


def test_list_sandbox_artifacts_and_path_validation():
    """Verify listing artifacts and path traversal enforcement."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sb = Path(tmpdir)
        art_dir = sb / "artifacts"
        art_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy artifacts and root script
        (sb / "runner.py").write_text("print('script')", encoding="utf-8")
        (art_dir / "data.csv").write_text("a,b\n1,2", encoding="utf-8")
        (art_dir / "chart.png").write_bytes(b"\x89PNG\r\n\x1a\n")

        artifacts = list_sandbox_artifacts(sandbox_dir=sb)
        assert len(artifacts) == 2
        paths = {a["path"] for a in artifacts}
        assert "artifacts/data.csv" in paths
        assert "artifacts/chart.png" in paths
        assert "runner.py" not in paths

        # Safe resolution
        resolved = get_artifact_path("artifacts/data.csv", sandbox_dir=sb)
        assert resolved == art_dir / "data.csv"

        # Traversal protection
        with pytest.raises(ValueError, match="Path traversal attempt"):
            get_artifact_path("../sensitive.txt", sandbox_dir=sb)


def test_execution_manifest_schema():
    """Verify ExecutionManifest and ArtifactMetadata instantiation."""
    manifest = ExecutionManifest(
        summary="Generated synthetic revenue dataset and histogram plot",
        artifacts=[
            ArtifactMetadata(
                name="sales.csv",
                path="artifacts/sales.csv",
                artifact_type="csv",
                description="Synthetic Q3 transactions",
            ),
            ArtifactMetadata(
                name="sales_hist.png",
                path="artifacts/sales_hist.png",
                artifact_type="chart",
                description="Histogram distribution of sales",
            ),
        ],
        success=True,
    )
    assert len(manifest.artifacts) == 2
    assert manifest.artifacts[0].artifact_type == "csv"
    assert manifest.artifacts[1].name == "sales_hist.png"
    assert manifest.success is True
