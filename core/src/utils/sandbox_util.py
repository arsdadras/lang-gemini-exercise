"""Sandbox execution utilities for safe test running across execution backends."""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

from deepagents.backends import LocalShellBackend
from deepagents.backends.protocol import ExecuteResponse
from output_schemas.code_review_output_schema import TestExecutionResult
from output_schemas.interpreter_output_schema import ArtifactMetadata, ArtifactType

SandboxType = Literal["local", "container", "cloud"]


class SandboxBackend(LocalShellBackend):
    """LocalShellBackend with automatic virtual path normalization.

    Prevents path fragmentation (e.g. LLM writing to `/workspace/script.py`
    while executing `python script.py` in the root sandbox directory).
    All `/workspace/` and `workspace/` prefixes are transparently mapped
    to the root sandbox directory.
    """

    def _resolve_path(self, key: str) -> Path:
        normalized = key.replace("\\", "/")
        if normalized.startswith("/workspace/"):
            normalized = normalized[len("/workspace/") :]
        elif normalized.startswith("workspace/"):
            normalized = normalized[len("workspace/") :]
        elif normalized in {"/workspace", "workspace"}:
            normalized = "."
        return super()._resolve_path(normalized)

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        normalized_command = command.replace("/workspace/", "").replace("workspace/", "")
        return super().execute(normalized_command, timeout=timeout)


def _run_local_sandbox(
    code: str,
    test_code: str,
    timeout_seconds: int,
) -> TestExecutionResult:
    """Execute tests locally in an isolated temporary directory via subprocess."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Write target source code
        src_file = tmp_path / "tested_module.py"
        src_file.write_text(code, encoding="utf-8")

        # Write test code
        test_file = tmp_path / "test_module.py"
        test_file.write_text(test_code, encoding="utf-8")

        try:
            res = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", str(test_file)],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

            is_passed = res.returncode == 0
            status = "passed" if is_passed else "failed"
            full_output = res.stdout + ("\n" + res.stderr if res.stderr else "")

            return TestExecutionResult(
                status=status,
                passed=is_passed,
                exit_code=res.returncode,
                output=full_output,
            )

        except subprocess.TimeoutExpired:
            return TestExecutionResult(
                status="timed_out",
                passed=False,
                exit_code=-1,
                output=f"Test execution timed out after {timeout_seconds} seconds.",
            )
        except Exception as e:  # noqa: BLE001
            return TestExecutionResult(
                status="error",
                passed=False,
                exit_code=-1,
                output=f"Local sandbox execution failed: {e}",
            )


def run_tests_in_sandbox(
    code: str,
    test_code: str,
    sandbox_type: SandboxType = "local",
    timeout_seconds: int = 15,
) -> TestExecutionResult:
    """Execute target code and test suite in a specified sandbox backend.

    Args:
        code: The Python source code under test.
        test_code: The Python test code to execute.
        sandbox_type: Execution backend ("local" | "container" | "cloud").
        timeout_seconds: Maximum allowed seconds for test execution.

    Returns:
        TestExecutionResult with status, pass/fail boolean, exit code, and captured output.
    """
    if not test_code.strip():
        return TestExecutionResult(
            status="error",
            passed=False,
            exit_code=-1,
            output="No test code provided to execute.",
        )

    if sandbox_type == "local":
        return _run_local_sandbox(code, test_code, timeout_seconds)
    elif sandbox_type in ("container", "cloud"):
        return TestExecutionResult(
            status="error",
            passed=False,
            exit_code=-1,
            output=f"Sandbox backend '{sandbox_type}' is planned for P4 (Sandbox / Interpreter Agent).",
        )
    else:
        return TestExecutionResult(
            status="error",
            passed=False,
            exit_code=-1,
            output=f"Unsupported sandbox type: '{sandbox_type}'. Expected 'local', 'container', or 'cloud'.",
        )


def _infer_artifact_type(suffix: str) -> ArtifactType:
    normalized = suffix.lower()
    if normalized == ".csv":
        return "csv"
    if normalized == ".json":
        return "json"
    if normalized in {".png", ".jpg", ".jpeg", ".svg", ".pdf"}:
        return "chart"
    if normalized in {".md", ".markdown"}:
        return "markdown"
    if normalized in {".txt", ".log"}:
        return "text"
    return "other"


def list_sandbox_artifacts(sandbox_dir: Path | None = None) -> list[ArtifactMetadata]:
    """List all deliverable artifacts currently stored in the sandbox artifacts directory."""
    if sandbox_dir is None:
        from configs.interpreter_config import DEFAULT_SANDBOX_DIR

        sandbox_dir = DEFAULT_SANDBOX_DIR

    artifacts_dir = sandbox_dir / "artifacts"
    if not artifacts_dir.exists() or not artifacts_dir.is_dir():
        return []

    artifacts: list[ArtifactMetadata] = []
    for item in sorted(artifacts_dir.rglob("*")):
        if item.is_file():
            stat = item.stat()
            rel_path = item.relative_to(sandbox_dir).as_posix()
            artifacts.append(
                ArtifactMetadata(
                    name=item.name,
                    path=rel_path,
                    artifact_type=_infer_artifact_type(item.suffix),
                    description=f"{item.suffix.upper().lstrip('.')} artifact ({stat.st_size} bytes)",
                    size_bytes=stat.st_size,
                    modified_at=stat.st_mtime,
                )
            )
    return artifacts


def get_artifact_path(relative_path: str, sandbox_dir: Path | None = None) -> Path:
    """Resolve and validate an artifact path within the sandbox, preventing traversal."""
    if sandbox_dir is None:
        from configs.interpreter_config import DEFAULT_SANDBOX_DIR

        sandbox_dir = DEFAULT_SANDBOX_DIR

    artifacts_dir = (sandbox_dir / "artifacts").resolve()
    target = (sandbox_dir / relative_path).resolve()

    if not target.is_relative_to(artifacts_dir):
        msg = f"Path traversal attempt: {relative_path} is outside artifacts directory"
        raise ValueError(msg)
    return target
