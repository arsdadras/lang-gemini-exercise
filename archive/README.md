# Archive

Retired documents, kept frozen so old links, commits, and records still resolve to something.
Nothing here is current: the banner on each file names what replaced it. Nobody edits an
archived file after it arrives.

## Procedure

Only the retiring file's owner archives it ([ownership.md](../library/governance/ownership.md)).

1. `git mv <path> archive/<path>`, keeping the original path under `archive/`.
2. Add one line at the top of the file:
   `> Archived <YYYY-MM-DD> by <role>. Superseded by <link to the replacement>.`
3. Add a row to the index below.
4. Fix live links to the old path so they point at the replacement (links from ADRs and other
   historical records may point at the archived copy instead).
5. Commit the move on its own: `docs(<role>): archive <path>`.

## Index

| Archived path | Date | By | Superseded by |
| :--- | :--- | :--- | :--- |
| [docs/MENTORING.md](docs/MENTORING.md) | 2026-09-27 | mentor | [offices/mentor/README.md](../offices/mentor/README.md) and [library/governance/](../library/governance/principles.md) |
| [docs/MENTOR_HANDOFF.md](docs/MENTOR_HANDOFF.md) | 2026-09-27 | mentor | [offices/mentor/STATE.md](../offices/mentor/STATE.md) and [LOG.md](../offices/mentor/LOG.md) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 2026-09-27 | lead | [offices/lead/ROADMAP.md](../offices/lead/ROADMAP.md) |
| [HANDOFF_LOCAL.md](HANDOFF_LOCAL.md) | 2026-09-27 | lead | [offices/lead/STATE.md](../offices/lead/STATE.md); the snapshot branch is the tag `archive/handoff-local-snapshot` |
