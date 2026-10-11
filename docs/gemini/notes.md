# Gemini General Notes & Project Context

This file serves as Gemini's internal working notebook for general project context, architectural state, and ongoing observations in the `agentlab` (`lang_claude_exercise`) repository.

- **Evaluations & Feedbacks for Developer/Claude:** Stored separately under [`feedbacks/`](feedbacks/):
  - [`developer_evaluation.md`](feedbacks/developer_evaluation.md): Initial architectural & engineering review.
  - [`product_ideas_and_refinements.md`](feedbacks/product_ideas_and_refinements.md): 10 new product ideas & 5 concrete refinements to current implementations.

---

## 1. Project Overview & Context

- **Repository:** `https://github.com/arsdadras/lang_claude_exercise.git` (owner: `arsdadras`)
- **Active Branch:** `main`
- **Core Technology Stack:**
  - Python >= 3.12 (developed on 3.14, managed via `uv`, linted with `ruff`, tested via `pytest`)
  - Frameworks: `langchain` (>=1.4.2), `langgraph` (>=1.2.12), `deepagents` (>=0.7.20), `langsmith`, `pydantic` (v2), `chromadb` (`langchain-chroma`), `langchain-google-genai`, `langchain-openai`, `langchain-tavily`, `langchain-typesafe`.
  - Architecture: Single-package structure (`src/agentlab`) acting as a production-track agentic AI curriculum (Term P: P1–P14 across two semesters).

---

## 2. Current Curriculum & Build State

- **Completed Specialists (P1–P5):**
  - **P1:** Evidence-grounded research agent (`lab-research`).
  - **P2:** Corrective RAG graph with self-grading & web fallback (`lab-rag`, `lab-repo-insight`).
  - **P3:** Multi-subgraph code review pipeline with sandboxed verification (`lab-code-review`).
  - **P4:** Sandboxed Python interpreter with HITL approval & artifact handling (`lab-interpreter`, `lab-coordinator`).
  - **P5:** Governed per-user memory assistant with SQLite persistence & skill designer (`lab-assistant`, `lab-brief`).
- **Return Pass Status (R0–R5):**
  - **R0:** Specialist contract standardized (`SpecialistResult[T]`, `UserContext`, declared side effects, failure taxonomy).
  - **R1 (Active):** Multi-source evidence-grounded researcher upgrade.
    - Topic 1 (Claims & claim check) & Topic 2 (Query options and planning): Completed.
    - Topic 3 (Multi-source router: web, academic via Exa, private corpus): Built and live-verified.
    - Topic 4 (Stop condition: `evidence_enough` loop): Next in queue.
  - **Upcoming:** R2 (RAG hybrid search/rerank) -> R3 (Deterministic tools first) -> R4 (Interpreter upgrade) -> P5 teaching pass -> R5 (Close) -> D1 (Decision engineering workbench) -> P6 (Content generator).

---

## 3. Key Architectural Patterns & Constraints

1. **Downwards Dependency Flow:**
   `apps -> agents -> (subagents, graphs) -> (nodes, middlewares, tools, retrieval) -> (models, prompts, schemas, data, utils) -> configs`
2. **Zero Import-Time Side Effects:** All configuration, environment loading, and graph builds occur inside factories and CLI `main()`.
3. **Seams & Modularity:**
   - Model Tier Catalog & Fallbacks: `agentlab.models.registry_model`, `fallback_middleware.py`.
   - Decision Models: `agentlab.models.decision_model` (`typesafe`/Jev integration).
   - Jev Model Router: `agentlab.models.router_model`.
   - Security: Sandboxed environments (`build_sandbox_env`), secret isolation, denial of `.env` reads, HITL on consequential tools.
4. **Operational Rules for Gemini:**
   - Zero code edits unless explicitly instructed by the user.
   - `docs/gemini/` is gitignored and never pushed to remote.
