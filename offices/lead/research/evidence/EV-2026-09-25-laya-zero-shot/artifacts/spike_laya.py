"""Laya spike: our own decision cases, one decision per call (as our nodes call), CPU."""

import json
import sys
import time
from pathlib import Path

from laya import Router

HERE = Path(__file__).parent
CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def noul(instructions, *, ab_labels):
    q = {"type": "noul", "instructions": instructions}
    if ab_labels:  # README's documented workaround for noul label bias (#156)
        q["criteria"] = {"true": "yes", "false": "no"}
        q["labels"] = {"true": "A", "false": "B"}
    return {"d": q}


GUARD_Q = {
    "d": {
        "type": "choice",
        "instructions": (
            "A personal assistant wants to save this to the user's long-term memory. "
            "Which policy decision applies?"
        ),
        "criteria": {
            "allow": "ordinary facts about the user (work, skills, preferences, schedules, "
            "goals), or a progress entry appended to an existing goal file",
            "ask": "sensitive: health, medication, finances, relationships, religion, "
            "politics, ID numbers, or any fact about another person",
            "block": "a credential: password, PIN, security answer, recovery code",
        },
    },
}


def run(router, label, state, questions):
    start = time.perf_counter()
    res = router.predict(state, questions)
    ms = (time.perf_counter() - start) * 1000
    ans = res["answers"]["d"]
    if "choice" in ans:
        pred = ans["choice"]
    else:
        pred = "yes" if ans["noul"] >= 0.5 else "no"
    conf = ans.get("answer_confidence", ans.get("confidence"))
    return {"pred": pred, "label": label, "ok": pred == label, "ms": round(ms, 1),
            "conf": round(float(conf), 3) if conf is not None else None,
            "model": res.get("routing", {}).get("model")}


def main():
    router = Router(device="cpu")
    start = time.perf_counter()
    router.preload(["english", "multilingual"])  # the two automatic routing chooses between
    print(f"cold load (download excluded if cached): {time.perf_counter() - start:.1f}s")
    router.predict("warm up", noul("Is this a test?", ab_labels=False))
    router.predict("salam, chetori?", noul("Is this a greeting?", ab_labels=False))
    out = {}
    for ab in (False, True):
        tag = "ab" if ab else "plain"
        out[f"relevance_{tag}"] = [
            run(router, c["label"], {"question": c["q"], "document": c["doc"]},
                noul("Does the document contain information that could help answer the "
                     "question?", ab_labels=ab))
            for c in CASES["relevance"]
        ]
        out[f"grounded_{tag}"] = [
            run(router, c["label"], {"context": c["ctx"], "answer": c["ans"]},
                noul("Is every claim in the answer supported by the context?", ab_labels=ab))
            for c in CASES["grounded"]
        ]
        out[f"intent_{tag}"] = [
            run(router, c["label"], c["text"], noul(c["q"], ab_labels=ab))
            for c in CASES["intent"]
        ]
    out["guard"] = [
        run(router, c["label"], {"action": c["action"], "content": c["content"]}, GUARD_Q)
        for c in CASES["guard"]
    ]
    (HERE / "results_laya.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, rows in out.items():
        acc = sum(r["ok"] for r in rows)
        ms = sorted(r["ms"] for r in rows)
        print(f"{k:18s} {acc}/{len(rows)}  p50={ms[len(ms)//2]:.0f}ms  "
              f"preds={[r['pred'] for r in rows]} models={sorted({r['model'] for r in rows})}")
        for r in rows:
            if not r["ok"]:
                print(f"    MISS expected={r['label']} got={r['pred']} conf={r['conf']}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
