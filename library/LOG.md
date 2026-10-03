# Library Log

Append-only: one line per change to the library, newest last. Format:
`YYYY-MM-DD | role | entry | what changed`.

- 2026-09-26 | lead | governance/principles.md | Moved from the lead office (was `docs/office/PRINCIPLES.md`); git ownership and "work to completion" added
- 2026-09-26 | lead | governance/protocol.md | New: offices, outboxes, message grammar, session rhythm
- 2026-09-26 | lead | governance/ownership.md | New: repository map and writers (replaces the office charter's write boundaries)
- 2026-09-26 | lead | governance/glossary.md | New
- 2026-09-26 | lead | engineering/git-policy.md | New
- 2026-09-26 | lead | engineering/dependency-policy.md | Moved from the lead's radar ("Dependency policy") and extended for Dependabot
- 2026-09-26 | lead | engineering/dev-environment.md | New
- 2026-09-27 | lead | engineering/git-policy.md | One worktree and branch per role; pull requests to `main` with merge commits; `/handoff` (ADR-0019)
- 2026-09-27 | lead | engineering/dev-environment.md | Role worktrees, per-worktree `.venv` and `.env`, session hooks, shared auto-memory
- 2026-09-27 | lead | governance/protocol.md | Sessions: identity in files, role from the worktree, hook summary at start, `/handoff` at end
- 2026-09-27 | lead | governance/ownership.md | Map updated for worktrees, `.claude/settings.json`, `CLAUDE.local.md`, the archived and moved docs
- 2026-09-27 | lead | governance/ownership.md | Roles column added; the session guard and the pull-request report read it (ADR-0020)
- 2026-09-27 | lead | engineering/git-policy.md | The lead merges without asking; unmerged branches retire as `archive/<branch>` tags
- 2026-09-27 | lead | engineering/dev-environment.md | Prompt hook, ownership guard, worktree routing, `/inbox` and `/loop`, the Messages workflow
- 2026-09-27 | lead | governance/protocol.md | Receiving: hooks announce messages; `inbox.py` defaults to the worktree's role
- 2026-09-28 | lead | architecture/decision-models.md | New: the rule for AI decision points and the one standard (ADR-0021); research's landscape keeps the facts
- 2026-09-28 | lead | governance/protocol.md | A fourth role, the engineer (`EN-###`), in the parties, routing, and sessions tables (ADR-0022)
- 2026-09-28 | lead | governance/ownership.md | Code, tests, evals, tooling, CI, hooks, and dependencies move to the engineer (ADR-0022)
- 2026-09-28 | lead | governance/principles.md | Principle 12: reports open with the bottom line (DEC-027)
- 2026-09-28 | lead | engineering/git-policy.md | The engineer's worktree; CI implemented by the engineer; exercise states restored with git
- 2026-09-28 | lead | engineering/dev-environment.md | The engineer's worktree
- 2026-09-28 | lead | README.md | The lead alone writes and curates the library; five categories (ADR-0024)
- 2026-09-28 | lead | architecture/standards.md | Moved in from the lead's ARCHITECTURE.md: principles, scale seams, composition patterns
- 2026-09-28 | lead | architecture/decision-models.md | Moved from engineering/
- 2026-09-28 | lead | technology/radar.md | Moved in from the lead's TECH_RADAR.md
- 2026-09-28 | lead | technology/models.md | New: the LLM tiers, the deciders, what is measured, how tiers will be chosen
- 2026-09-28 | lead | teaching/pedagogy.md | Moved in from the lead's PEDAGOGY.md; active review replaces typing (ADR-0023)
- 2026-09-28 | lead | governance/glossary.md | Engineer, active review, decision point, decider, cascade and fallback
- 2026-09-28 | lead | engineering/git-policy.md | No exercise states; code reaches main only through the engineer
- 2026-10-03 | lead | governance/protocol.md | Two roles, lead and mentor; the engineer and research retired; messages LD and MN only (ADR-0025)
- 2026-10-03 | lead | governance/ownership.md | Every path is the lead's except the mentor's; the research record is `offices/lead/research/`
- 2026-10-03 | lead | governance/glossary.md | Engineer and Research removed; Lead widened; Research record
- 2026-10-03 | lead | engineering/git-policy.md, engineering/dev-environment.md | Two worktrees; a retired role's branch may be deleted once `main` holds it
- 2026-10-03 | lead | teaching/pedagogy.md, architecture/decision-models.md, technology/*.md, engineering/dependency-policy.md | Engineer and research references now the lead; research links to `offices/lead/research/`
