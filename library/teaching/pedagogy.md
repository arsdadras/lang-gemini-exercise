---
title: Pedagogy
maintainer: mentor
status: current
updated: 2026-10-12
summary: Learning outcomes, the learning method (active review), top-down return-pass balancing, curriculum rules, readiness, delivery invariants, and assessment.
related: [../../mentor/ROADMAP.md, ../../mentor/README.md, ../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md]
---

# Pedagogy

How the curriculum is designed, and what every stage and lesson must satisfy. This is the
policy; the mentor's delivery procedure that implements it is
[mentor charter](../../mentor/README.md). The plan built with these rules is
[ROADMAP.md](../../mentor/ROADMAP.md).

## Method: backward design

The curriculum is designed from the outcome backwards, never from the framework's feature list.

1. **Outcomes first.** Each project names the competencies it advances (table below).
2. **Evidence second.** Each stage names how learning will show: a before/after demo, tests or an
   eval set, and the learner explaining the design's *why*.
3. **Activities last.** Stages and topics are cut to produce that evidence.

Coverage is checked against competencies, not against APIs: a framework feature enters only
when a competency needs it at a real consumer (the admission rule below).

## Graduate competencies

What a production AI-systems engineer can do at the end of Term P (C1-C10) and Term E (C11).

| # | Competency | Built in | Evidence |
| :--- | :--- | :--- | :--- |
| C1 | Agents and tools: agent loops, tool design, structured output, approvals | P1, P4, P5 | Running apps, design cards |
| C2 | Explicit control flow: graph state and reducers, loops, subgraphs, checkpoints, streaming, time travel | P2, P3 | Real-graph tests |
| C3 | Knowledge and grounding: retrieval, grading, corrective loops, provenance, retrieval metrics, hybrid retrieval, compiled knowledge (graphs and LLM-maintained wikis) | P2, R1, R2, P8 | Hit rate at k, claim-level provenance |
| C4 | Composition: subagent adapters, specialist contracts, workflows, fan-out and fan-in, choosing deterministic vs model-directed control | R0, P7, P14 | Control comparison on one eval set |
| C5 | Reliability: failure classes, timeouts, retries, fallbacks, resume, idempotency, compensation | R0, P7, P12, P14 | A failure replayed and analyzed |
| C6 | Safety and security: sandboxing, secret isolation, approval gates, guards, injection defense, authorization, tenancy | P3-P5, P8, P9, P12 | Red-team scenario set |
| C7 | Memory and state governance: durable per-user memory, single writer, approval, undo, privacy | P5 | P5 eval-lite |
| C8 | Evaluation and observability: boundary tests, eval sets, trace reading, regression gates, feedback loops | Every project; P5-C, R2, D1, P7-C, P9-C | Eval sets under `evals/`, labeled sets per decision point, CI |
| C9 | Model strategy: tiers, fallbacks, cascades, routing, decision models and decision engineering, measured cost and latency | P5, R1-R2, D1, P9, P10, E2 | Accuracy, coverage at an error budget, and cost per decision point, measured |
| C10 | Software architecture: layering, composition root, contracts, decision records, CI, designing for scale | Every project | The learner defends a design (teach-back) |
| C11 | Production platform: serving, async runs, queues, distributed execution, multi-tenancy | P14, Term E | A deployed service |

## Learning-science basis

The rules below exist for these reasons; change a rule only with its reason in view.

- **Cognitive load:** one hard new concept per stage, so working memory holds one new idea at a
  time on top of practiced ones.
- **Spiral curriculum:** concepts come back at a higher level (the return pass; the capstones
  composing earlier specialists).
- **Active review, not typing** (the learner's choice, 2026-09-28;
  [ADR-0023](../../docs/adr/0023-active-review-instead-of-typing.md)): the learner reviews the mentor's
  verified code instead of typing it, and writes code only when they choose, in their private
  area. Understanding is checked, never assumed: a prediction question before the code, "why
  this design?" and "what if X changed?" after it, a hands-on scenario after the demo, and a
  teach-back at each project close. The risk this guards against is fluency: reading code feels
  like understanding it.
