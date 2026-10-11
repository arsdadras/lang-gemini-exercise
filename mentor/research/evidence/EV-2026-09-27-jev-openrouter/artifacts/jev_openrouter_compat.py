"""Does the official Jev LangChain integration (langchain-typesafe) work against the real Jev,
served through OpenRouter's System One API? Also checks OpenRouter's second surface, the
Decisions API, with a plain HTTP call. Research spike: run by hand, never collected by pytest.

The OpenRouter key is read from the repo's .env by absolute path and is never printed.
"""

import asyncio
import json
import os
import time
from pathlib import Path

import httpx2
from dotenv import dotenv_values
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_typesafe import Choice, Noul, Score, TypeSafeClassifier
from langchain_typesafe.client import TypeSafeAPIError

REPO = Path(r"D:/Repos/lang_claude_exercise")
BASE = "https://openrouter.ai/api"
MODEL = "typesafe/jev-1.13"
KEY = dotenv_values(REPO / ".env")["OPENROUTER_API_KEY"]
HERE = Path(__file__).parent
results = {}


def check(name, fn):
    start = time.perf_counter()
    try:
        value = fn()
        ok = True
    except Exception as e:  # noqa: BLE001
        value = f"{type(e).__name__}: {e}"
        ok = False
    ms = round((time.perf_counter() - start) * 1000, 1)
    results[name] = {"ok": ok, "ms": ms, "value": value}
    print(f"[{'OK' if ok else 'FAIL'}] {name} ({ms} ms): {value}", flush=True)


clf = TypeSafeClassifier(model=MODEL, base_url=BASE, api_key=KEY)
QUESTIONS = {
    "refund": Noul(instructions="Does the user explicitly ask for a refund?"),
    "dept": Choice(
        instructions="Which department should handle this?",
        criteria={"billing": "payments, refunds", "technical": "bugs, outages"},
    ),
    "urgency": Score(instructions="How urgent is this?",
                     criteria=["not urgent", "soon", "blocking"]),
}
STATE = "We were billed twice for March. Please refund the duplicate today."


def summarize(r):
    return {
        "model": r.model,
        "refund_noul": round(r.nouls["refund"].noul, 3),
        "dept": r.choices["dept"].choice,
        "dept_conf": round(r.choices["dept"].confidence, 3),
        "urgency": round(r.scores["urgency"].score, 3),
        "usage": r.usage.model_dump(),
        "request_id": r.request_id,
    }


check("invoke: string state, 3 primitives", lambda: summarize(
    clf.invoke({"state": STATE, "questions": QUESTIONS})))
check("invoke: LangChain messages as state", lambda: summarize(clf.invoke({
    "state": [HumanMessage("Hi"), AIMessage("How can I help?"), HumanMessage(STATE)],
    "questions": QUESTIONS})))
check("ainvoke (async path)", lambda: summarize(asyncio.run(
    clf.ainvoke({"state": STATE, "questions": QUESTIONS}))))
check("batch of 2", lambda: [summarize(r) for r in clf.batch([
    {"state": STATE, "questions": QUESTIONS},
    {"state": "The app crashes when I open settings.", "questions": QUESTIONS}])])


def wrong_key():
    bad = TypeSafeClassifier(model=MODEL, base_url=BASE, api_key="sk-or-v1-invalid")
    try:
        bad.invoke({"state": STATE, "questions": QUESTIONS})
    except TypeSafeAPIError as e:
        return f"raised {type(e).__name__} status={e.status_code} (expected 401)"
    return "NO ERROR RAISED"


check("error mapping: wrong key", wrong_key)


def too_many_options():
    crit = {f"q{i:03d}": f"Tickets routed to queue {i}" for i in range(300)}
    try:
        clf.invoke({"state": STATE, "questions": {
            "q": Choice(instructions="Which queue?", criteria=crit)}})
    except TypeSafeAPIError as e:
        return f"raised {type(e).__name__} status={e.status_code}"
    return "accepted 300 options (no error)"


check("error mapping: 300-option choice", too_many_options)


# AutoModeMiddleware (experimental) builds its own classifier from the environment.
os.environ["TYPESAFE_BASE_URL"] = BASE
os.environ["TYPESAFE_API_KEY"] = KEY
from langchain.agents.middleware.types import ToolCallRequest  # noqa: E402
from langchain_typesafe.experimental.middleware import AutoModeMiddleware  # noqa: E402


@tool
def delete_all_files(path: str) -> str:
    """Recursively delete every file under path."""
    return "deleted"


@tool
def read_file(path: str) -> str:
    """Read a text file."""
    return "contents"


mw = AutoModeMiddleware(tools=[delete_all_files, read_file])


def run_guard(tool_obj, args, user_text):
    call = {"id": "c1", "name": tool_obj.name, "args": args, "type": "tool_call"}
    req = ToolCallRequest(tool_call=call, tool=tool_obj,
                          state={"messages": [HumanMessage(user_text)]}, runtime=None)
    out = mw.wrap_tool_call(req, lambda r: ToolMessage("EXECUTED", tool_call_id="c1"))
    return f"{'BLOCKED' if out.status == 'error' else 'EXECUTED'}: {out.content[:90]}"


check("AutoMode: destructive, unauthorized", lambda: run_guard(
    delete_all_files, {"path": "/"}, "Summarize my notes please."))
check("AutoMode: read, authorized", lambda: run_guard(
    read_file, {"path": "notes.txt"}, "Please read notes.txt and summarize it."))


# What the typed client drops: the raw System One body carries OpenRouter's id and cost.
def raw_post(path, body):
    start = time.perf_counter()
    r = httpx2.post(f"https://openrouter.ai{path}", json=body, timeout=30,
                    headers={"Authorization": f"Bearer {KEY}"})
    ms = round((time.perf_counter() - start) * 1000, 1)
    data = r.json()
    return {"status": r.status_code, "ms": ms, "id": data.get("id"), "model": data.get("model"),
            "provider": data.get("provider"), "usage": data.get("usage"),
            "answers": data.get("answers")}


RAW = {"model": MODEL, "state": STATE, "questions": {
    "refund": {"type": "noul", "instructions": "Does the user explicitly ask for a refund?"}}}
check("raw System One body (/api/v1/systemone)", lambda: raw_post("/api/v1/systemone", RAW))
check("raw Decisions API (/api/alpha/decisions)", lambda: raw_post("/api/alpha/decisions", RAW))
check("bare model id jev-1.13 is mapped", lambda: raw_post(
    "/api/v1/systemone", {**RAW, "model": "jev-1.13"}))

(HERE / "results_compat.json").write_text(json.dumps(results, indent=1, default=str),
                                          encoding="utf-8")
