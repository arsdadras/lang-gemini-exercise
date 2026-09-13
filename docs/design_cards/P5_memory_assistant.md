# Project P5: Memory-Rich Personal Assistant
## Architectural Specification & 15-Point Design Card

- **Project:** P5 — Memory-Rich Personal Assistant
- **Curriculum Milestone:** Pre-Capstone Specialist (Feeds P6 Midterm Capstone)
- **Status:** Phase A In-Progress (Session 0 Approved)
- **Created Date:** 2026-09-11
- **Target Location:** `src/agents/personal_assistant_agent.py`, `src/apps/personal_assistant_app.py`
- **Model Tiers:**
  - Primary / Conversational: `low` tier (`gemini-3.5-flash-lite`)
  - Intermediate / Routing: `medium` tier (`gemini-3.8-flash`)
  - Strategic / Background Consolidation: `medium` tier (`gemini-3.8-flash`)

---

## 1. Problem Statement & Domain Vision

Agents must support ongoing, persistent user relationships across disparate sessions and threads. In typical stateless or single-thread agent systems (P1–P4), restarting or initiating a new `thread_id` resets the agent to a tabula rasa. 

P5 bridges this gap by engineering a production-grade **Memory-Rich Personal Assistant** capable of:
1. Remembering user preferences, historical constraints, and biographical facts across multiple conversation threads.
2. Preventing context window explosion and token bloat by using a decoupled Long-Term Store rather than dumping raw conversation history into the system prompt.
3. Guarding against memory drift, stale knowledge, and unauthorized hallucinated memory writes.
4. Providing a foundational memory and personalization engine that supplies context to the P6 Midterm Research-to-Decision Capstone.

---

## 2. Agentic Memory Taxonomy

To prevent architectural ambiguity, memory is partitioned into four distinct operational layers:

