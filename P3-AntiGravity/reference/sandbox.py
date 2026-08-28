"""Reference sandbox utility for P3 Code Review."""

from typing import Literal
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from .output_schemas import TestExecutionResult
except ImportError:
    from output_schemas import TestExecutionResult

SandboxType = Literal["local", "container", "cloud"]


def _run_local_sandbox(
    code: str,
    test_code: str,
    timeout_seconds: int,
) -> TestExecutionResult:
    """Execute tests locally in an isolated temporary directory via subprocess."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_file = tmp_path / "tested_module.py"
        src_file.write_text(code, encoding="utf-8")

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
            is_passed = (res.returncode == 0)
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
                output=f"Local sandbox execution failed: {e}",
            )


def run_tests_in_sandbox(
    code: str,
    test_code: str,
    sandbox_type: SandboxType = "local",
    timeout_seconds: int = 15,
) -> TestExecutionResult:
    """Execute target code and test suite in specified sandbox backend."""
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
