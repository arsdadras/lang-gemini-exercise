# BR-001: Should this repo adopt AI decision models, and how?

| | |
| :--- | :--- |
| Status | **superseded** by [BR-003](../BR-003-decision-points/README.md) on 2026-09-27. Kept as the record of the earlier position |
| Addressed to | The project office (technology and architecture), then the user |
| Related office records | [DEC-004](../../../../offices/lead/DECISIONS.md) (calibrated cascade planned for P8-C3), [TECH_RADAR](../../../../offices/lead/TECH_RADAR.md) (Laya at *Assess*) |
| Built on | [Domain overview](../../landscape/decision-models/README.md), [Jev](../../landscape/decision-models/jev.md), [Laya](../../landscape/decision-models/laya.md), [Open-Jev](../../landscape/decision-models/open-jev.md), [integrations](../../landscape/decision-models/langchain-integrations.md), [EV-2026-09-25](../../evidence/EV-2026-09-25-laya-zero-shot/README.md), [EV-2026-09-26](../../evidence/EV-2026-09-26-jev-wire-compat/README.md), [fit analysis](fit.md) |

## Short answer

**Yes to the pattern, at the stage the office already chose. No to any member in today's call
sites.**

A calibrated cascade (a fast decision model answers when confident, and escalates to the LLM
otherwise) is a production pattern worth teaching. Its natural first consumer is P8's ticket
triage (DEC-004).

When that stage starts, build it on the shared `/v1/systemone` protocol, with the official
`langchain-typesafe` client. Pick the backend (hosted Jev, self-hosted Laya, or Open-Jev) by
measurement on our own labels.

Until then, change nothing in code or dependencies.

## Recommendations

1. **Now:** nothing in code. Keep the landscape current; the triggers are listed below.
2. **Before P8-C2 closes:** get a TypeSafe API key. Jev is the one member we can't measure
   without it, and it's the fastest and cheapest one measured independently.
3. **At P8-C3:**
   - one client (`langchain-typesafe`), with the backend set by `base_url` and a pinned model
     ID;
   - **our own cascade component**, not the package's experimental middlewares.
4. **Never** a decision model as the sole gate on a security or trust decision (the memory
   guard, prompt-injection screening, tool risk). At most it may fast-path the direction whose
   mistakes are safe, i.e. escalate or block.

## Reasons

Each reason is one of the admissible kinds.

