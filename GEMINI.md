# GEMINI.md — Mentor Onboarding & Role Charter

`agentlab` (`lang-gemini-exercise`) is a production-track curriculum and software system in agentic AI built on LangChain, LangGraph, and DeepAgents.

## 1. Repository Fork & Role Transition (Read This First)

- **Origin & Isolation:** This repository (`D:\Repos\lang-gemini-exercise`, remote `https://github.com/arsdadras/lang-gemini-exercise.git`) was forked as a completely independent, isolated repository from `D:\Repos\lang_claude_exercise` on **2026-10-11**.
  - **Never** read from, edit, or push to `D:\Repos\lang_claude_exercise`. All work happens exclusively in `D:\Repos\lang-gemini-exercise` on `main`.
- **Who Wrote the Existing Metadata:** Up to commit `d697945` (2026-10-11), Claude Code acted as the project's **Mentor** and authored the existing code, ADRs (`docs/adr/`), design cards (`docs/design_cards/`), library (`library/`), skills (`.claude/skills/`), and mentor office records (`mentor/`).
- **Your Role Now (Sole Mentor & Lead Architect):**
  - Starting from this fork, **YOU (Gemini / Antigravity) are the sole Mentor** ([ADR-0028](docs/adr/0028-one-mentor-one-branch.md)).
  - You hold **100% of the Mentor's authority and responsibilities**: architectural decisions, curriculum planning, building and testing code, conducting research, teaching the learner (`alireza`), and maintaining all documentation and state files (`mentor/STATE.md`, `mentor/ROADMAP.md`, `mentor/BACKLOG.md`, `mentor/DECISIONS.md`, `mentor/LOG.md`, `docs/`, `library/`).
  - Do not wait for or defer to any other agent—`mentor/` is **your** office now.

## 2. How to Orient Yourself in 60 Seconds

Whenever a new session starts in `D:\Repos\lang-gemini-exercise`, read these files in order:

1. **[`mentor/STATE.md`](mentor/STATE.md):** Where the project and teaching currently stand (active stage, build queue, working agreements, and known live code issues). Rewrite (don't append) `STATE.md` as state progresses.
2. **[`mentor/README.md`](mentor/README.md):** The Mentor Charter—how sessions run, how lessons are structured, how changes are built, verified, and reported.
3. **[`mentor/ROADMAP.md`](mentor/ROADMAP.md) & [`mentor/BACKLOG.md`](mentor/BACKLOG.md):** The full curriculum plan (P1–P14, Return Pass R0–R5, D1, Term E) and scheduled/parked engineering items.
4. **Gemini Transition Notes (Local in `docs/gemini/`):**
   - [`docs/gemini/notes.md`](docs/gemini/notes.md): Quick architectural summary.
   - [`docs/gemini/feedbacks/product_ideas_and_refinements.md`](docs/gemini/feedbacks/product_ideas_and_refinements.md): 5 concrete code/design refinements and 10 product expansion ideas identified during the fork review.

## 3. Core Rules & Precedence

- **Repo mechanics, architecture conventions, and commands:** [`AGENTS.md`](AGENTS.md)
- **Engineering & teaching principles:** [`library/governance/principles.md`](library/governance/principles.md)
- **Precedence:** The learner's explicit instruction overrides any document (state a reasoned technical objection first per Principle 1 if an idea has a flaw, then follow the learner's decision and record it).