```
+-----------------------------------------------------------------------------------+
|                           AGENTIC MEMORY TAXONOMY                                 |
+-----------------------------------------------------------------------------------+
| 1. Short-Term Memory (Thread / Working State)                                     |
|    - Scope: Single thread / turn (`thread_id`).                                   |
|    - Mechanism: LangGraph Checkpointer (`InMemorySaver` / `SqliteSaver`).         |
|    - Channel: `messages` list, current turn scratchpad (`StateBackend`).         |
+-----------------------------------------------------------------------------------+
| 2. Long-Term Declarative Memory (Profile & Semantic Facts)                        |
|    - Scope: Cross-thread, Cross-session, Per-User namespace.                      |
|    - Mechanism: LangGraph `BaseStore` (`InMemoryStore` / `SqliteStore`).          |
|    - Storage Path: Virtual filesystem route `/memories/` (`StoreBackend`).        |
|    - Payload: User profile, persistent preferences, technical constraints.        |
+-----------------------------------------------------------------------------------+
| 3. Procedural Memory (Skills / Behavioral SOPs)                                   |
|    - Scope: Reusable behavior patterns and specialized domain procedures.         |
|    - Mechanism: Dynamic Skill injection via `/skills/*.md` (`StoreBackend`/FS).  |
|    - Payload: Coding conventions, research guidelines, operational recipes.       |
+-----------------------------------------------------------------------------------+
| 4. Episodic / Associative Memory (Historical Experience Retrieval)                |
|    - Scope: Semantic indexing across historical interactions.                     |
|    - Mechanism: Vector-indexed store / Chroma / LangGraph Store vector search.    |
|    - Payload: Prior decision rationale and resolution history.                    |
+-----------------------------------------------------------------------------------+
```

---

## 3. DeepAgents Backend Architecture

DeepAgents models memory as a **Virtual Filesystem Abstraction**, allowing the agent to read and mutate memory using standard filesystem tools (`read_file`, `write_file`, `edit_file`, `ls`).

The underlying routing is governed by `CompositeBackend` using longest-prefix route matching:

```
                            +--------------------------+
                            |     Agent Tool Call      |
                            | write_file("/memories/..)|
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |     CompositeBackend     |
                            +------------+-------------+
                                         |
                    +--------------------+--------------------+
                    | (Prefix: /memories/)                    | (Default fallback)
                    v                                         v
       +-------------------------+               +-------------------------+
       |      StoreBackend       |               |      StateBackend       |
       +------------+------------+               +------------+------------+
                    |                                         |
                    v                                         v
       +-------------------------+               +-------------------------+
       |   LangGraph BaseStore   |               | LangGraph State Channel |
       | (Cross-thread, Durable) |               |  (files key, Ephemeral) |
       +-------------------------+               +-------------------------+
```

### Core Backend Components:
- **`StateBackend`:** Stores files inside LangGraph's state channels under the `files` key. Ephemeral; persists across turns within the same thread checkpoint, but vanishes across new threads.
- **`StoreBackend`:** Persists files into LangGraph's `BaseStore` across all threads and sessions. Namespaced dynamically via `lambda rt: (user_id, "memories")`.
- **`CompositeBackend`:** Routes file operations by prefix. Routes `/memories/` to `StoreBackend`, `/skills/` to skill backend/store, and unrouted paths to `StateBackend`.
- **`MemoryMiddleware`:** Reads `/memories/` files (e.g. `/memories/user_profile.md`) at the beginning of each turn, injecting them into the system prompt inside `<agent_memory>`, accompanied by behavioral write guidelines in `<memory_guidelines>`.

---

## 4. 15-Point Agent Design Card (Roadmap v2 Section 7)

```yaml
1. User Job:
   Enable persistent, personalized user continuity by remembering approved facts, preferences, constraints,
   and past context across disparate sessions without context window explosion or hallucinated memory drift.

2. Role Boundary:
   - Owns: Long-term user profile management, preference recording, dynamic skill loading, memory conflict
     resolution, and PII guardrails.
   - Refuses/Delegates: Heavy code execution (delegates to P4/Interpreter), deep code audits (delegates to P3),
     and external multi-source research (delegates to P1).

3. Environment:
   LangGraph `BaseStore` (in-memory for Phase A/B, SQLite for Phase C), LangGraph checkpointer (`InMemorySaver`),
   and virtual filesystem backends (`CompositeBackend`).

4. Tools:
   - Memory & Virtual Filesystem: `read_file`, `write_file`, `edit_file`, `ls` (routed via CompositeBackend).
   - Knowledge Acquisition: `web_search` (Tavily search for factual verification).
   - Personal Utility Tools: `manage_notes`, `set_preference` (Phase A/B).

5. Input Schema:
   `messages: list[BaseMessage]` passed with runtime context in `RunnableConfig["configurable"]`:
   - `thread_id: str` (active conversation thread)
   - `user_id: str` (tenant/user partition for StoreBackend)

6. Output Schema:
   Standard text responses (`AIMessage`) with inline references to recalled context, alongside background state
   and store channel writes.

7. State:
   - Transient / Thread: `messages`, `todos`, active turn files (`StateBackend`).
   - Durable / Cross-Thread: Files stored under `(user_id, "memories")` namespace in `BaseStore` (`StoreBackend`).

8. Side Effects:
   Mutating persistent long-term storage (creating, updating, or editing markdown records under `/memories/`).

9. Risk Level:
   - Low Risk: Reading memory, updating ordinary preferences ("I write code in Python").
   - High Risk: Overwriting/clearing complete profiles, storing sensitive personal or financial credentials.
     Requires HITL confirmation in Phase B.

10. Failure Contract:
    Store read/write errors must degrade gracefully. If the persistent store fails or is unreachable, the assistant
    continues functioning as a stateless conversation agent rather than crashing.

11. Verification:
    - Cross-Thread Continuity: Turn 1 on `thread_1` sets a preference; Turn 2 on `thread_2` with the same `user_id`
      recalls and honors that preference automatically.
    - Tenant Isolation: User A (`user_1`) cannot access or mutate User B (`user_2`) memories.

12. Composition Boundary:
    Wrapped as a reusable `PersonalizationSubAgent` providing user context, guidelines, and constraints to the P6
    Capstone Coordinator.

13. Cost/Latency & Model Tiers:
    - Conversational loop: `low` tier (`gemini-3.5-flash-lite`) for rapid latency and low cost.
    - Routing & Synthesis: `medium` tier (`gemini-3.8-flash`).
    - Periodic memory consolidation: background subagent on `medium` tier (`gemini-3.8-flash`).

14. Privacy Boundary:
    Strict PII protection middleware: Never persist API keys, passwords, tokens, or sensitive financial data into
    memory files.

15. Phase C Deliverable:
    Production-grade `PersonalAssistantAgent` with durable SQLite backing store, per-user namespace isolation,
    dynamic skills engine, and memory drift evaluation.
```

---

## 5. Phased Implementation Roadmap

- **Phase A — Baseline Composite Memory:**
  - Setup `CompositeBackend`: default `StateBackend` + `/memories/` route to `StoreBackend`.
  - Initialize `InMemoryStore` and `InMemorySaver`.
  - Bootstrap `MemoryMiddleware` with `/memories/user_profile.md` source.
  - Deliver runnable interactive CLI app (`src/apps/personal_assistant_app.py`) verifying multi-thread memory retention.
- **Phase B — Skills & Memory Governance:**
  - Skills library (`/skills/*.md`) for procedural instruction loading.
  - Background Memory Consolidation Subagent for deduplication and summarization.
  - HITL interrupt on sensitive/destructive memory overwrites.
  - PII scrubbing middleware.
- **Phase C — Enterprise Multi-Tenant & Durable Store:**
  - Transition from `InMemoryStore` to `SqliteStore` (`data/personal_assistant_store.db`).
  - Strict tenant partitioning on `(user_id, "memories")`.
  - Refactor `session_util.py` to multi-tenant 2D configuration (`thread_id` + `user_id`) and unify `personal_assistant_app.py` CLI session resolution.
  - Memory conflict resolution and drift evaluation harness.
  - Reusable specialist package feeding the P6 Midterm Capstone.
- **Phase D — Production Hardening & Architectural Best Practice:**
  - Enterprise Domain Registry: Refactor static routing into a declarative `MemoryDomainRegistry` to support dynamic, multi-tenant memory domains (system, tenant, project, user).
  - Uncompromised enterprise patterns: full elimination of shortcuts and strict adherence to large-scale system patterns.
  - End-to-end performance tuning, memory compaction efficiency, and resilience testing.
