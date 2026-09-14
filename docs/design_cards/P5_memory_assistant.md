# P5 Design Card: Memory-Rich Personal Assistant

- Created: 2026-09-11 (Session 0). Revised: 2026-09-13 (identity via runtime context, skills
  route, actual tools); 2026-09-14 (B2 write governance, assistant skills).
- Code: `agents/personal_assistant_agent.py`, `middlewares/memory_approval_middleware.py`,
  `utils/memory_backend_util.py`, `apps/personal_assistant_app.py`, skills under
  `resources/skills/personal_assistant/`. Stages: `docs/ROADMAP.md` (P5). Decisions:
  [ADR-0003](../adr/0003-runtime-context-for-user-identity.md),
  [ADR-0008](../adr/0008-memory-write-governance.md).

## Memory model

| Kind | Scope | Mechanism in this repo |
| :--- | :--- | :--- |
| Short-term (working) | One thread | Checkpointer + `StateBackend` (unrouted paths) |
| Long-term declarative | One user, across threads | `StoreBackend` on `/memories/`, namespace `(user_id, "memories")`: profile plus one file per goal under `/memories/goals/` |
| Procedural (skills) | Shared across users, read-only | `SkillsMiddleware` over `/skills/` -> `FilesystemBackend` on `resources/skills/personal_assistant` (`memory-curation`, `goal-plan`) |
| Episodic | One user, searchable history | Not built (candidate for Phase C or later) |

`CompositeBackend` routes by longest path prefix. `MemoryMiddleware` loads
`/memories/user_profile.md` into the prompt every turn. `SkillsMiddleware` loads the skill list
once per thread.

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
6. **Output:** a chat answer. Long-term side effects are files under `/memories/`.
7. **State:** the thread's messages and scratch files are transient; `/memories/` persists per
   user in the store.
8. **Side effects:** creating, editing, and deleting memory files.
9. **Risk:** adding a fact runs freely. Overwriting, destructively editing, or deleting stored
   memory waits for approval, decided in code (B2). Sensitive content needs the PII guardrail
   and security guard (B3); until then the skill tells the model to skip sensitive facts unless
   asked. Shared skills are read-only for the assistant; only `skill_designer` writes them (C3).
10. **Failure contract:** missing user identity raises an error (it never falls back to a
    shared user). An unknown file state during an approval check asks the human. Store
    failures should degrade to a stateless answer (C1).
11. **Verification:**
    - `tests/test_personal_assistant.py`: real graph, scripted model: user isolation, the
      approval rules (add, insert, overwrite, destructive edit, delete, delegated write,
      read-only skills), CLI resume with user context;
    - `tests/test_run_with_hitl.py`: streamed approval loop, including one prompt per
      subagent interrupt;
    - live checks (2026-09-13/14): two-user recall; approvals and rejections; skills read on
      demand mid-conversation and after ~150k characters of context;
    - memory eval-lite in C2 (includes rejection evasion and false "saved" claims).
12. **Composition boundary:** a context provider that exposes preferences and constraints to
    workflows (decided in C4, first used in P6).
13. **Cost and latency:** tier `low`, provider pinned to `openai` (`gpt-5.6-luna`), because
    `gemini-3.5-flash-lite` claimed memory writes it never made. Consolidation tier is decided
    in B4.
14. **Privacy boundary:** never store credentials or secrets. LangSmith traces currently
    include conversation content. Long replies leak Perso-Arabic script despite the prompt
    rule; a deterministic output check lands in B3.
15. **Phase C output:** a durable, per-user memory specialist with governed writes, skills,
    and an eval-lite suite.
