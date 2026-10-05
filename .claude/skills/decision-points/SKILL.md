---
name: decision-points
description: Use when designing, planning, building, or reviewing an AI step that decides rather than writes (route, gate, grade, verify, recall, stop, score, pick a schema or a tier), or when choosing between plain code, an LLM, a decision model such as Jev, or a cascade for such a step.
---

1. Read `library/architecture/decision-models.md` and apply its rule, in its order, to the step.
2. Hold the step to the one standard: a labeled set with a Finglish subset; accuracy per class,
   unsafe errors, latency, and cost; the decider first and the LLM as its escalation, unless the
   measurement says otherwise.
3. A gate on anything consequential escalates or tightens; it never approves or loosens.
4. Record the result on the design card's point 17 and in `mentor/DECISIONS.md`. Measurements
   go in a research record (`mentor/research/`). A new backend or dependency enters only through
   the radar (`library/technology/radar.md`).
