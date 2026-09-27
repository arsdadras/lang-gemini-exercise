# ADR-0020: An ownership guard, worktree routing, and automatic message awareness

- Status: Accepted
- Date: 2026-09-27
- Origin: user direction (2026-09-27): make wrong-worktree sessions harmless even when nobody
  checks, and build the rest of the coordination features; design by the lead. Builds on
  [ADR-0019](0019-role-worktrees-hooks-and-handoff.md).
- Revisit when: an edit made through a shell command slips past the guard, or research's
  upstream-watch procedure exists (then schedule its routine).

## Context

- **Worktrees only help if sessions open in the right one.** ADR-0019 gave each role its own
  worktree, but nothing stopped a session from starting in the main checkout or in another role's
  worktree and editing there. The user asked for a safeguard that works even when they forget to
  check.
- **Ownership lived only in prose.** `library/governance/ownership.md` said who writes what, and
  only people and models read it. Twice a role edited another's files (link repairs after its own
  move); both times it was benign, and neither was caught by anything.
- **Awareness stopped at session start.** The SessionStart hook shows the inbox once. A message
  sent while a session runs, or merged while nobody looks at GitHub, waits for the next session.

## Decision

- **The ownership map is machine-read.** Its table gains a **Roles** column (role names, `all`,
  `none`; the longest matching path wins; unlisted paths belong to the lead). `scripts/workspace.py`
  parses it, so the map stays the one place ownership is written.
- **An ownership guard** (PreToolUse on `Edit`, `Write`, `MultiEdit`, `NotebookEdit`) denies an
  edit when the session's checkout plays no role, when the file is in another checkout, or when
  the Roles column doesn't list the session's role. Paths outside the repository pass. The
  denial names the owner and the way out. `AGENTLAB_GUARD=off` in the environment turns it off for
  one session, a switch only the user can set.
- **Routing instead of relying on memory.** A session outside the role worktrees is told, at
  start and in every denial, to move itself: the desktop app's `change_directory` tool takes the
  session to the right worktree, and in a terminal the user starts `claude` there. `/lead`,
  `/mentor`, and `/research` do the same when opened in the wrong place.
- **Awareness during a session:** a UserPromptSubmit hook adds any message that arrived since
  the session last heard (it fetches at most every five minutes and announces each message once).
  `/inbox` shows the inbox on demand, so a long session can run `/loop 15m /inbox`.
- **Awareness on GitHub:** a `Messages` workflow writes a job summary: on each pull request, the
  messages it adds or changes and any file outside its branch's role (also as warnings); on each
  push to `main`, the open messages waiting for each role. It reports and never fails a run.
- **The scheduled cloud routine for research's upstream watch waits** for its procedure
  (sequencing): research hasn't defined the watch (LD-003), and an unattended weekly agent
  without a procedure writes whatever it guesses. The lead creates the routine as soon as
  research defines the procedure.

## Consequences

- A session in the wrong place can read but can't change anything in the repository, and it is
  told where to go.
- A cross-role link repair is no longer possible by hand; the mover asks the lead, which fixes
  the links when it merges.
- The guard doesn't see shell commands: an edit made through `Bash` passes, and the pull-request
  report is the net behind it.
- Every prompt in a role session runs a short hook, with a fetch at most every five minutes.
- `library/governance/ownership.md` must keep its table shape; a test parses the real file.

## Alternatives considered

- **Block every tool, Bash included, in the main checkout:** rejected; read-only shell commands
  (status, logs, tests) are how a misplaced session finds out where it is.
- **A CI check that fails on out-of-role files:** rejected as the enforcement point; the lead
  legitimately merges one role's work together with the link repairs it needs, and a failing
  check would block that. The local guard prevents, the report shows the rest.
- **A separate machine-readable ownership file:** rejected; two copies of one map drift.
- **Only `/loop` for awareness:** kept as an option, not the default; the prompt hook costs
  nothing when there is no news and needs no one to remember to start it.
- **Create the research routine now:** rejected for the sequencing reason above.
