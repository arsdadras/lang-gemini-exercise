"""LLM baseline on the same cases, through the repo's real code paths (run in test mode)."""

import json
import os
import sys
import time
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

HERE = Path(__file__).parent
# load_dotenv() searches upward from the calling file, which is outside the repo here.
load_dotenv(Path("D:/Repos/lang_claude_exercise/.env"))  # no override: shell test-mode vars win

from agentlab.middlewares.security_guard_middleware import make_security_guard  # noqa: E402
from agentlab.models.registry_model import llm_model  # noqa: E402
from agentlab.prompts.middlewares_prompt import MEMORY_WRITE_POLICY  # noqa: E402
from agentlab.prompts.nodes.rag_prompt import GRADE_PROMPT, HALLUCINATION_PROMPT  # noqa: E402
from agentlab.schemas.output.rag_output_schema import (  # noqa: E402
    GradeDocument,
    GradeHallucination,
)

CASES = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


class YesNo(BaseModel):
    binary_score: Literal["yes", "no"]


INTENT_PROMPT = ChatPromptTemplate.from_messages(
    [("system", "Answer the question about the user's message with 'yes' or 'no'."),
     ("human", "Message: {text}\n\nQuestion: {q}")],
)


def timed(fn):
    start = time.perf_counter()
    value = fn()
    return value, round((time.perf_counter() - start) * 1000, 1)


def main():
    profile = os.getenv("LLM_TEST_PROFILE", "default")
    tier = llm_model.resolve_tier("low")
    spec = llm_model.spec("low")
    print(f"test_mode={os.getenv('LLM_TEST_MODE')} profile={profile} -> tier={tier} "
          f"model={spec.model}")
    grade = GRADE_PROMPT | llm_model.chain("opensource", structured=GradeDocument)
    halluc = HALLUCINATION_PROMPT | llm_model.chain("low", structured=GradeHallucination)
    intent = INTENT_PROMPT | llm_model.chain("low", structured=YesNo)
    guard = make_security_guard(MEMORY_WRITE_POLICY)
    out = {"relevance": [], "grounded": [], "intent": [], "guard": []}
    for c in CASES["relevance"]:
        v, ms = timed(lambda c=c: grade.invoke({"question": c["q"], "document": c["doc"]}))
        out["relevance"].append({"pred": v.binary_score, "label": c["label"], "ms": ms})
    for c in CASES["grounded"]:
        v, ms = timed(lambda c=c: halluc.invoke({"context": c["ctx"], "generation": c["ans"]}))
        out["grounded"].append({"pred": v.binary_score, "label": c["label"], "ms": ms})
    for c in CASES["intent"]:
        v, ms = timed(lambda c=c: intent.invoke({"text": c["text"], "q": c["q"]}))
        out["intent"].append({"pred": v.binary_score, "label": c["label"], "ms": ms})
    for c in CASES["guard"]:
        v, ms = timed(lambda c=c: guard(c["action"], c["content"]))
        out["guard"].append({"pred": v.decision, "label": c["label"], "ms": ms})
    (HERE / f"results_llm_{profile}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, rows in out.items():
        acc = sum(r["pred"] == r["label"] for r in rows)
        ms = sorted(r["ms"] for r in rows)
        print(f"{k:10s} {acc}/{len(rows)}  p50={ms[len(ms)//2]:.0f}ms  "
              f"preds={[r['pred'] for r in rows]}")
        for r in rows:
            if r["pred"] != r["label"]:
                print(f"    MISS expected={r['label']} got={r['pred']}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
