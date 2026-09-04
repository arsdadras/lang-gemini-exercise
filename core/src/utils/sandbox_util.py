"""Sandbox execution utilities for safe test running across execution backends."""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

from deepagents.backends import LocalShellBackend
from deepagents.backends.protocol import ExecuteResponse
from output_schemas.code_review_output_schema import TestExecutionResult

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
