# BR-003: Decision points: what decision models should change in this repo, and how

| | |
| :--- | :--- |
| Status | current |
| Addressed to | The lead office (architecture, technology, curriculum), then the user |
| Question | The user asked four things on 2026-09-27. Where do decision models such as Jev belong in this repo's code? Does the architecture need a fundamental refactor, or a new perspective? How should the curriculum use them? How do the agents in every session learn to weigh them? All without forcing them anywhere |
| Supersedes | [BR-001](../BR-001-decision-model-adoption/README.md). Its cautions that still hold are restated here |
| Built on | [capabilities](../../landscape/decision-models/capabilities.md), [Jev](../../landscape/decision-models/jev.md), [integrations](../../landscape/decision-models/langchain-integrations.md), [EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md), [EV-2026-09-25-laya-zero-shot](../../evidence/EV-2026-09-25-laya-zero-shot/README.md), [EV-2026-09-26-laya-all-checkpoints](../../evidence/EV-2026-09-26-laya-all-checkpoints/README.md), [EV-2026-09-26-jev-wire-compat](../../evidence/EV-2026-09-26-jev-wire-compat/README.md); the lead's [ARCHITECTURE](../../../../offices/lead/ARCHITECTURE.md), [ROADMAP](../../../../offices/lead/ROADMAP.md), [PEDAGOGY](../../../../offices/lead/PEDAGOGY.md), [BACKLOG](../../../../offices/lead/BACKLOG.md), and DEC-004 |
| Files | [use-cases.md](use-cases.md), [plan.md](plan.md), [curriculum.md](curriculum.md), [agent-guidance.md](agent-guidance.md) |

## Short answer

1. **Use cases.**
   - **Strongest today:** the steps that already send a narrow, typed judgment to an LLM:
     - RAG relevance grading, one batched request per question;
     - the groundedness checks that R1 and R2 are about to make central;
     - the memory and skill guards, as a tightening signal only.
   - **On the roadmap:**
     - citation support (R1);
     - per-field confidence (P7);
     - triage, approval gates, and the calibrated cascade (P8);
     - action approval (P11);
     - routing (P12);
     - model routing (E2).

   Details, and the list of places it doesn't belong: [use-cases.md](use-cases.md).
2. **Refactor: no fundamental rewrite, but a change of perspective now.** Every AI step is
   either a **decision point** (a typed, closed answer) or a **generation point** (text).
   - **A decision point is a measured component.** It has:
     - options;
     - a labeled set;
     - a metric;
     - an error direction;
     - a threshold with an escalation;
     - a backend chosen by measurement.
   - **The seam already exists.** The code routes these steps through typed structured output.
   - **Each point migrates at the stage that teaches it,** measured before and after.
3. **How to migrate:** a nine-step recipe per decision point, and a stage schedule starting at
   R2 ([plan.md](plan.md)).
4. **Teaching:** a thread across stages that never adds a second hard concept to a stage. Beside
   it, teaching practices that decision models make cheap: prediction questions answered with
   live probabilities, a question-design lab, and decision-point hunts in design cards
   ([curriculum.md](curriculum.md)).
5. **Agents:** one shared library entry for every role,
   [design guide](../../landscape/decision-models/design-guide.md).
   The lead makes it discoverable in every session ([agent-guidance.md](agent-guidance.md)).
6. **Never forced.** The entry's rubric decides step by step, on evidence and on what's right at
   production scale. Several of today's AI steps should stay with an LLM or with plain code.

## Is it a gamechanger?

The paradigm matters more than the product.

- **The paradigm.** A decider cheap enough for every step makes a separate control plane
  affordable, with routing, gating, grading, and escalation. It pushes designs toward control flow
  owned by code, with narrow AI judgments inside. That is exactly what this curriculum should
  teach.
- **The product.** Jev is twelve days old, fast and cheap, and close to our LLM tiers on narrow
  checks: 22/23, with no unsafe guard error. Independent studies put it mid-pack on hard
  many-class tasks, and its calibration is contested.

So: teach the pattern with swappable backends, let each point's measurement pick the backend,
and cascade rather than replace.

## Recommendations

Each one names its kind of reason ([PRINCIPLES 2](../../../../library/governance/principles.md)).

