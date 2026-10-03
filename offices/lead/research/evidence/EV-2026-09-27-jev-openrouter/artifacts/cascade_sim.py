"""Offline analysis of results_jev_openrouter.json: answer margins, and a simulated
confidence-gated cascade (Jev answers at or above a threshold, the LLM answers the rest).

The simulation assumes the escalated cases get the LLM's recorded answer; glm-5.3 answered all
23 correctly in EV-2026-09-25-laya-zero-shot, so every escalated case counts as correct. That is
an assumption from one earlier run, not a new measurement.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
R = json.loads((HERE / "results_jev_openrouter.json").read_text(encoding="utf-8"))
THRESHOLDS = (0.6, 0.7, 0.8, 0.9, 0.95)


def margin(row):
    """Confidence of a single-question answer: max(p, 1-p) for a noul, `confidence` for a
    choice. The designed guard combines three nouls, so its margin is the smallest distance of
    any of them from its nearest threshold band edge (0.1 or 0.5), scaled to 0.5-1."""
    if row.get("conf") is not None:
        return row["conf"]
    ps = row["probs"].values()
    return min(max(p, 1 - p) for p in ps)


for variant in ("plain", "designed"):
    rows = [r for g in R[variant][0].values() for r in g]  # run 1; all runs were identical
    right = [margin(r) for r in rows if r["ok"]]
    wrong = [margin(r) for r in rows if not r["ok"]]
    print(f"\n{variant}: {len(right)}/{len(rows)} correct; "
          f"margin correct min/median={min(right):.2f}/{sorted(right)[len(right)//2]:.2f}; "
          f"margin wrong={[round(w, 2) for w in wrong]}")
    for t in THRESHOLDS:
        covered = [r for r in rows if margin(r) >= t]
        wrong_covered = sum(not r["ok"] for r in covered)
        escalated = len(rows) - len(covered)
        final = len(covered) - wrong_covered + escalated
        print(f"  tau={t:.2f}: Jev answers {len(covered):2d}/23, wrong among them "
              f"{wrong_covered}, escalated {escalated:2d}, cascade total {final}/23")

print("\nintent p(yes), plain and designed, run 1:")
for v in ("plain", "designed"):
    print(" ", v, [(r["label"], round(r["p_yes"], 2)) for r in R[v][0]["intent"]])

print("\nguard, run 1 (label -> plain choice probs | designed noul probs -> rule):")
for p, d in zip(R["plain"][0]["guard"], R["designed"][0]["guard"]):
    pp = {k: round(x, 2) for k, x in p["probs"].items()}
    dp = {k: round(x, 2) for k, x in d["probs"].items()}
    print(f"  {p['label']:5s} plain={p['pred']:5s} {pp} | designed={d['pred']:5s} {dp}")

print("\nrelevance p(yes) run 1 single-call plain / designed / batched:")
for a, b, c in zip(R["plain"][0]["relevance"], R["designed"][0]["relevance"],
                   R["batched"][0]["rows"]):
    print(f"  {a['label']:3s} {a['p_yes']:.2f} / {b['p_yes']:.2f} / {c['p_yes']:.2f}")

spread = []
for v in ("plain", "designed"):
    for g in R[v][0]:
        for i in range(len(R[v][0][g])):
            vals = [R[v][k][g][i].get("p_yes") for k in range(len(R[v]))]
            if None not in vals:
                spread.append(max(vals) - min(vals))
print(f"\nrepeatability: max spread of p(yes) across {len(R['plain'])} runs = {max(spread):.3f}, "
      f"median = {sorted(spread)[len(spread)//2]:.3f} (noul answers only)")
b_spread = [max(R["batched"][k]["rows"][i]["p_yes"] for k in range(3))
            - min(R["batched"][k]["rows"][i]["p_yes"] for k in range(3)) for i in range(6)]
print(f"batched relevance: p(yes) spread per pair across runs = {[round(s, 2) for s in b_spread]}")
