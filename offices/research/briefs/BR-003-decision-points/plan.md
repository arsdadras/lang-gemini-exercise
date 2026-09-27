# BR-003 › Plan: the System-1 layer, its migration, and the records it touches

Supports [BR-003](README.md) version 2; version 3's amendments are in
[second-review.md](second-review.md). Everything here is a proposal for the lead. The mentor
implements whatever the lead accepts; code conventions are `AGENTS.md`'s.

## 1. The perspective

Every AI step in a system is one of two kinds:

- a **generation point** writes: an answer, a rewrite, a plan, an explanation;
- a **decision point** picks, checks, or scores: route, gate, grade, verify, recall, stop.

Decision points are cheap enough now to be a layer of their own, the **System-1 layer**, sitting
in three places:

1. **Around the model:** the harness decisions of every agent.
2. **At the graph's branches:** conditional edges, graders, and gates.
3. **Around the code:** the development and learning loops.

**Three properties make it a layer and not a scattering of calls:**

- **One seam.** A decision is produced by an injected *decider*: an LLM with structured output,
  a decision model, or a cascade of both. It returns the typed answer plus its probabilities.
  The call site doesn't know which one it got.
- **One policy per point:**
  - thresholds fitted from the cost of each mistake;
  - the escalation target;
  - the direction errors fail in;
  - "escalate, never approve" wherever the decision could grant something.
- **One measurement per point:**
  - a labeled set;
  - accuracy per class, and unsafe errors for anything security-related;
  - coverage at an error budget;
  - latency and cost.

This is how the ecosystem's best-measured builds are made (the Stagehand fallback, done gates,
gates that escalate). It is also a direct continuation of what this repo already teaches: typed
contracts (convention 8), code-owned control flow in LangGraph, and one enforcement point per
policy (ADR-0010).

## 2. The design, when code starts

- **A seam, not a framework.**
  - The security guard already takes an injected `classifier=`. The graders, the groundedness
    middleware, and each later decision point get the same small factory change.
  - A decider returns the **existing** Pydantic schema, so no contract changes.
  - This is plumbing over observed consumers, which Principle 3 allows. No decision registry
    (ADR-0006).
- **One adapter module for Jev.**
  - It builds `TypeSafeClassifier` from configuration: the base URL, the name of the key's
    environment variable, and the pinned model ID, which lives in `configs/models_config.py`.
  - It maps answers onto our schemas, and carries the probabilities as run metadata.
  - A schema gains a confidence field only when a caller branches on it.
- **Two small, reusable policies,** extracted when their third consumer appears:
  - a *cascade*: the decider answers when confident, and otherwise the LLM path runs;
  - a *gate*: allow, ask a person, or block, where the decider may only add "ask" or "block".
- **Questions as versioned constants.** Each point's questions and thresholds sit in one place,
  reviewed like code. Rewording is an API change, and the labeled set re-runs.
- **Labeled sets as eval data.** One small labeled set per point, under `evals/`, run by hand
  like today's eval-lite. The research office's cases can seed them.
