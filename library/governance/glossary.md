---
title: Glossary
maintainer: lead
status: current
updated: 2026-09-26
summary: Terms with a specific meaning in this repository.
related: [principles.md, protocol.md, ../../offices/lead/ROADMAP.md]
---

# Glossary

| Term | Meaning here |
| :--- | :--- |
| **Lead** | The role that decides and executes direction, curriculum, architecture, technology, governance, and git. Formerly "the office" ([ADR-0018](../../docs/adr/0018-three-offices-library-and-archive.md)) |
| **Mentor** | The role that teaches the learner and implements the plan in lesson code; the default session role |
| **Research** | The role that investigates, measures, and advises; it decides nothing |
| **Office** | A role's own directory under `offices/`: charter, state, outbox, artifacts, sandbox |
| **Library** | Shared canonical knowledge under `library/` ([README](../README.md)) |
| **Archive** | Retired documents under `archive/`, frozen ([README](../../archive/README.md)) |
| **Message** | An entry in a role's `OUTBOX.md`: directive, request, notice, or reply ([protocol.md](protocol.md)) |
| **Directive** | A lead message another role must apply at its stated timing |
| **Specialist** | A project's agent or graph, reusable behind the specialist contract (P1-P5, P7-P9, P11) |
| **Specialist contract** | The typed result envelope and failure contract every specialist returns (defined in R0) |
| **Stage** | One central lesson (one hard new concept) within a project phase |
| **Topic** | One sitting's vertical slice within a stage |
| **Return pass (R0-R5)** | The stages between P5 and P6 that bring P1-P5 to one contract |
| **Term P / Term E** | Projects P1-P12 / productization and scale after P12 |
| **Eval-lite** | A small scenario set run against real models by hand, never by pytest (`evals/`) |
| **Test mode** | `LLM_TEST_MODE=true`: every tier routes to a test tier, optionally a named profile |
| **Evidence record** | A research record `EV-<date>-<slug>`: an immutable measurement, cited by ID |
| **Brief** | A research record `BR-###`: the research stance on a question |
| **Design card** | The contract for one specialist, written by the lead before its build or R stage |
