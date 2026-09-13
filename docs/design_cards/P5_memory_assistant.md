# P5 Design Card: Memory-Rich Personal Assistant

- Created: 2026-09-11 (Session 0). Revised: 2026-09-13 (identity via runtime context, skills
  route, actual tools).
- Code: `agents/personal_assistant_agent.py`, `utils/memory_backend_util.py`,
  `apps/personal_assistant_app.py`. Stages: `docs/ROADMAP.md` (P5).

## Memory model

| Kind | Scope | Mechanism in this repo |
| :--- | :--- | :--- |
| Short-term (working) | One thread | Checkpointer + `StateBackend` (unrouted paths) |
| Long-term declarative | One user, across threads | `StoreBackend` on `/memories/`, namespace `(user_id, "memories")` |
| Procedural (skills) | Shared across users | `SkillsMiddleware` over `/skills/` -> `FilesystemBackend` on `resources/skills/personal_assistant` |
| Episodic | One user, searchable history | Not built (candidate for Phase C or later) |

`CompositeBackend` routes by longest path prefix. `MemoryMiddleware` loads
`/memories/user_profile.md` into the prompt every turn.

## Card

1. **User job:** remember approved facts, preferences, and constraints across sessions,
   without bloating the context or inventing memories.
2. **Role boundary:** owns the user profile, preferences, and skill selection. Delegates code
   execution (P4), code review (P3), and deep research (P1).
3. **Environment:** a LangGraph store (in-memory now, SQLite in C1), the checkpointer, and the
   packaged skill files.
4. **Tools:**
   - DeepAgents file tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) over
     the routed backend;
   - `web_search` (Tavily);
   - `task` for delegation.
5. **Input:** `messages`. Config carries `thread_id`; runtime context is
   `UserContext(user_id)` and is required.
6. **Output:** a chat answer. Long-term side effects are files under `/memories/`.
7. **State:** the thread's messages and scratch files are transient; `/memories/` persists per
   user in the store.
8. **Side effects:** creating and editing memory files.
9. **Risk:** ordinary preference updates are low risk. Overwriting a profile, or storing
   sensitive data, needs approval (B2) and a PII guardrail (B3).
10. **Failure contract:** missing user identity raises an error (it never falls back to a
    shared user). Store failures should degrade to a stateless answer (C1).
11. **Verification:**
    - `tests/test_personal_assistant.py`: real graph, scripted model, two users isolated;
    - live two-user recall check (2026-09-13);
    - memory eval-lite in C2.
12. **Composition boundary:** a context provider that exposes preferences and constraints to
    workflows (decided in C4, first used in P6).
13. **Cost and latency:** tier `low`, provider pinned to `openai` (`gpt-5.6-luna`), because
    `gemini-3.5-flash-lite` claimed memory writes it never made. Consolidation tier is decided
    in B4.
14. **Privacy boundary:** never store credentials or secrets. LangSmith traces currently
    include conversation content.
15. **Phase C output:** a durable, per-user memory specialist with governed writes, skills,
    and an eval-lite suite.
