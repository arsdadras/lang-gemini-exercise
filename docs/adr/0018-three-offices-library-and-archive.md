# ADR-0018: Three offices, a shared library, an archive, and one message protocol

- Status: Accepted. Amends [ADR-0016](0016-project-office-and-document-governance.md); its shared
  working tree is replaced by one worktree per role ([ADR-0019](0019-role-worktrees-hooks-and-handoff.md)).
- Date: 2026-09-26
- Origin: user direction; design by the lead
- Revisit when: a fourth role appears, or messages start being lost between offices

## Context

- **A third role arrived.** A research session (investigation, measurement, evidence) started
  work on 2026-09-26 under `docs/research/`, with its own outbox and record types. ADR-0016's
  interface had two parties and two files; it had no place for a third.
- **The interface was asymmetric.** The office wrote directives in its own file, the mentor
  answered inside its handoff. Every new role would add another bespoke channel.
- **Shared knowledge had no home.** Principles, the ownership map, and policies lived in the
  office's directory, so other roles read "the office's" copy of rules that bind everyone.
- **Nothing was ever retired cleanly.** Superseded documents (roadmap v3, the old mentor
  contract) either stayed in place, contradicting their replacements, or would be deleted and
  lose their inbound links.
- **Git had no owner.** Commits waited for the user's word, and four commits sat unpushed on one
  machine.
- **"Office" named a place, not a role.** With three offices, the deciding role needed its own
  name.

## Decision

- **Three roles, three offices** under `offices/`: `lead` (decides and executes; formerly "the
  office"), `mentor` (teaches and implements), `research` (investigates and advises; decides
  nothing). Each office has a charter (`README.md`), `STATE.md`, `OUTBOX.md`, `artifacts/`, and
  an ignored `sandbox/`.
- **One message protocol** ([protocol.md](../../library/governance/protocol.md)): every message
  lives only in its sender's outbox, under a one-line heading
  `ID | to <role> | <type> | <status>`; `scripts/inbox.py <role>` lists what a role must act
  on; replies go in the replier's own outbox; the sender closes.
- **A shared, text-only library** (`library/`) holds canonical knowledge every role relies on,
  maintained as an LLM-maintained wiki: front matter, an index, an append-only log, and a lint
  (`scripts/check_docs.py`). Knowledge moves in; it is never copied.
- **A frozen archive** (`archive/`): the owner of a retired document `git mv`s it under its
  original path with a one-line banner and an index row.
- **Git and GitHub belong to the lead** ([git policy](../../library/engineering/git-policy.md)):
  every role commits its own paths and pushes at session end; CI and Dependabot guard `main`.
- **`CLAUDE.md` routes three roles:** it loads `AGENTS.md`, the principles, the protocol, and the
  mentor's charter (the default role); `/lead` and `/research` open the other roles.
- **Bootstrap.** The lead seeds the mentor office from the mentor's documents; the mentor adopts
  it, archives its old files, and owns it from then on (LD-001). Research moves its own office
  (LD-002). Until both land, the offices and the library win any disagreement.

## Consequences

- One mechanism serves every pair of roles; adding a role adds an office, not a channel.
- A session starts by reading one state file and one inbox command, whatever its role.
- Every shared rule has one file and one maintainer; stale links fail CI instead of rotting.
- Old documents keep resolving, frozen, with a pointer to what replaced them.
- The lead now carries git hygiene: a red `main`, an unmerged branch, or a pending Dependabot
  update is its work.
- Until LD-001 and LD-002 are applied, some facts exist twice (the old mentor contract and the
  seeded charter); the precedence line in `CLAUDE.md` settles conflicts.

## Alternatives considered

- **Keep ADR-0016's two files and add a third for research:** rejected; three bespoke channels,
  each read differently, and still no way to list what a role owes.
- **A shared message board (one file every role writes):** rejected; it breaks one writer per
  path and invites lost updates between concurrent sessions.
- **GitHub issues as the message bus:** rejected for now; messages must be readable offline and
  in every session without API access, and must version with the repo. Revisit if the offices
  outgrow text files.
- **Copy shared rules into each office:** rejected; copies drift (the migration's own risk,
  RSK-03).
- **Delete retired documents:** rejected; history keeps the text, but inbound links and readers
  looking for them lose it.
