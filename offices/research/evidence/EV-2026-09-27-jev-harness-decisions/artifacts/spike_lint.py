"""Semantic lint of this repo's own conventions (AGENTS.md 1, 2, 4, 6, 7, 10, 11): one request per
code snippet, one noul per rule (speculative fan-out), Jev through OpenRouter, three repeats.
Labels were written with the snippets, before any run. Research spike."""

import json
import time
from pathlib import Path

from dotenv import dotenv_values
from langchain_typesafe import Noul, TypeSafeClassifier

REPO = Path(r"D:/Repos/lang_claude_exercise")
HERE = Path(__file__).parent
KEY = dotenv_values(REPO / ".env")["OPENROUTER_API_KEY"]
clf = TypeSafeClassifier(model="typesafe/jev-1.13", base_url="https://openrouter.ai/api",
                         api_key=KEY, timeout=30)
DATA = json.loads((HERE / "lint_cases.json").read_text(encoding="utf-8"))
QUESTIONS = {name: Noul(instructions=f"Is this true of `code` in `file`? {rule}")
             for name, rule in DATA["rules"].items()}

runs = []
for rep in range(3):
    rows = []
    for s in DATA["snippets"]:
        t = time.perf_counter()
        r = clf.invoke({"state": {"description": "A code change in the agentlab repository. "
                                                 "Judge only what this code does.",
                                  "file": s["file"], "code": s["code"]},
                        "questions": QUESTIONS})
        ms = round((time.perf_counter() - t) * 1000, 1)
        rows.append({"file": s["file"], "violates": s["violates"], "ms": ms,
                     "tokens": r.usage.input_tokens or 0,
                     "p": {k: r.nouls[k].noul for k in QUESTIONS}})
    runs.append(rows)
(HERE / "results_lint_jev.json").write_text(json.dumps(runs, indent=1), encoding="utf-8")

for t in (0.5, 0.7, 0.9):
    tp = fp = fn = 0
    for row in runs[0]:
        for k, p in row["p"].items():
            pos, pred = row["violates"] == k, p >= t
            tp += pos and pred
            fp += (not pos) and pred
            fn += pos and not pred
    print(f"threshold {t}: TP {tp} FP {fp} FN {fn}  (8 violations, 120 clean rule checks)")
pos = sorted(row["p"][row["violates"]] for row in runs[0] if row["violates"])
neg = sorted(p for row in runs[0] for k, p in row["p"].items() if k != row["violates"])
print("violations p:", [round(x, 2) for x in pos])
print("clean checks, top 6 p:", [round(x, 2) for x in neg[-6:]])
auc = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))
print(f"AUROC (run 1): {auc:.3f}")
flips = sum((runs[0][i]["p"][k] >= 0.5) != (runs[j][i]["p"][k] >= 0.5)
            for j in (1, 2) for i in range(len(runs[0])) for k in QUESTIONS)
spread = max(max(runs[j][i]["p"][k] for j in range(3)) - min(runs[j][i]["p"][k] for j in range(3))
             for i in range(len(runs[0])) for k in QUESTIONS)
ms = sorted(r["ms"] for run in runs for r in run)
tok = sum(r["tokens"] for run in runs for r in run)
print(f"label flips vs run 1: {flips}; max p spread {spread:.2f}; p50 {ms[len(ms)//2]:.0f} ms "
      f"per 8-rule request; ${tok * 0.042 / 1e6:.5f}")
