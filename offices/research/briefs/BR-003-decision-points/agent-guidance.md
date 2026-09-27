# BR-003 › Agent guidance: how every session learns to weigh decision models

Supports [BR-003](README.md). The user asked, on 2026-09-27, that the Claude agents in every
session know this concept and consider it in their designs and work, without forcing it.

## What exists now

[design guide](../../landscape/decision-models/design-guide.md),
maintained by the research office. It is the shared guidance for every role:

- what decision models are;
- the rubric for choosing a backend;
- question design;
- the recurring policies;
- how to call Jev in this repo;
- how each role raises a use.

## Discovery: proposals for the lead

These files are the lead's; requested in the outbox as RS-011.

1. **Index the entry** in the library.
2. **Add one line where every session looks.** `CLAUDE.md` routes sessions, and `AGENTS.md` is
   read by any coding agent. Proposed line:

   > **AI decision points.** Before designing or reviewing a step where a model classifies,
   > routes, grades, gates, or verifies, read `library/engineering/decision-models.md`.

3. **Add a shared-procedure skill** in `.claude/skills/`, which is the lead's. The line reaches
   every session's context; the skill surfaces at the moment of design, when its description
   matches the task. Proposed text:

   ```markdown
   ---
   name: decision-points
   description: Use when designing, planning, or reviewing an AI step that decides rather than
     writes (classify, route, grade, gate, verify, approve, score), or when choosing between
     plain code, an LLM, a decision model such as Jev, or a cascade for such a step.
   ---

   1. Read `library/engineering/decision-models.md` and apply its rubric to the step.
   2. Record the result where your role records design: the design card's decision points
      (lead), the handoff's "For the office" section (mentor), or a brief (research).
   3. Never add a dependency or change a call site outside your role's plan; a new backend
      enters through the lead's radar.
   ```

The protocol has offices talk through files, never through memory. So this office didn't use
Claude's auto-memory to reach other sessions.

## Uses in our own work: ideas for the lead

- **`scripts/check_docs.py` and one fact, one file.** Embeddings or keywords would find
  candidate paragraph pairs, and a `noul` would ask "does A restate a fact that B owns?".
  Measure on a labeled sample before it reports anything.
- **Claude Code permission prompts (a security setting, so the user's call).**
  - **The pattern:** OpenRouter's recipe auto-approves a shell command only when Jev rates it at
    least 0.9 on both "reversible" and "serves the task". A static risk list is the real
    boundary.
  - **Why not yet:** measured against the current prompt-every-time setup, that is a loosening.
    By principle 4's logic, it first needs a labeled sample of our own commands with no
    dangerous approvals.
