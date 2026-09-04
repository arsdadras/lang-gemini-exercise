"""Unit tests for P4 Interpreter Agent components and execution tools."""

from agents.interpreter_agent import make_interpreter_agent
from output_schemas.interpreter import AnalysisReport
from prompts.agents import build_interpreter_agent_prompt
from tools.file_ops import make_file_tools
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
    assert "write_file" in prompt
    assert "read_file" in prompt
    assert "list_files" in prompt


def test_agent_factory():
    agent = make_interpreter_agent()
    assert agent is not None


def test_sandbox_file_ops(tmp_path):
    write_tool, read_tool, list_tool = make_file_tools(tmp_path)

    # 1. Write file
    write_res = write_tool.invoke({"file_path": "sub/data.txt", "content": "hello sandbox"})
    assert "Successfully wrote" in write_res

    # 2. Read file
    read_res = read_tool.invoke({"file_path": "sub/data.txt"})
    assert read_res == "hello sandbox"

    # 3. List files
    list_res = list_tool.invoke({"directory": "."})
    assert "sub" in list_res


def test_sandbox_path_traversal_blocked(tmp_path):
    write_tool, _, _ = make_file_tools(tmp_path)
    res = write_tool.invoke({"file_path": "../../dangerous.txt", "content": "bad"})
    assert "Security Error" in res or "escapes" in res


def test_analysis_report_schema():
    report = AnalysisReport(
        title="Sales Q1",
        executive_summary="Strong revenue growth.",
        metrics={"total_revenue": 150000.0, "active_reps": 12},
        insights=["Engineering drove highest deal volume."],
        artifacts_created=["q1_sales.csv"],
        recommendations=["Increase marketing budget."],
    )
    assert report.title == "Sales Q1"
    assert report.metrics["total_revenue"] == 150000.0
    assert len(report.artifacts_created) == 1


def test_agent_with_structured_output():
    agent = make_interpreter_agent(response_format=AnalysisReport)
    assert agent is not None


