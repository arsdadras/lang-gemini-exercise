---
title: Glossary
maintainer: mentor
status: current
updated: 2026-10-06
summary: Terms with a specific meaning in this repository.
related: [principles.md, ../../mentor/README.md, ../../mentor/ROADMAP.md]
---

# Glossary

| Term | Meaning here |
| :--- | :--- |
| **Mentor** | The project's only role: plans, builds, tests, researches, keeps the records, and teaches ([ADR-0028](../../docs/adr/0028-one-mentor-one-branch.md)). The lead, engineer, and research roles before it are retired |
| **Research record** | The evidence base, `mentor/research/`: landscape, evidence, briefs, and their catalog |
| **Office** | `mentor/`: the charter, state, records, research, artifacts, and sandbox |
| **Library** | Shared canonical knowledge under `library/` ([README](../README.md)) |
| **Archive** | Retired documents under `archive/`, frozen ([README](../../archive/README.md)) |
| **Message ID** | `LD-`, `MN-`, `EN-`, `RS-###`: a message between the retired roles, kept in [`archive/offices/`](../../archive/README.md); old records cite them |
| **Specialist** | A project's agent or graph, reusable behind the specialist contract (P1-P5, P7-P9, P11) |
| **Specialist contract** | The typed result envelope and failure contract every specialist returns (defined in R0) |
| **Stage** | One central lesson (one hard new concept) within a project phase |
| **Topic** | One sitting's vertical slice within a stage |
| **Return pass (R0-R5)** | The stages between P5 and P6 that bring P1-P5 to one contract |
| **Term P / Term E** | Projects P1-P12 / productization and scale after P12 |
| **Eval-lite** | A small scenario set run against real models by hand, never by pytest (`evals/`) |
| **Test mode** | `LLM_TEST_MODE=true`: every tier routes to a test tier, optionally a named profile |
| **Evidence record** | A research-record entry `EV-<date>-<slug>`: an immutable measurement, cited by ID |
| **Brief** | A research-record entry `BR-###`: a stance on a question |
| **Design card** | The contract for one specialist, written before its build or R stage |
| **Active review** | How the learner practices: reviewing the mentor's verified code, with a prediction question before and "why" and "what if" questions after, instead of typing it ([ADR-0023](../../docs/adr/0023-active-review-instead-of-typing.md)) |
| **Decision point** | A step where a model decides rather than writes: route, gate, grade, verify, recall, stop ([decision-models.md](../architecture/decision-models.md)) |
| **Decider** | Whatever answers a decision point: a decision model (Jev), an LLM with structured output, or a cascade of both |
| **Cascade** | Escalation on uncertainty: a cheap decider answers when confident, and the rest goes up to an LLM or a person. Failing over when a call fails is a **fallback** |
