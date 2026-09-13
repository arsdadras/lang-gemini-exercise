"""Tests for sandbox helpers: path aliasing, environment allowlist, artifacts."""

from pathlib import Path

import pytest

from agentlab.utils.sandbox_util import (
    SandboxBackend,
    build_sandbox_env,
    diff_sandbox_artifacts,
    get_artifact_path,
    list_sandbox_artifacts,
    snapshot_sandbox_artifacts,
)


def test_workspace_alias_maps_to_sandbox_root(tmp_path: Path) -> None:
    backend = SandboxBackend(root_dir=tmp_path, virtual_mode=True)
    root = tmp_path.resolve()

    assert backend._resolve_path("/workspace/test.py") == root / "test.py"
    assert backend._resolve_path("workspace/test.py") == root / "test.py"
    assert backend._resolve_path("test.py") == root / "test.py"
    assert backend._resolve_path("/workspace") == root
    assert backend._resolve_path("workspace") == root
    assert backend._resolve_path("/workspace/artifacts/report.csv") == root / "artifacts" / "report.csv"
    assert backend._resolve_path("my_workspace/test.py") == root / "my_workspace" / "test.py"


def test_build_sandbox_env_keeps_only_allowlisted_names() -> None:
    source = {"PATH": "bin", "SystemRoot": "C:\\Windows", "GITHUB_ACCESS_TOKEN": "secret"}

    env = build_sandbox_env(allowlist=("PATH", "SYSTEMROOT"), source=source)

    assert env == {"PATH": "bin", "SystemRoot": "C:\\Windows"}


def test_sandbox_shell_cannot_read_process_secrets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTLAB_FAKE_SECRET", "leaked")
    backend = SandboxBackend(root_dir=tmp_path, virtual_mode=True, env=build_sandbox_env())

    result = backend.execute("python -c \"import os; print(os.getenv('AGENTLAB_FAKE_SECRET'))\"")

    assert result.exit_code == 0
    assert "leaked" not in result.output
    assert "None" in result.output


def test_list_sandbox_artifacts_and_path_validation(tmp_path: Path) -> None:
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    (tmp_path / "runner.py").write_text("print('script')", encoding="utf-8")
    (artifacts_dir / "data.csv").write_text("a,b\n1,2", encoding="utf-8")
    (artifacts_dir / "chart.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    by_path = {artifact.path: artifact for artifact in list_sandbox_artifacts(tmp_path)}

    assert set(by_path) == {"artifacts/data.csv", "artifacts/chart.png"}
    assert by_path["artifacts/data.csv"].artifact_type == "csv"
    assert by_path["artifacts/chart.png"].artifact_type == "chart"
    assert by_path["artifacts/data.csv"].size_bytes is not None
    assert get_artifact_path("artifacts/data.csv", tmp_path) == (artifacts_dir / "data.csv").resolve()
    with pytest.raises(ValueError, match="Path traversal attempt"):
        get_artifact_path("../sensitive.txt", tmp_path)


def test_diff_sandbox_artifacts_reports_new_and_modified(tmp_path: Path) -> None:
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    (artifacts_dir / "unchanged.txt").write_text("same", encoding="utf-8")
    (artifacts_dir / "will_change.txt").write_text("before", encoding="utf-8")

    before = snapshot_sandbox_artifacts(tmp_path)
    (artifacts_dir / "will_change.txt").write_text("after, longer content", encoding="utf-8")
    (artifacts_dir / "brand_new.csv").write_text("a,b\n1,2", encoding="utf-8")

    changes = {artifact.path: tag for tag, artifact in diff_sandbox_artifacts(before, tmp_path)}

    assert changes == {
        "artifacts/will_change.txt": "modified",
        "artifacts/brand_new.csv": "new",
    }
