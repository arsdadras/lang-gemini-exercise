"""Reference app runner for P3 Code Review."""
import sys
from pathlib import Path
from dotenv import load_dotenv
from .graph import build_code_review_graph
from .output_schemas import ReviewResult, TestSuite

load_dotenv()

_SAMPLE_CODE = """
def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent > 100:
        return 0.0
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount
""".strip()

def run_code_review(code: str, language: str = "python", file_path: str | None = None) -> None:
    graph = build_code_review_graph()
    config = {"configurable": {"thread_id": "ref_session"}}
    print(f"Running review for: {file_path or '<inline_code>'}")
    res = graph.invoke({"code": code, "language": language, "file_path": file_path}, config=config)
    if res.get("error"):
        print(f"Error: {res['error']}")
        return
    print(f"Score: {res['review'].score}/10")
    print(f"Summary: {res['review'].summary}")
    print(f"Tests: {len(res['tests'].test_cases)} test cases generated.")

if __name__ == "__main__":
    run_code_review(_SAMPLE_CODE, "python", "demo.py")
