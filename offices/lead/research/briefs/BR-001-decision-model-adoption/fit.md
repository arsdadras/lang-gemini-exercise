# BR-001 › Fit analysis: where a decision model could sit in this repo

Supports [BR-001](README.md). Code read on 2026-09-26; roadmap per
[`offices/lead/ROADMAP.md`](../../../ROADMAP.md) (then at `docs/office/`). Judged at production load.

The **verdict** column is advice, not a decision. It weighs three things:

- **Shape:** whether the task is a closed-set decision at all;
- **Cost of error:** what a wrong answer does;
- **Evidence:** what we know about decider performance on that kind of task.

## Every model call site today

The repo has 18 `llm_model.get/chain` calls under `src/agentlab`.

| Site | What it decides | Shape | Cost of error | Evidence | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `nodes/rag_node.grade_documents_node` | Is each retrieved document relevant? One call per document (`opensource`) | **Strong:** one `noul` per document, all documents in one request | Low: a missed document is dropped; the rewrite loop recovers | Laya 5/6 zero-shot ([EV-2026-09-25](../../evidence/EV-2026-09-25-laya-zero-shot/README.md)) | Candidate, inside a cascade. Overlaps R2's batch-grading item |
| `nodes/rag_node.check_hallucination_node` | Is the answer grounded in the context? (`low`) | Medium: a `noul`, but an answer holds several claims | High: P2's core trust guarantee | Laya 6/6 on short single-claim cases; indirection and irrelevant context are known weaknesses | Only as an escalating pre-screen |
| `middlewares/groundedness_middleware` | Same check over all tool outputs (`low`) | Medium, over a large state | High | Irrelevant context lowers accuracy; Laya's English context is ~320 tokens | Weak until R1 decides how claims are split |
| `middlewares/security_guard_middleware` | Allow / ask / block, a category, and a sentence for the user (`low`) | Partial: the verdict is a `choice`; the sentence needs generation | **Highest:** a security boundary | Laya never answered "ask" (3/3 failed open); every member is weak to adversarial content | **Not as the guard.** At most a `block`-only fast path, with everything else escalated |
| `middlewares/finglish_output_middleware` | Rewrites leaked lines | None: detection is already a regex, and repair is generation | n/a | n/a | Not a candidate |
| RAG rewrite, generate, web answer; skill designer; memory consolidation; 3 code-review chains | Generation | None | n/a | n/a | Not candidates |
| 5 DeepAgents agents | Tool-calling loops | Only side decisions: which model this turn needs, whether a tool call is risky | Tool risk is high (Convention 7) | The package's middlewares block without a human, or route with no confidence gate | Later: a tool-risk signal *before* HITL, never instead of it; model routing belongs with E2 |

## Planned consumers on the roadmap

| Stage | What it builds | Why a decider fits | Caution |
| :--- | :--- | :--- | :--- |
| **P8-A1, B1** | Ticket classification, multiple intents, SLA and priority routing | A fan-out of `choice`/`score`/`noul` over one ticket, exactly the class's design | None beyond measurement |
| **P8-B2** | Router vs handoffs | A decider as a third router arm next to code and an LLM | Only if the office wants three arms |
| **P8-C2 → C3** | Labeled data, then the calibrated cascade (DEC-004) | The class's reason to exist | [BR-001](README.md) phases |
| P7-C3 | Prompt injection carried in documents | One screening signal | Adversarial content is the class's documented weakness |
| P6, P12-A1/C1 | Routing between specialists; a capability catalog | Intent → specialist is a `choice` | Compare against code routing (P6-C1 already compares deterministic and model-directed) |
| E2 | Model routing | `ModelRouterMiddleware` shows the shape | It needs a confidence gate |
| P6-C2, P8 regression gate | Rubric grading of outputs | Cheap, low-variance `score` rubrics | As one judge beside an LLM, with agreement measured |

## Constraints particular to this repo

- **Finglish.** It's the learner's working language, no vendor tests it, and our spike routed it
  to the wrong checkpoint. Any Persian-facing decision needs its own labeled check first.
- **Personal data.** P5 memory holds health, finances, and third parties. A hosted decider sends
  that off-site, which needs the vendor's DPA (Jev's zero retention is enterprise-only). A
  self-hosted backend avoids it.
- **Hardware.** No GPU is confirmed. Laya is usable on CPU (0.2-0.4 s); Open-Jev and local Qwen
  are not ([EV-2026-09-23-local-ollama-qwen](../../evidence/EV-2026-09-23-local-ollama-qwen/README.md)).
- **Seams.**
  - The security guard (`classifier=`) and the P5 skill-designer and consolidation nodes
    (`model=`) already take an injected runnable that returns our Pydantic schema, so a
    decider-backed runnable drops in without rewiring.
  - The RAG graders and the groundedness middleware call `llm_model.chain(...)` inline (tests
    patch it). They would first need the same small factory change the guard has.
  - No new abstraction is needed before a consumer exists (Principle 3).