| # | Recommendation | Kind | Reason |
| :-: | :--- | :--- | :--- |
| 1 | **Decision points** become an architecture principle, design card point 17, and a quality-ladder thread (proposed text in [plan.md](plan.md#1-the-perspective)) | Production value; evidence | The production patterns for controlling AI (gates, cascades, routing, online evaluation) need decisions to be measured components. Our own data shows that wording and thresholds change outcomes, so an unmeasured decision is a hidden risk. No code changes |
| 2 | **Radar:** Jev enters the Assess row with this evidence, and OpenRouter's System One API as its access path. Both go to Trial when R2's measurement passes; OpenRouter as an LLM gateway stays on Hold | Evidence | 22/23, stable over three runs, 11 of 11 client checks, one key the user already has ([EV-2026-09-27](../../evidence/EV-2026-09-27-jev-openrouter/README.md)) |
| 3 | **Client:** `langchain-typesafe`, entering at R2 with a recorded pre-release reason and an exit date | Evidence | Verified: it adds one package and changes no version. It is maintained by LangChain, and its typed errors are ones our `failure_util` already classifies. Exit: its first non-alpha release, or, if it's still alpha when P8-C3 starts, a small client of our own over the System One API |
| 4 | **No big-bang refactor** | Sequencing; evidence | R0 is in flight. The curriculum allows one hard concept per stage. Twenty-three cases give a direction, not a rate. Most decision points have no labeled set yet |
| 5 | **First code consumer: R2,** as a supporting lesson on R2's labeled set: the grader measured as LLM against Jev, batched, plus the groundedness decision that R2's rerouting item will branch on | Sequencing | R2 builds the labeled set that makes the comparison honest, and its backlog already holds batch grading, rerouting of ungrounded answers, and groundedness on the web path. At production load, grading each document with its own LLM call is the wrong design |
| 6 | **R1 keeps the LLM** for citation checks, and logs every decision so later stages inherit labeled data | Sequencing | R1's hard concept is provenance; a new backend would be a second one |
| 7 | **Security verdicts:** ARCHITECTURE principle 4 stands. A decider may add "ask" or "block", run as a tightening ensemble beside the LLM guard. An "allow" without the LLM is a loosening, and it needs a labeled red-team set and a recorded lead decision | Evidence | None of our 48 guard decisions was unsafe, but that is far from a rate, and adversarial content is the class's documented weakness |
| 8 | **Gates with a review band** (act, block, or ask a person) enter where approval is the lesson: P8-B3 and C1, then P11-B1. P6-B3 closes the coordinator's shell with static rules and approval for everything else | Sequencing; evidence | P6-B3's hard concept is surfacing nested approvals. Auto-approval loosens a control, so it needs P7-C3's red-team set and P8-C2's labels first |
| 9 | **P8-C3 unchanged** (DEC-004). Jev is now a measured contender, and our 23 cases and scripts can seed the shared eval-lite harness's decision set | Evidence | [EV-2026-09-27](../../evidence/EV-2026-09-27-jev-openrouter/README.md) |
| 10 | **One shared library entry** teaches every role, and is made discoverable in every session | Scope | The user asked for it; one fact, one file |

## Risks

| Risk | Handled by |
| :--- | :--- |
| Overuse driven by novelty | The rubric; a labeled set before any production use |
| Vendor lock-in or a price change | The protocol seam, verified on two servers; a pinned model ID; Laya as the self-hosted fallback |
| An alias silently changes answers | Pin `typesafe/jev-1.13`; refit thresholds on every upgrade |
| The alpha client changes or stalls | One adapter module, and the exit plan in recommendation 3 |
| Calibration isn't what's claimed | Thresholds fitted per question on labels; the gate is coverage at an error budget, not raw confidence |
| Adversarial content | Never the sole gate; principle 4 |
| Finglish | A labeled Finglish subset per decision point; escalate until measured |
| Personal data leaves our infrastructure | The same exposure as today's hosted LLM tiers. It needs one data policy for every hosted provider, which is a lead decision, not a Jev-specific rule |
| Wording sensitivity | Question text is versioned and measured like code |
| Cognitive load for the learner | One hard concept per stage; the thread spreads the rest ([curriculum.md](curriculum.md)) |

## For the lead

Mirrored in the [outbox](../../OUTBOX.md) as RS-010 (decide on this brief) and RS-011 (make the
library entry discoverable).

- **Decisions requested:** recommendations 1-10. They touch ARCHITECTURE, the design card
  template, TECH_RADAR, the ROADMAP rows for R2, P6-B3, and P8, BACKLOG, PEDAGOGY (C9's evidence),
  and `CLAUDE.md` or `AGENTS.md`.
- **Nothing is needed from the user:** the key exists, and a full re-run of the harness costs
  under $0.01.

## Update triggers

Any of these reopens this brief:

- a Jev release or an alias move;
- `langchain-typesafe` or OpenRouter's Decisions API leaves alpha;
- independent calibration evidence;
- R2's measurement;
- P8-C2's labeled set;
- a data-policy decision for hosted providers.

## History

| Date | Change |
| :--- | :--- |
| 2026-09-27 | First version, answering the user's request and built on EV-2026-09-27. **Supersedes BR-001:** Jev became measurable through OpenRouter and measured close to our LLM tiers. The first consumer moves from P8-C3 to R2, and "no member in today's call sites" becomes "no member before its stage's measurement" |
