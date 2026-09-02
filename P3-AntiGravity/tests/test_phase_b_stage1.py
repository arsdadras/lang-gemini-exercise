"""Unit test for Phase B Stage 1: Sandbox Test Execution."""
import sys
from pathlib import Path

# Add reference folder to sys.path for direct import
ref_path = str(Path(__file__).resolve().parents[1] / "reference")
if ref_path not in sys.path:
    sys.path.append(ref_path)

from output_schemas import TestSuite, TestCase, TestExecutionResult
from state import CodeReviewState
from nodes import execute_tests

def test_execute_tests_success():
    sample_code = "def multiply(a: int, b: int) -> int:\n    return a * b\n"
    sample_test = "from tested_module import multiply\ndef test_multiply():\n    assert multiply(2, 4) == 8\n"
    
    state: CodeReviewState = {
        "code": sample_code,
        "language": "python",
        "file_path": "math_ops.py",
        "review": None,
        "tests": TestSuite(framework="pytest", test_code=sample_test, test_cases=[TestCase(name="test_multiply", description="basic test", target_function="multiply")]),
        "test_execution": None,
        "error": None,
    }
    
    result = execute_tests(state)
    assert result["test_execution"] is not None
    assert result["test_execution"].passed is True
    assert result["test_execution"].status == "passed"

def test_execute_tests_failure():
    sample_code = "def multiply(a: int, b: int) -> int:\n    return a * b\n"
    # Intentional failing assertion
    sample_test = "from tested_module import multiply\ndef test_multiply():\n    assert multiply(2, 4) == 999\n"
    
    state: CodeReviewState = {
        "code": sample_code,
        "language": "python",
        "file_path": "math_ops.py",
        "review": None,
        "tests": TestSuite(framework="pytest", test_code=sample_test, test_cases=[]),
        "test_execution": None,
        "error": None,
    }
    
    result = execute_tests(state)
    assert result["test_execution"] is not None
    assert result["test_execution"].passed is False
    assert result["test_execution"].status == "failed"
