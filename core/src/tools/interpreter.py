"""Stateful Python REPL execution tool for data manipulation and analysis."""

import ast
import contextlib
import io
import textwrap
import traceback
from typing import Any

from langchain_core.tools import tool


class SafePythonREPL:
    """Stateful, in-process Python execution environment."""

    def __init__(self, max_output_chars: int = 4000) -> None:
        self.max_output_chars = max_output_chars
        self.globals: dict[str, Any] = {"__builtins__": __builtins__}

    def reset(self) -> None:
        """Reset the execution namespace to a clean state."""
        self.globals = {"__builtins__": __builtins__}

    def run(self, code: str) -> str:
        """Execute Python code in the persistent namespace and capture output."""
        buffer = io.StringIO()
        try:
            # Strip common LLM artifacts: markdown fences first, then dedent leading indentation
            clean_code = code.strip()
            if clean_code.startswith("```"):
                lines = clean_code.splitlines()
                if lines and lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                clean_code = "\n".join(lines)
            clean_code = textwrap.dedent(clean_code).strip()

            tree = ast.parse(clean_code)
            if not tree.body:
                return "Empty code block."

            # Jupyter-style evaluation: evaluate the final expression if present
            last_stmt = tree.body[-1]
            eval_node = None
            if isinstance(last_stmt, ast.Expr):
                eval_node = ast.Expression(last_stmt.value)
                tree.body.pop()

            exec_code = compile(tree, filename="<repl>", mode="exec") if tree.body else None

            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                if exec_code:
                    exec(exec_code, self.globals)  # noqa: S102
                if eval_node:
                    eval_code = compile(eval_node, filename="<repl>", mode="eval")
                    result = eval(eval_code, self.globals)
                    if result is not None:
                        print(repr(result))

            output = buffer.getvalue()
            if not output.strip():
                return "Code executed successfully with no output."

            if len(output) > self.max_output_chars:
                return (
                    output[: self.max_output_chars]
                    + f"\n[Output truncated: exceeded {self.max_output_chars} characters]"
                )
            return output

        except Exception:  # noqa: BLE001
            # Return limited traceback so the agent can inspect and self-correct
            return traceback.format_exc(limit=3)


# Global default REPL instance for the session
_session_repl = SafePythonREPL()


@tool("python_interpreter")
def python_interpreter(code: str) -> str:
    """Execute Python code in a persistent stateful REPL environment.

    State (variables, functions, imported modules) persists across multiple calls.
    If the final statement is an expression, its evaluated representation is returned.
    Standard output from print() and execution error tracebacks are captured and returned.
    Use this for data analysis, computations, and verifying logic.
    """
    return _session_repl.run(code)


def make_interpreter_tool(repl: SafePythonREPL | None = None):
    """Factory creating an isolated python_interpreter tool instance bound to a given REPL."""
    scoped_repl = repl or SafePythonREPL()

    @tool("python_interpreter")
    def _scoped_python_interpreter(code: str) -> str:
        """Execute Python code in a persistent stateful REPL environment.

        State (variables, functions, imported modules) persists across multiple calls.
        If the final statement is an expression, its evaluated representation is returned.
        Standard output from print() and execution error tracebacks are captured and returned.
        Use this for data analysis, computations, and verifying logic.
        """
        return scoped_repl.run(code)

    return _scoped_python_interpreter

