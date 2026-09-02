"""Sandbox execution utilities for safe test running across execution backends."""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

from output_schemas.code_review import TestExecutionResult

SandboxType = Literal["local", "container", "cloud"]


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