- **Problem before theory:** every topic opens on a visible failure of the current code, so the
  concept arrives as the answer to a question the learner already has.
- **Retrieval and self-explanation:** prediction questions before answers, and a teach-back at
  each project close.
- **Momentum:** every topic ends in something visibly working; sittings are bounded.

## Curriculum rules

### Difficulty curve

The level rises only at project boundaries, never mid-project. A stage holds at most one hard new
concept (a stage that needs two is split), and a steep stage is followed by a lighter one that
practices it.

| Level | What gets hard | Where |
| :--- | :--- | :--- |
| L1 | One agent with tools and structured output | P1 |
| L2 | Explicit graphs: state, loops, checkpoints, streaming | P2 |
| L3 | Composed subgraphs, sandboxes, approval gates, subagent adapters | P3, P4 |
| L4 | Governance, memory, guards, background work, contracts, Wave-Particle Duality | P5, return pass |
| L5 | Multi-specialist workflows: parallelism, failure classes, cascades, eval-driven choices | P6-P11 |
| L6 | Actions with side effects: authorization, catalogs, compensation, hierarchy | P12-P14 |
| L7 | Production platform: runtime services, distribution, tenancy | Term E |

### Top-down mountain-peak perspective and the Compressor Balancing rule (Return Pass)

In the initial pass (`P1`-`P5`), lessons started from inside a single unit and grew outward so
the learner could build foundational vocabulary without cognitive overload. In the **Return Pass
(`R0`-`R5`)** and all subsequent stages, we reverse the camera angle and **stand at the mountain
peak ([ADR-0033](../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md))**:

1. **Top-down film script first:** Before touching any node or tool, every `R` stage starts by
   inspecting the project's Rung-2 coin (`Workflow` + `Specialist[TInput, TReport]`), its Rung-1
   Wave/Particle density (`Graph` stations vs. `Agent` hot loops), and its Rung-0 infrastructure
   consumption. When the whole film script is visible from the top, component boundaries and
   design patterns are chosen deliberately rather than patched bottom-up.
2. **The Compressor Threshold across P1-P5:** The return pass acts as a leveler so all five
   foundational projects exit `R5` at the same production threshold:
   - **`P1` (Research)** started structurally short in Phase A-C, so `R1` expanded it
     horizontally/longitudinally into a multi-source plan-fanout-verify graph.
   - **`P2` (RAG), `P3` (Code Review), and `P4` (Interpreter)** already stand structurally tall,
     so `R2`-`R4` focus on **vertical depth and preventative engineering**: tightening joints,
     replacing raw `str` outputs with rich `*Report` schemas (`RagReport`, `InterpreterReport`),
     decider-backed grading/routing, and eliminating subtle failure modes—without adding lateral
     feature bloat.
   - **`P5` (Personal Context & Memory)** went deep into storage/guard infrastructure while
     leaving its specialist surface thin (`dict[str, str]`), so its return pass extends it
     horizontally/practically into a full `PersonalContextReport` `Workflow` and `Specialist`
     while promoting Memory/Store/Security to Rung-0 repo-wide infrastructure.
3. **Teaching preventative engineering without line-by-line tedium:** As a project's height
   increases, the risk of subtle interaction bugs rises. In `R` stages, the mentor teaches the
   **preventative engineering mindset** (why a failure mode exists, what architectural invariant
   prevents it, and how the design pattern enforces it) in depth, walks through core LangGraph/Agent
   mechanisms verbatim, and summarizes routine defensive plumbing in two lines with file links.

### Stage admission rule

A topic, framework feature, or practice enters a stage only when all three hold:

1. **The project needs it now,** judged at production load (Principle 2), not by what today's
   CLI exercises. Not a problem the project might have later, and not one invented to show an
   API.
2. **It teaches something new:** a concept, trade-off, or failure mode not already learned.
   Reusing a known mechanism in a new domain is practice and stays small.
