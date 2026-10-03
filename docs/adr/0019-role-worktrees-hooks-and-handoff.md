# ADR-0019: One worktree and branch per role, session hooks, and a /handoff skill

- Status: Accepted; the roles are now two, the lead and the mentor ([ADR-0025](0025-two-roles-lead-and-mentor.md))
- Date: 2026-09-27
- Origin: user direction (2026-09-27); design by the lead. Replaces the shared working tree of
  the git policy that [ADR-0018](0018-three-offices-library-and-archive.md) set up; the offices,
  the library, and one writer per path stay as they are.
- Revisit when: the setup has run for a week without coordination trouble (then decide on
  automatic message awareness, backlog item e).

## Context

- **One working tree, three sessions.** The lead, the mentor, and research all worked in the
  same checkout. On 2026-09-23 a concurrent session's half-done rename left 13 tests failing; on
  2026-09-27 the lead had to save, re-apply, and hand-resolve the mentor's uncommitted
  `AGENTS.md` hunk before it could pull; commits needed hunk-level staging to avoid carrying
  another role's work.
- **One `.venv` for everything.** A recreate on 2026-09-26 failed halfway because the IDE's ruff
  server held an executable, and left the environment broken for every role.
- **Local and cloud drifted.** A cloud lead session and local sessions diverged on shared files
  (RSK-11), and the switch needed a hand-written handoff.
- **Long sessions lose their footing.** A session compacted again and again keeps less of its
  own context than a fresh one that reads its office's state.

## Decision

- **One worktree and one long-lived branch per role:** `../lce-lead` on `lead`,
  `../lce-mentor` on `mentor`, `../lce-research` on `research`, each with its own `.venv`,
  `.env` copy, and runtime data. The main checkout stays on a clean `main` for the user and
  runs no role session. `scripts/setup_worktrees.py` creates or completes them.
- **Every change reaches `main` by pull request;** CI gates it and the lead merges, its own
  included. Role branches merge with a **merge commit**, not a squash: SHAs that office records
  cite stay valid on `main`, and the role branch never diverges from it. Each session starts by
  merging `origin/main` into its branch when `main` has moved.
- **Identity lives in files, not sessions.** The role comes from the worktree's own git config
  (`agentlab.role`), or from the branch name in a cloud session. Each worktree's ignored
  `CLAUDE.local.md` loads its role's charter, so `CLAUDE.md` no longer loads the mentor's
  charter into every session. Sessions are short and rebuild their context from `STATE.md` and
  the inbox.
- **Session hooks** in `.claude/settings.json` run `scripts/session_hooks.py` (standard library
  only; always exit 0): SessionStart adds the role, what the branch lacks from `main`, unpushed
  work, `git status`, the head of `STATE.md`, and the inbox to the session's context; Stop shows
  one non-blocking warning about uncommitted or unpushed work.
- **`/handoff`** ends a session: the model updates `STATE.md` and replies, then
  `scripts/handoff.py` commits the worktree (as `wip(<role>): ...` when unfinished), pushes the
  branch, optionally opens the pull request, and prints three lines.
- **The inbox reads every role's branch** (`origin/<role>`) as well as `main`, so a message is
  seen before its pull request merges.

## Consequences

- Concurrent sessions can no longer overwrite, stage, or break each other's work; a red branch
  stays on its branch.
- Moving between machines or into the cloud is a push and a pull.
- Three environments and three copies of `.env` on the machine; runtime data (checkpoints, the
  P5 store, the vector index) is per worktree, and the mentor's moves over once.
- `main` sees merge commits and, sometimes, `wip` commits in its history.
- A change is on `main` only after the lead merges it; until then other roles read it from the
  role's branch (the inbox does this for messages).
- GitHub Free can't protect a private repo's branch (the API answers 403), so "only by pull
  request" is policy, not enforcement; CI still runs on every push.
- Project hooks run a fetch at every session start and need the user to trust the project's
  hooks once.

## Alternatives considered

- **Keep the shared tree with path-limited commits:** rejected; it is what failed three times
  in four days.
- **Short-lived topic branches per task, squash-merged:** a cleaner history, but every task needs
  a new branch, messages must be found across many branches, and squashing rewrites the SHAs the
  offices cite.
- **Squash-merge the long-lived role branches** (the direction's first form): rejected for the
  same SHA reason, and because each squash leaves the role branch diverged until it merges
  `main` back.
- **Role from the directory name:** rejected as fragile; the worktree's git config survives a
  rename and is explicit.
- **`CLAUDE.md` importing every charter:** rejected; each session would carry two charters that
  don't apply to it.
