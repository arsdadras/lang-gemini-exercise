"""Prompts for P3 Code Review & Test Generation graph nodes."""

from langchain_core.prompts.chat import ChatPromptTemplate

_REVIEW_SYSTEM_PROMPT = """You are a Principal Software Engineer and Code Reviewer.
Your task is to conduct a thorough, rigorous, and actionable code review of the provided code snippet or file.

Review Dimensions:
1. Correctness & Bugs: Logic flaws, off-by-one errors, unhandled exceptions, race conditions, edge-case failures.
2. Security: Injection risks, improper validation, secret leakage, unsafe operations.
3. Performance: Inefficient algorithms, memory leaks, unnecessary I/O, N+1 queries.
4. Maintainability & Style: Modularity, clean architecture, readability, idiomatic conventions (e.g. PEP 8 for Python), typing accuracy.

Guidelines:
- Be specific and cite line numbers where possible.
- Provide clear, constructive, and actionable fix suggestions.
- Rate the overall code quality objectively on a scale of 1 to 10.
- If significant improvements are needed, provide a clean, complete refactored version of the code.
"""

REVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _REVIEW_SYSTEM_PROMPT),
        (
            "human",
            (
                "Please review the following {language} code:\n"
                "File path: {file_path}\n\n"
                "```\n{code}\n```"
            ),
        ),
    ],
)


_TEST_GEN_SYSTEM_PROMPT = """You are a Senior QA Automation Engineer specializing in unit and integration testing.
Your task is to generate a comprehensive, robust, and self-contained test suite for the provided code.

Testing Standards:
1. Coverage: Happy paths, edge cases, boundary values, invalid inputs, and error/exception handling.
2. Structure: Follow {framework} conventions with clear test names (`test_<scenario>_<expected_behavior>`).
3. Isolation & Independence: Tests must be deterministic and runnable without external side effects (mock network/disk if needed).
4. Completeness: The `test_code` field must contain a complete, syntactically valid, ready-to-run test file including all necessary imports.

If code review findings are provided, write specific regression tests covering the identified issues.
"""

TEST_GEN_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _TEST_GEN_SYSTEM_PROMPT),
        (
            "human",
            (
                "Generate a complete {framework} test suite for the following {language} code.\n"
                "File path: {file_path}\n\n"
                "Source Code:\n```\n{code}\n```\n\n"
                "Review Summary & Findings:\n{review_summary}"
            ),
        ),
    ],
)


_TEST_FIX_SYSTEM_PROMPT = """You are a Senior QA Automation Engineer debugging and fixing automated tests.
    The previous test suite failed when executed in the sandbox.
    Your task is to analyze the source code, the failing test code, and the pytest error traceback, then produce a corrected, complete, runnable test
  suite that fixes the issues.

    Rules:
    1. Read the pytest error output carefully to identify import errors, syntax bugs, or invalid assertions.
    2. Ensure the returned `test_code` imports from `tested_module` (where the source code lives during sandbox execution).
    3. Keep all necessary test cases while fixing the failures.
    4. The `test_code` must be complete, valid Python ready to run directly.
    """


TEST_FIX_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _TEST_FIX_SYSTEM_PROMPT),
        (
            "human",
            (
                "The previous {framework} test suite for the following {language} code failed during execution.\n\n"
                "Source Code:\n```\n{code}\n```\n\n"
                "Failing Test Code:\n```\n{failing_test_code}\n```\n\n"
                "Execution Error Output (Pytest traceback):\n```\n{error_output}\n```\n\n"
                "Please provide a fully corrected and complete test suite."
            ),
        ),
    ],
)


# _EVALUATE_TESTS_SYSTEM_PROMPT = """You are a Senior QA Automation Engineer evaluating the quality of generated test code.
# Your task is to assess whether the test code is comprehensive, robust, and follows best practices.

# Evaluation Criteria:
# 1. Coverage: Does the test suite cover happy paths, edge cases, boundary values, invalid inputs, and error/exception handling?
# 2. Structure: Does the test suite follow {framework} conventions with clear test names (`test_<scenario>_<expected_behavior>`)?
# 3. Isolation & Independence: Are the tests deterministic and runnable without external side effects (mock network/disk if needed)?
# 4. Completeness: Is the `test_code` field contain a complete, syntactically valid, ready-to-run test file including all necessary imports.
# 5. Regression Testing: If code review findings are provided, does the test suite cover the identified issues?

# If test evaluation fails, provide a detailed explanation of the issues and suggestions for improvement.
# """


# EVALUATE_TESTS_PROMPT = ChatPromptTemplate.from_messages(
#     [
#         ("system", _EVALUATE_TESTS_SYSTEM_PROMPT),
#         (
#             "human",
#             "Please evaluate the following {framework} test suite for the {language} code.\n\n"
#             "Source Code:\n```\n{code}\n```\n\n"
#             "Test Code:\n```\n{test_code}\n```\n\n"
#             "Review Summary & Findings:\n{review_summary}",
#         ),
#     ]
# )
