# BR-003 › Plan: the perspective, the design, and the migration

Supports [BR-003](README.md). Proposals for the lead; the mentor implements whatever the lead
accepts. Code conventions cited are `AGENTS.md`'s.

## 1. The perspective

Every AI step is one of two kinds:

- a **generation point** writes text: an answer, a rewrite, a plan, an explanation;
- a **decision point** picks from a closed set, answers yes or no, or places something on a
  scale: classify, route, grade, gate, verify, approve.

A decision point is designed and reviewed as a measured component. It has:

1. **Options,** each described, with `other` or `none` when nothing may fit.
2. **A state** holding only what the decision needs.
3. **A labeled set** that measures it.
4. **A metric:**
   - accuracy per class;
   - for security points, a count of unsafe errors;
   - coverage at an error budget;
   - latency and cost per decision.
5. **An error direction:** which mistake is safe. Security fails closed; cosmetic steps may fail
   open.
6. **A threshold and an escalation target:** an LLM, a person, or the stricter default.
7. **A backend chosen by measurement,** with its version pinned: an LLM, a decision model, or a
   cascade of the two.

Where the decision lives, as proposed text for the lead's files:

- **ARCHITECTURE, a principle:** "Decision points are measured components. A model step that
  decides (classify, route, grade, gate, verify) has typed options, a labeled set, an error
  direction, and a threshold with escalation. Its backend (an LLM, a decision model, or a
  cascade) is chosen by measurement, and it never loosens a security verdict (principle 4)."
- **Design card template, point 17:** "**Decision points:** every step where a model decides
  rather than writes, with its options, the labeled set that measures it, its error direction,
  its threshold and escalation, and the backend chosen by measurement."
- **Quality ladder, a thread named Decisions:**
  - **Now:** typed structured output from LLM tiers.
  - **Grows at:**
    - measured backends on labeled sets (R2);
    - gates with a review band (P8-B3, P11-B1);
    - calibrated cascades (P8-C3);
    - routing over typed contracts (P12);
    - routing and policy services (E2).

## 2. The design, when code starts at R2

- **A seam, not a new layer.**
  - The guard already takes an injected `classifier=` that returns `GuardVerdict`. The graders
    and the groundedness middleware get the same small factory change.
  - A decider-backed runnable returns the **existing** Pydantic schema (`GradeDocument`,
    `GradeHallucination`), so no contract changes.
  - This is plumbing over three observed consumers (Principle 3), not a registry.
- **One adapter module for Jev.**
  - It builds `TypeSafeClassifier` from configuration: the base URL, the name of the key's
    environment variable, and the pinned model ID. The model ID lives in
    `configs/models_config.py` (Convention 2).
  - It maps answers onto our schemas, and records the probabilities in the run's metadata.
  - Placement and naming are the mentor's call under `AGENTS.md`.
- **Probabilities travel as metadata first.** A schema gains a `confidence` field only when a
  caller branches on it (P8-C3).
- **Retries (Convention 11).** The client doesn't retry, so a decision call is an external call
  with exactly one retry layer (`TRANSIENT_RETRY` on its node). In a cascade, a decider failure
  escalates to the LLM path instead of failing: the fail-safe direction.
- **Timeouts:** set explicitly. The client exposes `timeout`, which meets R0's item on explicit
  timeouts.
- **Test mode.** `LLM_TEST_MODE` routes the LLM registry only; a Jev call already costs about
  $0.00002. Whether a test profile should send decisions to the LLM path for comparison is the
  mentor's design at R2.
- **Tests:**
  - unit tests inject a scripted fake decider (the repo's real-framework, scripted-model
    policy);
  - live checks run in eval-lite, never in `pytest`.
- **Telemetry:** the served snapshot's model ID, the probabilities, the path (fast or
  escalated), and the cost computed from input tokens. The client drops OpenRouter's `id` and
  `usage.cost`.
- **Security:** static rules run before any decider, such as credential patterns and deny
  lists. An error never allows.
- **Data:** a hosted decider sees the state. One data policy for every hosted provider, LLM or
  decider, is a lead decision.

## 3. The migration recipe, per decision point

1. **Inventory:** the point's name, current backend, schema, and error direction.
2. **Label:** at least 50 items to start, and at least 200 before fitting thresholds on a
   security point. Include negations, Finglish, adversarial content, and hard negatives.
3. **Baseline:** measure the current backend: accuracy per class, unsafe errors, p50 and p95
   latency, and cost per decision.
4. **Design the questions:** atomic, with criteria for both outcomes, `other` or `none` options,
   and a state description. Measure at least two wordings.
5. **Contenders:** Jev, and Laya wherever the data must stay local, on the same set. Record the
   margins.
6. **Policy:**
   - thresholds from the cost of each mistake;
   - the escalation target;
   - the direction errors fail in.
7. **Integrate** behind the existing seam. The LLM path stays as the escalation and the fallback.
8. **Promote** only if the cascade meets the bar on held-out data. Show the before and after,
   and update the design card and the radar.
9. **Operate:**
   - pin the version, and refit on every upgrade;
   - watch the probability distributions for drift;
   - send low-confidence cases to labeling.

## 4. Schedule

| When | What changes | Evidence gate |
| :--- | :--- | :--- |
| Now (lead) | The principle, design card point 17, the Decisions thread, the radar entries, the library entry made discoverable | None: no code |
| R1 | Citation checks stay on the LLM; every decision is logged | None |
| R2 | The grader and the groundedness decision are measured, LLM against Jev; grading is batched; the adapter arrives, and with it `langchain-typesafe` | The cascade matches the LLM grader's accuracy on R2's held-out set, with no loss on the groundedness decision |
| P5 teaching pass, C2 | Guard agreement, with Jev as a tightening ensemble (measured) | No unsafe error on the guard set |
| P6-C1 | Typed decisions as the workflow's branch conditions, against a supervisor | P6-C1's eval set |
| P7-A1, B2, C3 | Extraction from candidates; the review band; the red-team set | Per-field accuracy; red-team results |
| P8 | A1 triage; B3 and C1 gates; C2 labels; C3 the cascade | DEC-004's gate |
| P11-B1, P12-A1 and C1, E2 | Action gates; routing; routing and policy services | Per stage |

## 5. What not to build

- **No decision registry and no plugin layer** (ADR-0006's lesson). Each point builds its
  decider from its own specification.
- **No experimental middleware as-is.** `AutoModeMiddleware` hard-codes 0.5 and blocks instead
  of asking a person; `ModelRouterMiddleware` takes the argmax with no confidence gate. Both are
  references only ([integrations](../../landscape/decision-models/langchain-integrations.md#experimental-middlewares)).
- **No migration of generation steps.**
- **No schema change** before a caller branches on confidence.
