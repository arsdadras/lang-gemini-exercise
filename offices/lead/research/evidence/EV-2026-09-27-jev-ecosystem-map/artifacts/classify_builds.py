"""Label every shipwithjev build with the role its Jev decision plays, using Jev itself (one
request per build), plus three yes/no properties. Research spike; the key is read from the
repo's .env and never printed."""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import dotenv_values
from langchain_typesafe import Choice, Noul, NoulCriteria, TypeSafeClassifier

REPO = Path(r"D:/Repos/lang_claude_exercise")
HERE = Path(__file__).parent
KEY = dotenv_values(REPO / ".env")["OPENROUTER_API_KEY"]
clf = TypeSafeClassifier(model="typesafe/jev-1.13", base_url="https://openrouter.ai/api",
                         api_key=KEY, timeout=30)

ROLES = {
    "action_selection": "Jev picks the next action, tool, or element for an agent or program "
                        "to execute: browser or computer use, tool or MCP routing, game or "
                        "robot moves, voice commands.",
    "safety_gate": "Jev checks an agent's proposed action or a message against a policy "
                   "before it runs or is sent: tool-call and shell-command gates, auto-approval, "
                   "guardrails, prompt-injection screening.",
    "context_management": "Jev decides what context an agent sees: which skills, rules, "
                          "memories, or retrieved passages to load, what to compact or forget.",
    "verification": "Jev checks finished work: whether a coding agent is really done, "
                    "whether code, a PR, a commit, or an answer meets rules or a spec, evals "
                    "of agent traces.",
    "model_or_agent_routing": "Jev decides which model, reasoning effort, subagent, or "
                              "specialist handles a request.",
    "triage": "Jev classifies incoming business items to route or prioritize them: email, "
              "tickets, leads, alerts, documents, logs.",
    "search_and_ranking": "Jev ranks or filters items against a query: semantic search, "
                          "reranking, code search, recommendations, SQL filters.",
    "content_scoring": "Jev scores, labels, filters, or moderates content: social feeds, "
                       "drafts, ads, AI-slop detection, moderation.",
    "extraction": "Jev picks field values or structure out of documents or text.",
    "analysis_at_scale": "Jev labels large datasets to study or measure them: research "
                         "corpora, feature extraction for ML, surveys, trading signals.",
    "about_jev": "The item is about Jev itself: a client library, SDK, framework "
                 "integration, benchmark, study, tutorial, or opinion piece.",
    "other": "None of the above fits.",
}
QUESTIONS = {
    "role": Choice(instructions="What role do Jev's decisions play in `build`?",
                   criteria=ROLES),
    "coding_agent": Noul(
        instructions="Does `build` work with or for coding agents such as Claude Code, Codex, "
                     "Cursor, or OpenCode?",
        criteria=NoulCriteria(true="It hooks into, extends, or serves a coding agent.",
                              false="It has nothing to do with coding agents.")),
    "llm_fallback": Noul(
        instructions="Does `build` combine Jev with an LLM, sending some cases or steps to the "
                     "LLM (a cascade, fallback, or planner-plus-Jev split)?",
        criteria=NoulCriteria(true="An LLM handles some steps or the uncertain cases.",
                              false="Jev works alone, or no LLM is mentioned.")),
    "measured": Noul(
        instructions="Does `build` report a measurement of quality against labels or a "
                     "baseline (accuracy, precision, AUROC, agreement), not only speed or cost?",
        criteria=NoulCriteria(true="A quality number against labels or a baseline appears.",
                              false="Only speed, cost, anecdotes, or nothing is reported.")),
}


def label(row):
    state = {"description": "One entry from a public catalog of things people built with Jev. "
                            "Judge only from this text.",
             "build": {"title": row["title"], "category": row["category"],
                       "summary": row["summary"], "text": row["text"][:900]}}
    for attempt in range(3):
        try:
            r = clf.invoke({"state": state, "questions": QUESTIONS})
            ch = r.choices["role"]
            return {"slug": row["slug"], "role": ch.choice, "role_conf": round(ch.confidence, 3),
                    "role_probs": {k: round(v, 3) for k, v in ch.probabilities.items()},
                    **{k: round(r.nouls[k].noul, 3) for k in ("coding_agent", "llm_fallback",
                                                               "measured")},
                    "tokens": r.usage.input_tokens or 0}
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"
            time.sleep(2 * (attempt + 1))
    return {"slug": row["slug"], "error": err}


rows = json.loads((HERE / "builds.json").read_text(encoding="utf-8"))
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as pool:
    out = list(pool.map(label, rows))
elapsed = time.perf_counter() - start
(HERE / "labels_jev.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
ok = [o for o in out if "error" not in o]
tokens = sum(o["tokens"] for o in ok)
print(f"labeled {len(ok)}/{len(out)} in {elapsed:.0f}s; {tokens} input tokens, "
      f"${tokens * 0.042 / 1e6:.4f}")
for o in out:
    if "error" in o:
        print("ERR", o["slug"], o["error"][:120])