- **Conventions:**
  - **Retries:** the client has none, so exactly one retry layer on its node (convention 11).
    In a cascade, a decider failure takes the LLM path, which is the fail-safe direction.
  - **Timeouts:** explicit (R0's item).
  - **Test mode:** decisions keep their backend. A test profile may route them to the LLM
    path for comparison.
  - **Tests:** unit tests inject a scripted fake decider; live checks run only in eval-lite.
- **Telemetry:**
  - the served model snapshot, the probabilities, and the path taken (fast or escalated);
  - the cost, computed from input tokens;
  - a decision cache keyed on model, questions, and state, which makes replay deterministic.
- **Data:** hosted deciders see the state. One data policy for every hosted provider.

## 3. The migration recipe, per decision point

1. **Inventory:** the point's name, its current backend, its schema, and its error direction.
2. **Label:** at least 50 items to start, and 200 before fitting thresholds on a security point.
   Include negations, Finglish, adversarial content, and hard negatives.
3. **Baseline:** the current backend's accuracy per class, unsafe errors, p50 and p95 latency,
   and cost.
4. **Design the questions:** decompose, close the answer set with `none` or `unclear`, write the
   edge cases into the questions, and keep instructions in English. Measure at least two
   wordings.
5. **Contenders:** Jev, and Laya or a llama.cpp backend wherever the data must stay local.
   Record the margins.
6. **Policy:**
   - thresholds from the cost of each mistake;
   - the escalation target;
   - the direction errors fail in;
   - "escalate, never approve" where the point could grant.
7. **Integrate** behind the seam. The LLM path stays as the escalation and the fallback.
8. **Promote** only if the cascade meets the bar on held-out data. Show the before and after,
   and update the design card and the radar.
9. **Operate:**
   - pin the version, and refit on every upgrade;
   - watch the probability distributions for drift;
   - send low-confidence cases to labeling.

## Schedule

**Amended by version 3** ([second-review.md](second-review.md)): Phase 1 retrofits the decision
points P1 to P5 already have, starting at R1 (A2); decision models enter the models layer with
that first retrofit (A1); per-request tier selection is measured at R2 (A5); and every decision
point, whatever its backend, is held to the same standard (A10). The rows below are otherwise
unchanged.

| When | What changes | Evidence gate |
| :--- | :--- | :--- |
| **Now** (lead, no code) | The principle, design card point 17, the Decisions thread, the radar at *Assess*, the design guide placed | None |
| **R1** | Citation checks stay on the LLM, and every decision is logged as future labels | None |
| **R2** (supporting lesson) | Graders measured LLM against decider; batched grading; the adapter; `langchain-typesafe` enters and the radar moves to *Trial* | The cascade matches the LLM grader on held-out data, with no loss on the groundedness decision |
| **P5 teaching pass** (supporting lesson) | A staleness pre-pass that proposes to the consolidator; a tightening ensemble on the guard | No unsafe guard error; implied changes escalated |
| **D1, decision engineering** (a new stage, proposed) | The layer's hard concept: decomposition, thresholds from error costs, the cascade and gate policies, and the seam made general. Material: the routing, staleness, and grader sets | Coverage at an error budget, measured on each point's set |
| **P6** | "Prod, not god": the workflow's branches are decided by typed decisions. At C1, three control styles compared on one eval set: code rules, decider at the branches, and a supervisor agent. At B3, the shell gate escalates | P6-C1's eval set |
| **P7** | Extraction from candidates with "none"; per-field confidence feeding human review; the red-team set (C3) | Per-field accuracy; red-team results |
| **P8** | Triage fan-out (A1); approval gates (B3, C1); the calibrated cascade at production scale on C2's feedback data (C3, DEC-004) | DEC-004's gate |
| **P11, P12, E1, E2** | Action gates; routing over typed contracts; context budgets; routing and policy services | Per stage |
| **Development loop** (whenever the lead and user choose) | Advisory hooks, then blocking only after a replay of our own sessions | A replay precision the lead sets |

## 4. What not to build

- **No decision registry or plugin framework.** Each point builds its decider from its own
  specification (ADR-0006).
- **No experimental middleware as-is.** `AutoModeMiddleware` hard-codes 0.5 and blocks instead
  of asking; `ModelRouterMiddleware` has no confidence gate. Reference only.
- **No migration of generation steps,** and no decider replacing code that already decides.
- **No gate that grants on the decider's say.**

## Proposed text for lead-owned records

For the lead to adopt, edit, or reject. This office writes none of them.

- **ARCHITECTURE, principle 10:** "Decision points form a System-1 layer. A model step that
  decides rather than writes (route, gate, grade, verify, recall, stop) takes an injected
  decider, returns a typed answer with its probabilities, and has a labeled set, a fitted
  threshold, and an escalation target. Its backend (an LLM, a decision model, or a cascade) is
  chosen by measurement. A decider may escalate or tighten; it never approves or loosens
  (principle 4)."
- **ARCHITECTURE, quality ladder, a thread named Decisions:**
  - **Now:** typed structured output from LLM tiers.
  - **Grows at:**
    - measured deciders on labeled sets (R2);
    - memory decisions (the P5 teaching pass);
    - the layer made general (D1);
    - decisions at the workflow's branches (P6);
    - gates (P8, P11);
    - the cascade at scale (P8-C3);
    - routing and policy services (E2).
- **ARCHITECTURE, composition patterns:** "**Gate:** a decider may stop and ask a person, never
  grant."
- **Design card template, point 17:** "**Decision points:** every step where a model decides
  rather than writes, with its options, labeled set, error direction, threshold and escalation,
  and the backend chosen by measurement."
- **TECH_RADAR:** "Jev (TypeSafe) through OpenRouter's System One API: *Assess*. Evidence:
  EV-2026-09-27-jev-openrouter, EV-2026-09-27-jev-harness-decisions. *Trial* at R2." Also:
  "`langchain-typesafe` 0.0.1a3: enters at R2, with a pre-release reason and exit criteria: its
  first non-alpha release, or a small in-house client if it's still alpha at P8-C3."
- **ROADMAP:** the D1 stage row; supporting lessons at R2 and in the P5 teaching pass; P6's rows
  as in the schedule above.
- **PEDAGOGY:** C9's evidence gains "decisions measured per point (coverage at an error budget)",
  and C8's gains "labeled sets per decision point".
