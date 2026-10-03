# BR-003 › Agents: how every session learns to weigh decision models

Supports [BR-003](README.md) version 2. The user asked on 2026-09-27 that the Claude agents in
every session know this concept, and consider it in their designs and their work, without
forcing it. This office writes only inside itself, so everything outside it below is a
**proposal** with its text; the lead decides, and the user decides anything touching security
settings.

## What exists now, inside this office

- [design-guide.md](../../landscape/decision-models/design-guide.md): the guidance any role
  needs at design time:
  - finding decision points in the three loops;
  - the backend rubric;
  - Jev engineering;
  - the recurring policies;
  - calling Jev in this repo.
- [capabilities.md](../../landscape/decision-models/capabilities.md) and
  [ecosystem.md](../../landscape/decision-models/ecosystem.md): the background and the evidence.

## Proposed records

| # | Record (owner) | Proposal | Why |
| :-: | :--- | :--- | :--- |
| 1 | A library entry (lead: structure and index) | Promote the design guide to `library/engineering/decision-models.md`, maintained by research. The text is ready as the design guide | Shared knowledge lives in the library (principle 9); every role designs AI steps |
| 2 | `CLAUDE.md` or `AGENTS.md` (lead) | One line: "**AI decision points.** Before designing or reviewing a step where a model routes, gates, grades, verifies, recalls, or stops, read `library/engineering/decision-models.md`." | Every session loads these files; one line makes the guide findable at the right moment |
| 3 | A shared-procedure skill in `.claude/skills/` (lead) | The `decision-points` skill below | The line reaches every context; the skill surfaces at the moment of design, when its description matches the task |
| 4 | TypeSafe's official agent skill (lead, then the user) | Install it for sessions that write Jev integrations (from R2 on). It carries the API, primitives, and patterns, and it's installable as a Claude Code plugin | Our design guide covers *whether and where*; the vendor skill covers *how to call the API correctly*, and stays current with it |
| 5 | Architecture, radar, roadmap, pedagogy (lead) | The texts in [plan.md](plan.md#proposed-text-for-lead-owned-records) | They carry the decision |

**Proposed skill text** (record 3):

```markdown
---
name: decision-points
description: Use when designing, planning, or reviewing an AI step that decides rather than
  writes (route, gate, grade, verify, recall, stop, score), or when choosing between plain code,
  an LLM, a decision model such as Jev, or a cascade for such a step.
---

1. Read `library/engineering/decision-models.md` and apply its rubric to the step.
2. Gates on anything consequential escalate and never approve.
3. Record the result where your role records design: the design card's decision points (lead),
   a request to the lead (mentor), or a brief (research).
4. Never add a dependency or change a call site outside your role's plan; a new backend enters
   through the lead's radar.
```

## The development loop

The Claude sessions that build this repo meet the same decision points as any coding agent.
These are the ecosystem's best-measured uses, mapped to our own rules:

| Hook | Checks | Our rule it serves | Evidence |
| :--- | :--- | :--- | :--- |
| **Done gate** (Stop hook) | Files changed and no check ran since, so is "done" unverified? | Principle 5: verify before handing over | AUROC 0.976 on 100 labeled stops **[T]** |
| **Convention gate** (post-edit, or advisory CI) | Meaning-level rules: one fact in one file, the rule of three, write boundaries in prose, `AGENTS.md` conventions a parser can't check | Principles 3, 9; ownership | Our spike: AUROC 1.0 on synthetic snippets **[V]**; Abide: 10 of 39 real flags confirmed **[T]** |
| **Scope and intent gate** | Edits outside what was asked, or edits made in answer to a question | The user's prefixes (S, M, D) and the protocol's roles | jev-gates **[T]** |
| **Commit honesty** (pre-commit) | Does the message match the staged diff? | The git policy's conventional commits | jev-commit **[T]** |
| **Rule selection** | Load only the rules that apply to this task | Context economy in long sessions | jev-rules **[T]** |

**How we propose to introduce them:**

1. **Advisory first.** A hook reports; it doesn't block. Every gate escalates and never approves.
2. **Static rules stay the boundary.** Deny lists and `check_docs.py` come before any decider.
3. **Measure on our own replays before anything blocks.** Replaying past sessions, the way Abide
   replayed 93, gives us our own precision. Those transcripts belong to the user, so reading
   them is the user's call. The research office can run the replay if the user allows it.
4. **Installing hooks changes what sessions may do.** That makes it a security-settings decision
   for the user, made with the lead.

## Why not memory

The protocol has offices talk through files, never through memory. This office's auto-memory
records only the user's stance and its own role, never instructions for other roles.

## What this office already does itself

Inside its own remit, this office uses the decider for its own work. In this redo it classified
551 builds for $0.03, and validated them against a hand-labeled sample
([EV-2026-09-27-jev-ecosystem-map](../../evidence/EV-2026-09-27-jev-ecosystem-map/README.md)).
The decider's confidence marked which labels needed a human look: all 19 sample items at
confidence ≥ 0.9 matched the hand labels.