3. **It fits the flow:** one central lesson per stage and at most a few supporting ones.

A framework feature enters at the first stage with a real consumer, never as a tour. Beta APIs
are re-verified against the pinned version when their stage starts. An item that fails the rule
goes to [BACKLOG.md](../../mentor/BACKLOG.md) with the trigger that would admit it.

### Phase contract

Every project has three phases ([ADR-0001](../../docs/adr/0001-three-phase-project-model.md)).

| Phase | Goal | In scope | Out of scope |
| :--- | :--- | :--- | :--- |
| **A: domain core** | A useful vertical slice | One user job, minimal tools, typed output where something consumes it, production-grade seams for identity, persistence, and secrets (Principle 3), one runnable app, a clear success condition | Generic registries and platform layers, deployment |
| **B: robust operation** | Resilient, meaningful behavior | Persistence and resume, recovery, streaming, validation and self-correction, approval on consequential actions, domain errors | Shared primitives before a second consumer exists |
| **C: composable specialist** | Safe reuse by later workflows | Input/output contract (`Specialist[TInput, TReport]`), `workflows/*_workflow.py` runner, side-effect and risk declaration, failure contract, subagent/tool adapter, eval-lite, one small composition exercise | Platform hardening (Term E) |

Every project also moves each quality thread one step
([ARCHITECTURE.md](../../docs/ARCHITECTURE.md#quality-ladder)).

### Pacing

Counted in stages, never weeks: a stage is one central lesson over a few sessions, and a topic
fits one sitting.

### Digressions and deep-dives

A question above the current level is answered in a few lines (is the instinct right, where does
it land) and parked; it never grows into the lesson. A worthwhile technique with no natural stage
can get one optional **deep-dive** session at a project boundary, at most one per boundary,
scheduled by the mentor from [BACKLOG.md](../../mentor/BACKLOG.md).

## Definition of Ready

The mentor makes a stage ready before it opens it:

- its one hard concept and the competencies it advances are named;
- scope in and out is explicit, including backlog items scheduled into it;
- the specialist's design card is current;
- acceptance is concrete: the before/after demo scenario, and the tests or eval cases;
- dependencies (earlier stages, library versions, directives) are in place;
- it passes the admission rule;
- the code for the next topic is built and verified before its lesson starts.

## Definition of Done

The mentor closes a stage when `uv run pytest`, `uv run ruff check src tests scripts`, and
`uv run mypy src/agentlab` are green with real output, the stage's live scenario has run, the
mentor's state is updated, every decision is recorded, and a commit has landed on `main`
with the user's OK.

## Delivery invariants

Whatever the mentor's procedure looks like, it keeps these true:

- Each topic is a vertical slice that ends in code the learner has watched run.
- The problem is shown before the theory.
- The learner reviews the mentor's verified code: the mentor walks through the core
  architecture code one component at a time, with a prediction question before it and "why"
  and "what if" questions after it; plumbing is shown with a link to every changed file. When
  a probe shows fluency, the learner may review the component as a pull request first, and the
  walkthrough becomes the reconciliation.
- The repo is always the verified, clean version; nothing is reset for typing.
- **Nothing changes in the code without the learner hearing about it** (the learner's
  instruction, 2026-10-06). Every lesson and every report names each file it added or changed
  as a clickable link with its path, says what changed and why, and introduces each new
  function that matters in a line or two, even when the lesson's walkthrough covers only the
  core.
- Messages to the learner teach, one idea at a time in full sentences; working notes stay out.
- Each step waits for the learner's OK, carries a position marker, and ends with the next step.

## Assessment

| Level | Evidence |
| :--- | :--- |
| Topic | A prediction question before the code; "why" and "what if" questions after reviewing it; one hands-on scenario after the demo |
| Stage | A before/after demo of the same scenario; tests or eval cases |
| Project | Eval-lite results; the study guide; a **teach-back** at the project close (the learner explains the design card's key decisions in their own words; gaps become review items in the next project) |
