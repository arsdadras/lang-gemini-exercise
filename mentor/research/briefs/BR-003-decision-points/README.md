# BR-003: Decision points: what decision models should change in this repo, its development, and its teaching

| | |
| :--- | :--- |
| Status | current, **version 3** (2026-09-27). Advice only; the lead decides |
| Addressed to | The lead (architecture, technology, curriculum, governance), then the user |
| Question | The user asked four things on 2026-09-27. Where do decision models such as Jev belong in this repo's code? Does the architecture need a fundamental refactor or a new perspective? How should the teaching use them? How do the agents in every session learn to weigh them, without forcing them anywhere? After reviewing version 1, the user found it underestimated the subject and asked for a wider, deeper redo |
| Supersedes | [BR-001](../BR-001-decision-model-adoption/README.md) |
| Built on | [capabilities](../../landscape/decision-models/capabilities.md), [ecosystem](../../landscape/decision-models/ecosystem.md), [Jev](../../landscape/decision-models/jev.md), [integrations](../../landscape/decision-models/langchain-integrations.md), [design guide](../../landscape/decision-models/design-guide.md); evidence [EV-2026-09-27-jev-harness-decisions](../../evidence/EV-2026-09-27-jev-harness-decisions/README.md), [EV-2026-09-27-jev-ecosystem-map](../../evidence/EV-2026-09-27-jev-ecosystem-map/README.md), [EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md), and the Laya records; the lead's [ARCHITECTURE](../../../../docs/ARCHITECTURE.md), [ROADMAP](../../../ROADMAP.md), [PEDAGOGY](../../../../library/teaching/pedagogy.md), [BACKLOG](../../../BACKLOG.md), DEC-004 |
| Files | [second-review.md](second-review.md) (version 3's amendments), [use-cases.md](use-cases.md), [plan.md](plan.md), [curriculum.md](curriculum.md), [agent-guidance.md](agent-guidance.md) |

## What version 3 adds

The user's second review ([second-review.md](second-review.md)) found gaps that version 2 left,
and made some claims the evidence doesn't support. Both are recorded there, point by point.

- **Where version 2 fell short:**
  - it held a decider to a stricter bar than the LLM deciders already in the code, none of
    which has a labeled set;
  - it put no code before R2;
  - it never read the output schemas field by field;
  - it deferred tier selection to P9;
  - it catalogued patterns without naming anything to build.
- **Version 3 adds:**
  - decision models as a model family in the models layer, beside the LLM tiers (A1);
  - Phase 1, a file-level retrofit of the decision points P1 to P5 already have, starting at R1
    (A2);
  - structured output split by field between code, decider, and LLM (A3);
  - per-request tier selection, measured at R2 (A5);
  - thirteen utilities and ten compositional builds, the decision workbench first (A6, A7);
  - one standard for every decision point, with the decider as the default candidate (A10).
- **Where the evidence says otherwise (A9):**
  - speed is 3-5x per call here, about 25x like for like, and about 20x when batching replaces
    sequential calls. It is not 200x; cost is where the gain is large;
  - a decider grades and reranks the top k. Retrieval over a whole corpus stays with the index;
  - it fills closed fields, not free text, numbers, or dates;
  - every gate still escalates and never approves.

## What version 1 got wrong

- **Too small a scope.** Version 1 treated a decision model as a cheaper grader for a handful of
  call sites, and deferred almost everything to P8.
- **The wider sweep shows otherwise:**
  - LangChain's two posts;
  - TypeSafe's patterns and twenty cookbooks;
  - all 551 cataloged builds, which we classified;
  - eleven independent studies.
- **What it is, mainly:** the *System-1 layer of harnesses*, meaning the small decisions around
  every model call:
  - routing;
  - which skills, rules, and memories to load;
  - whether a tool call may run;
  - which results stay in context;
  - whether the work is really done.
- **The same decisions recur in two more loops:** the development loop, where coding agents build
  software, and the learning loop, where a person learns a craft.
- **Our own spikes agree:**
  - specialist routing 32/32 in all three runs, where two LLM tiers scored 30/32;
  - memory staleness 59/60;
  - semantic lint of our own conventions at AUROC 1.0 on synthetic snippets;
  - graders 22/23.
- **Most of version 1's cautions still stand, and the evidence behind them is stronger now.**

## Short answer

1. **Use cases: far more than the graders,** in three loops ([use-cases.md](use-cases.md)):
   - **Product loop,** our agents:
     - routing to specialists and to model tiers;
     - skill selection;
     - tool-call and approval triage;
     - tool-result filtering and compaction;
     - verifying specialists' claims against their envelopes;
     - memory write, staleness, and recall decisions;
     - RAG grading, reranking, citation, and groundedness;
     - guardrails, and evals.
   - **Development loop,** the Claude sessions working on this repo:
     - a "done means verified" gate;
     - checks against conventions no linter can express;
     - scope and intent gates;
     - commit honesty;
     - selecting which rules to load.
   - **Learning loop:**
     - formative feedback on the learner's typed code and teach-backs;
     - stuck detection;
     - calibration training;
     - scoring prediction questions;
     - item analysis across stages.
2. **Refactor: no big-bang rewrite, but more than a perspective.** We propose a first-class
   **System-1 layer**:
   - one seam, with typed decisions returned by an injected decider;
   - escalation to an LLM or a person;
   - "escalate, never approve" on anything that grants;
   - a labeled set per decision point.

   It is introduced deliberately:
   - in the architecture now, with no code;
   - through a curriculum thread with its own stage;
   - migrated point by point at the stage that teaches each one ([plan.md](plan.md)).
3. **How:** a nine-step recipe per decision point, a stage schedule, and proposed text for every
   record the lead owns ([plan.md](plan.md)).
4. **Teaching:** three layers ([curriculum.md](curriculum.md)):
   - *teach it*: decision engineering as a skill, with its own stage;
   - *teach with it*: the learning loop;
   - *teach by building it*: harness labs.
5. **Agents in every session:** a design guide in this office, with proposed records for the lead
   (a library entry, a line in `CLAUDE.md`, a skill) and proposed development-loop hooks for the
   user ([agent-guidance.md](agent-guidance.md)).
6. **Never forced.** Each use passes the rubric in the design guide. [use-cases.md](use-cases.md)
   lists where it doesn't belong.

## Is it a gamechanger?

**For how harnesses, development workflows, and learning loops are designed: yes,** on the
evidence.

- It makes affordable a separate, typed, measurable layer of judgment at every step.
- The ecosystem converged on exactly that within twelve days:
  - half the builds that use Jev work in the harness;
  - one in four serves coding agents;
  - about ten frameworks shipped integrations.

**For trusting it on its own: no.**

- Only one build in fifteen measures quality.
- Authority-claiming injection succeeded 147 times in 200.
- Calibration fails off its training distribution.
- Spanish costs 3-6 points, and Persian is unknown.
- A real rule-checker's flags were confirmed 10 times in 39.

So the layer escalates, is measured, and never grants on its own.

## Proposals

Each is a proposal; the lead decides. Each names its kind of reason
([principles 2](../../../../library/governance/principles.md)).

| # | Proposal | Kind | Reason |
| :-: | :--- | :--- | :--- |
| 1 | An architecture principle: a **System-1 layer** of typed, measured decision points that escalate (text in [plan.md](plan.md#proposed-text-for-lead-owned-records)) | Production value; evidence | Harness decisions are the production pattern for controlling agents, and they need to be measurable and swappable. The principle costs no code |
| 2 | **Design card point 17,** decision points, and a quality-ladder thread, **Decisions** | Production value | Makes each specialist's decisions reviewable |
| 3 | **A curriculum thread** with its own stage, **D1, decision engineering** (reframed in version 3 as the compositional layer; everyday calls are not a subject, [A8](second-review.md#a8-the-curriculum)), between R5 and P6; supporting lessons at R2 and in the P5 teaching pass; P6 built as "prod, not god"; P8-C3 kept as the cascade at production scale ([curriculum.md](curriculum.md)) | Sequencing | One hard concept per stage: the skill gets its own stage once labeled sets exist (R2), and just before the capstone that uses it most (P6) |
| 4 | **Radar:** Jev, through OpenRouter's System One API, at *Assess* with this evidence; *Trial* at its first stage (R2); `langchain-typesafe` enters then, with a recorded pre-release reason and an exit date | Evidence | 22/23 graders, 32/32 routing, 11/11 client checks; adding the client adds one package and changes no version |
| 5 | **Product harness,** point by point: Phase 1 retrofits P1 to P5's existing decision points from R1 ([A2](second-review.md#a2-phase-1-retrofit-the-decision-points-that-already-exist)), then the later stages ([plan.md](plan.md#schedule)) | Sequencing | R0 is in flight; each point, whatever its backend, needs a labeled set |
| 6 | **Security:** principle 4 stays. Every decider gate on something consequential **escalates and never approves**. Loosening a control needs a labeled red-team set and a lead decision | Evidence | 147/200 authority-claiming injections succeeded; 10 of 39 real rule-gate flags were confirmed |
| 7 | **Development loop:** a done gate and a convention gate for the Claude sessions, advisory first, measured on replays of our own sessions before anything blocks. Installing hooks is the user's call ([agent-guidance.md](agent-guidance.md#the-development-loop)) | Evidence; scope | Principle 5 ("verify before handing over") is exactly what the best-measured hook in the ecosystem checks, at AUROC 0.976 |
| 8 | **Learning loop:** formative uses only. The learner owns every judgment about their own work; no grades; private scratch stays private ([curriculum.md](curriculum.md#teach-with-it-the-learning-loop)) | Scope; evidence | Fluency bias and gaming are documented; summative marks stay human |
| 9 | **Records outside this office,** proposed with their text ([agent-guidance.md](agent-guidance.md#proposed-records)) | Scope | The lead owns the library, `CLAUDE.md`, skills, and the radar |
| 10 | **One data policy for every hosted provider,** LLM and decider alike | Production value | Decisions send state off-site just as our LLM tiers already do |
| 11 | **Decision models in the models layer,** beside the LLM tiers: pinned ID, key by name, test mode, a fake; with the first retrofit ([A1](second-review.md#a1-two-model-families-in-the-models-layer)) | Production value | An infrastructure seam is built production-grade from its first consumer (principle 3) |
| 12 | **Per-request tier selection,** decomposed questions mapped to a tier in code, measured at R2 ([A5](second-review.md#a5-model-tier-selection-per-request)) | Sequencing; evidence | Its labels need an answer-quality eval, which R2 builds; four-tier routing 95.0% against 73.75% **[T]** |
| 13 | **Structured output split by field,** and the utilities ([A3](second-review.md#a3-structured-output-field-by-field), [A6](second-review.md#a6-utilities)) | Production value | Closed fields don't need a generating model; free text does |
| 14 | **The compositional builds,** the decision workbench first ([A7](second-review.md#a7-the-compositional-layer-the-triangle)) | Production value; sequencing | Where the deeper teaching happens; the workbench serves every other point |
| 15 | **One standard for every decision point,** with the decider as the first candidate and the LLM as the escalation ([A10](second-review.md#a10-one-standard-for-every-decision-point)) | Evidence | Version 2 held deciders to a stricter bar than the LLMs already deciding in the code |

## Risks

| Risk | How the proposals handle it |
| :--- | :--- |
| Novelty-driven overuse | The rubric; a labeled set per point; the "doesn't belong" list |
| Gates that block good work | Escalate, never approve; advisory first; measured on replays before any blocking |
| Security bypass by injection | Never the only gate; static rules first; principle 4 |
| Calibration off-distribution | Thresholds fitted per question, pinned version, drift checks |
| Finglish and Persian | A labeled Finglish subset per point; English instructions; escalate until measured |
| Vendor, alias, or alpha-client change | The protocol seam, verified on two servers plus a llama.cpp adapter; pinned model ID; one adapter module; an exit plan |
| Cognitive load for the learner | One hard concept per stage; D1 carries the concept; later stages practice it |
| Privacy | `alireza/` never touched; learner-facing uses only on in-session material; one hosted-provider data policy |

## For the lead

Mirrored in the [outbox](../../../../archive/offices/research/OUTBOX.md) as RS-020, which replaces RS-014.

- **Decisions requested:** proposals 1-15. They touch ARCHITECTURE, the design card template,
  TECH_RADAR, ROADMAP (R2, the P5 teaching pass, D1, P6, P8), BACKLOG, PEDAGOGY, the library, and
  `CLAUDE.md` or `AGENTS.md`.
- **For the user:** whether to try the development-loop hooks, which change security settings.

## Update triggers

Any of these reopens this brief:

- a Jev release or an alias move;
- the client or the Decisions API leaves alpha;
- new independent calibration or language studies;
- a Persian or Finglish study;
- R2's measurement;
- the lead's decision on D1;
- a replay of our own sessions.

## History

| Date | Change |
| :--- | :--- |
| 2026-09-27 | Version 1: superseded BR-001 after Jev was measured through OpenRouter; first code consumer R2 |
| 2026-09-27 | **Version 2**, after the user's review ("it underestimates what it's dealing with"). Rebuilt on a wider sweep: LangChain's posts, TypeSafe's patterns and cookbooks, the full 551-build catalog classified, eleven independent studies, and three new spikes on this repo's own harness decisions. Scope widened from graders to a System-1 layer across the product, development, and learning loops, and a dedicated curriculum stage was proposed. Advice only; this office writes nothing outside itself |
| 2026-09-27 | **Version 3**, after the user's second review, recorded point by point with verdicts in [second-review.md](second-review.md). Adds proposals 11-15: decision models in the models layer, a Phase 1 retrofit of P1 to P5 from R1, per-request tier selection at R2, field-level structured output and utilities, the compositional builds, and one standard for every decision point. Corrects the speed and RAG claims the evidence doesn't support. D1 reframed as the compositional layer |
