"""Sandbox execution utilities for safe local test running."""

import subprocess
import sys
import tempfile
from pathlib import Path
from output_schemas.code_review import TestExecutionResult


def run_tests_in_sandbox(
    code: str,
    test_code: str,
    timeout_seconds: int = 15,
) -> TestExecutionResult:
    """Execute target code and generated pytest tests in an isolated temporary directory.

    Args:
        code: The Python source code under test.
        test_code: The Python test code to execute.
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
        except Exception as e:
            return TestExecutionResult(
                status="error",
                passed=False,
                exit_code=-1,
                output=f"Sandbox execution failed: {e}",
            )
