# P5 Design Card: Memory-Rich Personal Assistant

- Created: 2026-09-11 (Session 0). Revised: 2026-09-13 (identity via runtime context, skills
  route, actual tools); 2026-09-14 (B2 write governance, assistant skills); 2026-09-17 (B3
  content guardrails: one gate in the memory storage, security guard, secret detectors,
  Finglish repair).
- Code: `agents/personal_assistant_agent.py`, `middlewares/memory_approval_middleware.py`,
  `middlewares/security_guard_middleware.py`, `middlewares/finglish_output_middleware.py`,
  `utils/memory_backend_util.py`, `utils/secret_redaction_util.py`,
  `apps/personal_assistant_app.py`, skills under `resources/skills/personal_assistant/`.
  Stages: `docs/ROADMAP.md` (P5). Decisions:
  [ADR-0003](../adr/0003-runtime-context-for-user-identity.md),
  [ADR-0008](../adr/0008-memory-write-governance.md),
  [ADR-0010](../adr/0010-one-gate-in-memory-storage.md).

## Memory model

| Kind | Scope | Mechanism in this repo |
| :--- | :--- | :--- |
| Short-term (working) | One thread | Checkpointer + `StateBackend` (unrouted paths) |
| Long-term declarative | One user, across threads | `GatedMemoryBackend` (a `StoreBackend`) on `/memories/`, namespace `(user_id, "memories")`: profile plus one file per goal under `/memories/goals/` |
| Procedural (skills) | Shared across users, read-only | `SkillsMiddleware` over `/skills/` -> `FilesystemBackend` on `resources/skills/personal_assistant` (`memory-curation`, `goal-plan`) |
| Episodic | One user, searchable history | Not built (candidate for Phase C or later) |

`CompositeBackend` routes by longest path prefix. `MemoryMiddleware` loads
`/memories/user_profile.md` into the prompt every turn. `SkillsMiddleware` loads the skill list
once per thread. Guard verdicts are cached per user under `(user_id, "memory_verdicts")`.

## Card

1. **User job:** remember approved facts, preferences, constraints, and goals across sessions,
   without bloating the context or inventing memories.
2. **Role boundary:** owns the user profile, preferences, goal plans, and skill selection.
   Delegates code execution (P4), code review (P3), and deep research (P1).
3. **Environment:** a LangGraph store (in-memory now, SQLite in C1), the checkpointer, and the
   packaged skill files.
4. **Tools:**
   - DeepAgents file tools (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`,
     `grep`) over the routed backend;
   - `web_search` (Tavily);
   - `task` for delegation.
5. **Input:** `messages`. Config carries `thread_id`; runtime context is
   `UserContext(user_id)`, required on every call including resumes.
6. **Output:** a chat answer, with Perso-Arabic script repaired into Finglish. Long-term side
   effects are files under `/memories/`.
7. **State:** the thread's messages and scratch files are transient; `/memories/` persists per
   user in the store.
8. **Side effects:** creating, editing, and deleting memory files.
9. **Risk:** every memory change passes one gate in the storage, shared by the assistant and
   its subagents (B3, [ADR-0010](../adr/0010-one-gate-in-memory-storage.md)): adding an
   ordinary fact runs; overwriting, destructive edits, deletions, and sensitive content wait
   for approval; secrets and credentials are refused. The user's typed input is redacted at
   the app boundary before anything records it. Shared skills are read-only for the assistant;
   only `skill_designer` writes them (C3).
10. **Failure contract:** missing user identity raises an error (it never falls back to a
    shared user). A guard that fails, times out, or returns an unparsable verdict becomes
    "ask". The Finglish repair fails open: an unrepaired line is kept and logged. Store
    failures should degrade to a stateless answer (C1).
11. **Verification:**
    - `tests/test_personal_assistant.py`: real graph, scripted model and guard: user
      isolation, the gate (add, insert, overwrite, destructive edit, delete, delegated write,
      secret, block, guard reasons, verdict cache), read-only skills, CLI resume with context;
    - `tests/test_security_guard.py`, `tests/test_secret_redaction_util.py`,
      `tests/test_finglish_output_middleware.py`, `tests/test_run_with_hitl.py`;
    - live checks (2026-09-13/17): two-user recall; approvals, rejections, and refusals with
      the real guard (33/33 policy cases); secrets redacted before the graph; trace uploads
      masked; leaked script cut from 215 lines to 55 across three long plans;
    - memory eval-lite in C2 (rejection evasion, false "saved" claims, guard accuracy, and an
      assistant-model comparison).
12. **Composition boundary:** a context provider that exposes preferences and constraints to
    workflows (decided in C4, first used in P6). `PIIMiddleware` joins there, so input
    protection travels with the agent to other callers.
13. **Cost and latency:** tier `low`, provider pinned to `openai` (`gpt-5.6-luna`), because
    `gemini-3.5-flash-lite` claimed memory writes it never made. The guard and the Finglish
    repair are extra `low`-tier calls: the guard once per judged change (cached across a
    resume), the repair only when a final answer leaks. Consolidation tier is decided in B4.
14. **Privacy boundary:** secrets are redacted at the app boundary, refused by the memory
    gate, and masked in traces by a LangSmith anonymizer. Conversation content still reaches
    traces. Sensitive facts are stored only with the user's approval.
15. **Phase C output:** a durable, per-user memory specialist with governed writes, skills,
    and an eval-lite suite.