| Recommendation | Kind | Reason |
| :--- | :--- | :--- |
| Adopt the pattern | Production value | Typed output, native probabilities, and flat latency across many parallel questions are engineering qualities a production agent system uses. The cascade teaches calibration, thresholds, and asymmetric risk (PEDAGOGY C9) |
| …at P8-C3, not now | **Sequencing** | Thresholds must be fitted on labeled data from our domain ([calibration](../../landscape/decision-models/README.md#calibration-the-central-claim-unproven)); P8-C2 is planned to produce that data |
| No member in today's call sites | **Evidence** | The member we could measure was worse on our cases and failed the guard open ([EV-2026-09-25](../../evidence/EV-2026-09-25-laya-zero-shot/README.md)). The strongest hosted member is mid-pack on accuracy and worst-calibrated in the only independent check ([Jev](../../landscape/decision-models/jev.md#measurements)) |
| One client over the shared protocol | **Evidence** | Verified: the official client ran unchanged on a second backend, 8 of 8 checks ([EV-2026-09-26](../../evidence/EV-2026-09-26-jev-wire-compat/README.md)). This is plumbing, not policy (Principle 3): nothing gets organized around one vendor, and swapping backends is a config change |
| `langchain-typesafe` over Laya's wrapper | **Evidence** | Maintained inside LangChain, truly async, errors that our `failure_util` already classifies, LangSmith tagging. Laya's wrapper is sync-only and tied to one backend ([integrations](../../landscape/decision-models/langchain-integrations.md)) |
| Our own cascade, not the experimental middlewares | **Wrong at production scale** | The router has no confidence gate or fallback; the tool-risk middleware hard-codes 0.5 and blocks instead of asking a human (Convention 7) |
| Never the sole security gate | **Evidence** | Every member documents weakness to adversarial content; the measured guard failed open; Jev bluffs on unanswerable items ([class weaknesses](../../landscape/decision-models/README.md#weaknesses-the-whole-class-shares)) |

## Proposed phases

Each phase is a proposal for the office to accept, re-cut, or reject.

**Phase 0, watch (now):** no codebase changes. Refresh the landscape when a trigger fires.

**Phase 1, measure (with P8-C2's labeled set):** an eval-lite harness under `evals/`, owned by
the mentor.

- **Contenders:**
  - the LLM `opensource` and `low` tiers;
  - hosted Jev, pinned to `jev-1.13.0` rather than an alias;
  - self-hosted Laya, with temperatures fitted on a held-out split;
  - Open-Jev, only if a GPU exists.
- **Data:** P8's labels plus our existing 23 cases.
- **Metrics:**
  - accuracy and macro-F1, ECE and Brier;
  - **coverage at a fixed error budget**;
  - position-flip rate, unanswerable items, and negation and Finglish subsets;
  - p50 and p95 latency, cost per 1k decisions;
  - whether the state leaves our infrastructure.
- **Gate to phase 2:** some decider meets the office's accuracy bar on its confident slice, at
  useful coverage.

**Phase 2, cascade (P8-C3):** a node or middleware around `TypeSafeClassifier`.

- **Thresholds** per class, asymmetric, loaded from config, fitted on held-out data.
- **Below threshold** → escalate to an LLM tier through `llm_model`.
- **Classifier error** → escalate; never fail open.
- **One retry layer** (Convention 11), because the client has none.
- **Endpoint and model ID** come from environment configuration.
- **Logged per call:** the answering model ID, confidence, and whether it was fast-pathed or
  escalated.
- **Tests:** unit tests use a stub server or an injected client; thresholds are validated by
  eval-lite.

**Phase 3, later candidates**, each only after phase 2 proves the pattern:

| Candidate | Condition |
| :--- | :--- |
| RAG passage grading, all documents in one request | Measured against R2's retrieval eval; the grader first gains an injectable factory ([fit](fit.md)) |
| Groundedness pre-screen | Escalating only, with claims split one per question |
| Guard fast path | `block` only; `allow` and `ask` always go to the LLM |
| P7-C3 prompt-injection screening | One signal among several, never the gate |
| Model routing (E2) | With a confidence gate, unlike `ModelRouterMiddleware` |

## Preconditions

| Item | Who acts |
| :--- | :--- |
| A TypeSafe account and key; the DPA accepted if personal data may be sent | User |
| `langchain-core` ≥1.6.2 (pinned 1.6.1) and the new `httpx2` dependency | Office decides, mentor applies |
| A self-hosted backend as its own service (`laya-serve` on loopback, with a key), so the app's environment doesn't gain torch | Office |
| P8-C2's labeled set | Office plans, mentor builds |

## Risks

| Risk | How this plan handles it |
| :--- | :--- |
| Vendor lock-in or price change (closed weights, rate limits still moving) | The protocol seam: open backends drop in behind the same client |
| An alias changes answers silently | Pin the versioned ID; refit thresholds on upgrade |
| Calibration isn't what's claimed | Fit and verify on our labels; gate on coverage at an error budget, never on raw confidence |
| Adversarial content | Never the sole gate; asymmetric thresholds |
| Personal data leaves our infrastructure | A self-hosted backend for P5 content, or the DPA with zero retention |
| Immature components (alpha client, week-old Laya) | Pin versions; phase 0 watch; no production dependency before phase 1 |
| Finglish | Its own labeled subset; escalate non-English until measured |

## For the office

Mirrored in the [outbox](../../OUTBOX.md).

- **New evidence since DEC-004 and the radar entry:**
  - the protocol compatibility result;
  - the official `langchain-typesafe` package and the limits of its two middlewares;
  - independent measurements placing Jev below `glm-5.3` on accuracy, and last on calibration;
  - `laya-serve` defaults to `0.0.0.0` with no authentication.
- **Backlog candidate:** a TypeSafe key before P8-C2 closes.
- **Dependency note:** `langchain-typesafe` needs `langchain-core` ≥1.6.2. It may join DEC-009's
  upgrade to released versions.

## Update triggers

Any of these reopens this brief:

- a Jev release or an alias move;
- `langchain-typesafe` leaves alpha, or its middlewares leave `experimental`;
- Laya fixes #156, #377, or #131;
- any member publishes independent calibration evidence;
- a TypeSafe key becomes available;
- P8-C2 or P8-C3 starts.

## History

| Date | Change |
| :--- | :--- |
| 2026-09-25 | First advice, in chat after the Laya spike: don't adopt now, revisit at P8. Part of the reasoning was that our call volume is low and the latency saving small |
| 2026-09-26 | **Corrected.** The volume and savings argument is inadmissible (ADR-0017), and the office re-decided on that basis (DEC-004). The conclusion stands on evidence and sequencing alone. Added: the Jev research, the protocol compatibility result, the integration design, and the phases |
| 2026-09-27 | **Superseded by [BR-003](../BR-003-decision-points/README.md).** Jev became reachable through the user's OpenRouter key and measured 22/23 on our cases with no unsafe guard error ([EV-2026-09-27](../../evidence/EV-2026-09-27-jev-openrouter/README.md)), so the recommendation to obtain a TypeSafe key and "no member in today's call sites" no longer hold. The user also widened the question to architecture, curriculum, and agent guidance. The cautions on security gates and on the experimental middlewares carry over to BR-003 |
