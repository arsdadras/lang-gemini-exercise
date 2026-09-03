"""Unit tests for P4 Interpreter Agent components and execution tools."""

from agents.interpreter import make_interpreter_agent
from prompts.agents import build_interpreter_agent_prompt
from tools.interpreter import SafePythonREPL, make_interpreter_tool, python_interpreter


def test_safe_repl_persistence():
    repl = SafePythonREPL()
    repl.run("x = 10; y = 20")
    res = repl.run("x + y")
    assert "30" in res


def test_safe_repl_auto_eval():
    repl = SafePythonREPL()
    res = repl.run("numbers = [1, 2, 3]; len(numbers)")
    assert "3" in res


def test_safe_repl_traceback():
    repl = SafePythonREPL()
    res = repl.run("1 / 0")
    assert "ZeroDivisionError" in res


def test_safe_repl_dedent_and_markdown():
    repl = SafePythonREPL()
    code_with_markdown = """```python
    val = 100
    val * 2
    ```"""
    res = repl.run(code_with_markdown)
    assert "200" in res


def test_tool_invocation():
    res = python_interpreter.invoke({"code": "msg = 'ok'; msg.upper()"})
    assert "'OK'" in res


def test_factory_tool_isolation():
    repl1 = SafePythonREPL()
    repl2 = SafePythonREPL()

    tool1 = make_interpreter_tool(repl1)
    tool2 = make_interpreter_tool(repl2)

    tool1.invoke({"code": "user1_val = 99"})
    res2 = tool2.invoke({"code": "user1_val"})
    assert "NameError" in res2


def test_prompt_builder():
    prompt = build_interpreter_agent_prompt()
    assert "Interpreter Agent" in prompt
    assert "python_interpreter" in prompt


def test_agent_factory():
    agent = make_interpreter_agent()
    assert agent is not None
