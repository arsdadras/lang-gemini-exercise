# P5 Design Card: Memory-Rich Personal Assistant

- Created: 2026-09-11 (Session 0). Revised: 2026-09-13 (identity via runtime context, skills
  route, actual tools); 2026-09-14 (B2 write governance, assistant skills); 2026-09-17 (B3
  content guardrails); 2026-09-22 (B4: read-only assistant, background consolidator);
  2026-09-23 (P5 complete: history and undo, durable memory, eval-lite, skill designer,
  context provider).
- Code: `agents/personal_assistant_agent.py`; `graphs/` and `nodes/` `memory_consolidation_*`
  and `skill_designer_*`; `middlewares/memory_approval_middleware.py`,
  `security_guard_middleware.py`, `finglish_output_middleware.py`;
  `utils/memory_backend_util.py`, `memory_session_util.py`, `secret_redaction_util.py`;
  `tools/user_context_tool.py`; `apps/personal_assistant_app.py` (`lab-assistant`),
  `apps/personal_brief_app.py` (`lab-brief`); `evals/p5_memory_eval.py`; skills under
  `resources/skills/personal_assistant/`. Decisions:
  [ADR-0003](../adr/0003-runtime-context-for-user-identity.md),
  [ADR-0008](../adr/0008-memory-write-governance.md),
  [ADR-0010](../adr/0010-one-gate-in-memory-storage.md),
  [ADR-0012](../adr/0012-memory-consolidation-single-writer.md),
  [ADR-0013](../adr/0013-p5-completion.md).

## Memory model

| Kind | Scope | Mechanism in this repo |
| :--- | :--- | :--- |
| Short-term (working) | One thread | SQLite checkpointer + `StateBackend` (unrouted paths) |
| Long-term declarative | One user, across threads | `StoreBackend` on `/memories/`, namespace `(user_id, "memories")`: profile plus one file per goal. Read-only for the assistant; written only by the consolidator through `GatedMemoryBackend` |
| Procedural (skills) | Shared across users, read-only for the assistant | `SkillsMiddleware` over `/skills/` (packaged, `goal-plan`) and `/published-skills/` (store namespace `("shared", "skills")`, written only by the skill designer) |
| Episodic | One user, searchable history | Not built (trigger in the handoff backlog) |

Per-user bookkeeping in the store: `memory_verdicts` (guard cache), `memory_history` (previous
versions), `memory_rejections`, `threads` (consolidation watermarks), `memory_reviews` (pending
reviews). `MemoryMiddleware` loads the profile every turn.

## Card

1. **User job:** remember approved facts, preferences, constraints, and goals across sessions,
   without bloating the context or inventing memories.
2. **Role boundary:** owns the user's memory and the shared skill library. Delegates code
   execution (P4), code review (P3), and deep research (P1).
3. **Environment:** SQLite store and checkpointer under `out/state/` (apart from the other
   apps), the packaged skill files.
4. **Tools:** DeepAgents file tools over the routed backend (writes to `/memories/`, `/skills/`,
   and `/published-skills/` denied); `web_search`; `task` for delegation.
5. **Input:** `messages`. Config carries `thread_id`; runtime context is
   `UserContext(user_id)`, required on every call including resumes.
6. **Output:** a chat answer, with Perso-Arabic script repaired into Finglish. Memory changes
   happen after the conversation, as reviewed proposals.
7. **State:** conversations, memory, bookkeeping, and pending reviews are durable; the app
   resumes the last user and thread.
8. **Side effects:** memory changes through the consolidator only (ADR-0012); skills through
   the skill designer only, after approval (ADR-0013).
9. **Risk:** every consolidator edit passes one gate (ADR-0010): additions run; replacements,
   removals, and sensitive content wait for approval, one edit at a time; a correction the user
   explicitly asked for runs without approval because the previous version is kept; secrets
   are refused. `/undo` reverts, `/forget` deletes everything about a user.
10. **Failure contract:** missing identity raises (never a shared default). A failed guard
    becomes "ask". A failed consolidation is reported and leaves memory unchanged; an
    interrupted one resumes on the next start. The Finglish repair fails open.
11. **Verification:** unit tests with real graphs, SQLite, and scripted models
    (`test_personal_assistant.py`, `test_memory_consolidation.py`, `test_memory_session_util.py`,
    `test_skill_designer.py`, `test_user_context_tool.py`, and others); live eval-lite
    `evals/p5_memory_eval.py` (results in the handoff).
12. **Composition boundary:** a context provider, `get_user_context` (read-only, identity from
    `UserContext`, secrets redacted). Callers that send text outward add `PIIMiddleware` on tool
    results. Mini-workflow: `lab-brief` (P5 + P1).
13. **Cost and latency:** assistant `low` tier pinned to `openai` (`gpt-5.6-luna`); guard and
    Finglish repair `low`; consolidator `medium` pinned to `anthropic` (`claude-sonnet-5`,
    measured on implicit conflicts); skill designer `medium`. Consolidation runs in the
    background and never delays a reply.
14. **Privacy boundary:** secrets redacted at the app boundary, refused by the gate, and
    masked in traces; reviewed consolidation runs drop their checkpoints; personal data is
    redacted before a composing agent's model sees P5's context.
15. **Phase C output:** a durable, per-user memory specialist with governed writes, governed
    skills, a context-provider boundary, and an eval-lite suite.
