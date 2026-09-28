# Pedagogy

How the curriculum is designed, and what every stage and lesson must satisfy. This is lead
policy; the mentor's delivery procedure that implements it is
[mentor charter](../mentor/README.md). The plan built with these rules is
[ROADMAP.md](ROADMAP.md).

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
| C3 | Knowledge and grounding: retrieval, grading, corrective loops, provenance, retrieval metrics, hybrid retrieval, compiled knowledge (graphs and LLM-maintained wikis) | P2, R1, R2, P7 | Hit rate at k, claim-level provenance |
| C4 | Composition: subagent adapters, specialist contracts, workflows, fan-out and fan-in, choosing deterministic vs model-directed control | R0, P6, P12 | Control comparison on one eval set |
| C5 | Reliability: failure classes, timeouts, retries, fallbacks, resume, idempotency, compensation | R0, P6, P11, P12 | A failure replayed and analyzed |
| C6 | Safety and security: sandboxing, secret isolation, approval gates, guards, injection defense, authorization, tenancy | P3-P5, P7, P8, P11 | Red-team scenario set |
| C7 | Memory and state governance: durable per-user memory, single writer, approval, undo, privacy | P5 | P5 eval-lite |
| C8 | Evaluation and observability: boundary tests, eval sets, trace reading, regression gates, feedback loops | Every project; P5-C, R2, D1, P6-C, P8-C | Eval sets under `evals/`, labeled sets per decision point, CI |
| C9 | Model strategy: tiers, fallbacks, cascades, routing, decision models and decision engineering, measured cost and latency | P5, R1-R2, D1, P8, P9, E2 | Accuracy, coverage at an error budget, and cost per decision point, measured |
| C10 | Software architecture: layering, composition root, contracts, decision records, CI, designing for scale | Every project | The learner defends a design (teach-back) |
| C11 | Production platform: serving, async runs, queues, distributed execution, multi-tenancy | P12, Term E | A deployed service |

## Learning-science basis

The rules below exist for these reasons; change a rule only with its reason in view.

- **Cognitive load:** one hard new concept per stage, so working memory holds one new idea at a
  time on top of practiced ones.
- **Spiral curriculum:** concepts come back at a higher level (the return pass; the capstones
  composing earlier specialists).
- **Deliberate practice:** the learner types the core architecture code; plumbing is integrated
  for them, because typing it teaches little.
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
| L4 | Governance, memory, guards, background work, contracts | P5, return pass |
| L5 | Multi-specialist workflows: parallelism, failure classes, cascades, eval-driven choices | P6-P9 |
| L6 | Actions with side effects: authorization, catalogs, compensation, hierarchy | P11, P12 |
| L7 | Production platform: runtime services, distribution, tenancy | Term E |

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
goes to [BACKLOG.md](BACKLOG.md) with the trigger that would admit it.

### Phase contract

Every project has three phases ([ADR-0001](../../docs/adr/0001-three-phase-project-model.md)).

| Phase | Goal | In scope | Out of scope |
| :--- | :--- | :--- | :--- |
| **A: domain core** | A useful vertical slice | One user job, minimal tools, typed output where something consumes it, production-grade seams for identity, persistence, and secrets (Principle 3), one runnable app, a clear success condition | Generic registries and platform layers, deployment |
| **B: robust operation** | Resilient, meaningful behavior | Persistence and resume, recovery, streaming, validation and self-correction, approval on consequential actions, domain errors | Shared primitives before a second consumer exists |
| **C: composable specialist** | Safe reuse by later workflows | Input/output contract, side-effect and risk declaration, failure contract, subagent or graph wrapper, eval-lite, one small composition exercise | Platform hardening (Term E) |

Every project also moves each quality thread one step
([ARCHITECTURE.md](ARCHITECTURE.md#quality-ladder)).

### Pacing

Counted in stages, never weeks: a stage is one central lesson over a few sessions, and a topic
fits one sitting.

### Digressions and deep-dives

A question above the current level is answered in a few lines (is the instinct right, where does
it land) and parked; it never grows into the lesson. A worthwhile technique with no natural stage
can get one optional **deep-dive** session at a project boundary, at most one per boundary,
scheduled by the lead from [BACKLOG.md](BACKLOG.md).

## Definition of Ready

The lead makes a stage ready before the mentor opens it:

- its one hard concept and the competencies it advances are named;
- scope in and out is explicit, including backlog items scheduled into it;
- the specialist's design card is current;
- acceptance is concrete: the before/after demo scenario, and the tests or eval cases;
- dependencies (earlier stages, library versions, directives) are in place;
- it passes the admission rule;
- the stage's verified reference implementation is merged by the engineer, or the engineer is
  at least one topic ahead of the lesson ([ADR-0022](../../docs/adr/0022-engineer-role-and-division-of-labor.md)).

## Definition of Done

The mentor closes a stage when `uv run pytest` and `uv run ruff check src tests` are green with
real output, the stage's live scenario has run, the mentor's state is updated, every decision request
has gone to the lead, and a commit has landed with the user's OK.

## Delivery invariants

Whatever the mentor's procedure looks like, it keeps these true:

- Each topic is a vertical slice that ends in code the learner has watched run.
- The problem is shown before the theory.
- Core agent-architecture code is typed by the learner; plumbing is built by the engineer and
  shown with a link to every changed file.
- The repo is always the engineer's verified, clean version; an exercise state is never committed.
- Messages to the learner teach, one idea at a time in full sentences; working notes stay out.
- Each step waits for the learner's OK, carries a position marker, and ends with the next step.

## Assessment

| Level | Evidence |
| :--- | :--- |
| Topic | A prediction question before the answer; one hands-on scenario after the demo |
| Stage | A before/after demo of the same scenario; tests or eval cases |
| Project | Eval-lite results; the study guide; a **teach-back** at the project close (the learner explains the design card's key decisions in their own words; gaps become review items in the next project) |
