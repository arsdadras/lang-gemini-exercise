---
title: Glossary
maintainer: lead
status: current
updated: 2026-10-03
summary: Terms with a specific meaning in this repository.
related: [principles.md, protocol.md, ../../offices/lead/ROADMAP.md]
---

# Glossary

| Term | Meaning here |
| :--- | :--- |
| **Lead** | The role that decides, plans, builds, researches, and reviews: direction, curriculum, architecture, technology, governance, code and tooling, evidence, git, and the library. Formerly "the office" ([ADR-0018](../../docs/adr/0018-three-offices-library-and-archive.md)); took over the engineer's and research's work in [ADR-0025](../../docs/adr/0025-two-roles-lead-and-mentor.md) |
| **Mentor** | The role that teaches the learner and reviews the code it teaches |
| **Research record** | The lead's evidence base, `offices/lead/research/`: landscape, evidence, briefs, and their catalog |
| **Office** | A role's own directory under `offices/`: charter, state, outbox, artifacts, sandbox |
| **Library** | Shared canonical knowledge under `library/` ([README](../README.md)) |
| **Archive** | Retired documents under `archive/`, frozen ([README](../../archive/README.md)) |
| **Message** | An entry in a role's `OUTBOX.md`: directive, request, notice, or reply ([protocol.md](protocol.md)) |
| **Directive** | A lead message the mentor must apply at its stated timing |
| **Specialist** | A project's agent or graph, reusable behind the specialist contract (P1-P5, P7-P9, P11) |
| **Specialist contract** | The typed result envelope and failure contract every specialist returns (defined in R0) |
| **Stage** | One central lesson (one hard new concept) within a project phase |
| **Topic** | One sitting's vertical slice within a stage |
| **Return pass (R0-R5)** | The stages between P5 and P6 that bring P1-P5 to one contract |
| **Term P / Term E** | Projects P1-P12 / productization and scale after P12 |
| **Eval-lite** | A small scenario set run against real models by hand, never by pytest (`evals/`) |
| **Test mode** | `LLM_TEST_MODE=true`: every tier routes to a test tier, optionally a named profile |
| **Evidence record** | A research-record entry `EV-<date>-<slug>`: an immutable measurement, cited by ID |
| **Brief** | A research-record entry `BR-###`: the lead's stance on a question |
| **Design card** | The contract for one specialist, written by the lead before its build or R stage |
| **Active review** | How the learner practices: reviewing the lead's verified code, with a prediction question before and "why" and "what if" questions after, instead of typing it ([ADR-0023](../../docs/adr/0023-active-review-instead-of-typing.md)) |
| **Decision point** | A step where a model decides rather than writes: route, gate, grade, verify, recall, stop ([decision-models.md](../architecture/decision-models.md)) |
| **Decider** | Whatever answers a decision point: a decision model (Jev), an LLM with structured output, or a cascade of both |
| **Cascade** | Escalation on uncertainty: a cheap decider answers when confident, and the rest goes up to an LLM or a person. Failing over when a call fails is a **fallback** |
