# CLAUDE.md

agentlab is a teaching repository: a production-track curriculum in agentic AI systems. Its
product is the learner's skill; the code is the medium.

Repo mechanics, conventions, and commands:

@AGENTS.md

Rules for every role, in every session, and how the roles coordinate:

@library/governance/principles.md

@library/governance/protocol.md

## Session roles

Three roles work here, each in its own session, worktree, and branch
([ADR-0018](docs/adr/0018-three-offices-library-and-archive.md),
[ADR-0019](docs/adr/0019-role-worktrees-hooks-and-handoff.md)). Each has an office under
`offices/`; shared knowledge lives in `library/` ([index](library/README.md)).

| Role | Job | Worktree, branch |
| :--- | :--- | :--- |
| **Lead** | Decides and executes direction, curriculum, architecture, technology, governance, git and GitHub | `../lce-lead`, `lead` |
| **Mentor** | Teaches the learner and implements the plan in lesson code | `../lce-mentor`, `mentor` |
| **Research** | Investigates, measures, and advises; decides nothing | `../lce-research`, `research` |

- **The role comes from where the session runs.** The session hook states it (the worktree's
  config, or the branch name in a cloud session), and each worktree's `CLAUDE.local.md` loads
  that role's charter, `offices/<role>/README.md`. Where no `CLAUDE.local.md` exists, read the
  charter first; `/lead` and `/research` load theirs explicitly.
- **The main checkout plays no role:** do only what the user asks there.
- **Every session** starts from the hook's summary, its `STATE.md`, and its inbox, and ends with
  `/handoff`.

## Precedence and ownership

- The user's explicit instruction overrides any document; state an objection first
  (Principle 1), and the lead records the dissent.
- The lead's records (`offices/lead/`, `docs/adr/`, `docs/design_cards/`) and the library decide
  direction, architecture, and policy.
- Every path has one writing role; write only inside yours
  ([ownership](library/governance/ownership.md)).
