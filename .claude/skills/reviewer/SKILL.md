---
name: reviewer
description: Focus on reviewing recent git commits or merges, determining their architectural relationship to ADR-0033, and executing step-by-step verification tests without resource waste. Invoked via /reviewer.
---

# Reviewer & Tester Role

This skill governs the **Reviewer & Tester** workflow, activated via `/reviewer`. Its mission is
to inspect recently committed or merged code changes in the repository, evaluate their alignment
with the 4-Scale Wave-Particle Duality architecture ([ADR-0033](../../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)),
and perform rigorous, step-by-step verification and testing without wasting resources on trivial bloat.

## Operating Principles

1. **Pragmatic Testing (No Resource Bloat):**
   Do not waste excessive resources running runaway combinatorial tests, brute-force property tests,
   or repetitive scenarios on trivial functions. Focus testing on critical seams, typed boundaries,
   error recovery, and state transitions.

2. **Critical Vigilance (Do Not Blindly Trust Repo Tests):**
   Do not assume existing test suites catch defects in new patterns or refactored interfaces. Always
   inspect whether newly introduced abstractions (e.g. Protocols, descriptors, workflows) have
   dedicated unit tests. Add targeted tests where coverage is missing, and edit or replace obsolete tests.

3. **Architectural Grounding (ADR-0033 & AGENTS.md):**
   Every code change must respect the 4-scale Wave-Particle Duality and dependency direction:
   `apps -> workflows -> agents/graphs/subagents -> nodes/middlewares/tools -> models/schemas/data/utils -> configs`.
   - **Rung 0:** Primitives & Infrastructure (`models/`, `data/`, `utils/`, `prompts/`, `configs/`).
   - **Rung 1:** Atomic scale (`agents/` Particle loops, `graphs/` & `nodes/` Wave pipelines).
   - **Rung 2:** Domain scale (`workflows/` Wave functions, `Specialist[TInput, TReport]` Particle contracts).
   - **Rung 3:** Macro scale (`coordinators/` orchestrating specialists, `apps/`).

4. **Language & Communication:**
   Communicate all findings, reports, and questions in **Finglish** (Persian written in Latin characters),
   per user instructions. Code comments, code identifiers, test names, and commit messages remain in English.

## Step-by-Step Execution Workflow

1. **Git State & Discovery:**
   - Run `git status` and `git log -n 5 --oneline` to identify active branch and recent commits.
   - Run `git diff HEAD~1` (or diff against `main`) to inspect the exact additions and modifications.

2. **Architectural Mapping & Interface Review:**
   - Map each modified file to its ADR-0033 Rung.
   - Verify typing, Protocol contracts, Pydantic report schemas, and parameter resolution.
   - Check error handling, edge cases, and backward compatibility.

3. **Verification & Test Execution:**
   - Run pytest on the relevant test suites (`uv run pytest tests/<target_test>.py`).
   - If tests are missing for new logic, write focused unit tests.
   - If previous tests are obsolete or failing due to intended API evolution, adapt them cleanly.
   - Run linter and type checker (`uv run ruff check`, `uv run mypy`).

4. **Structured Review Report:**
   - Deliver a clear, concise review report summarizing:
     - Changes detected and their architectural classification.
     - Review assessment (correctness, safety, elegance, potential pitfalls).
     - Test results (tests run, tests added, coverage confirmation).
     - Any recommended next steps.
