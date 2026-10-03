> Archived 2026-10-03 by lead. The research role was folded into the lead ([ADR-0025](../../../docs/adr/0025-two-roles-lead-and-mentor.md)); the lead's office, [offices/lead/](../../../offices/lead/README.md), carries its work.

# Research Office

The research office holds what this repo **knows and has measured** about the technology it
builds on, and what it **advises** as a result. It records, analyzes, and recommends. It
decides, approves, and sets nothing: the lead reads its reports and decides what is done and
how ([`offices/lead/`](../../offices/lead/README.md)), and the user has the final word. The roles
and how they talk are in [`library/governance/protocol.md`](../../library/governance/protocol.md).

## Sessions

Per [ADR-0019](../../docs/adr/0019-role-worktrees-hooks-and-handoff.md) and LD-011:

- **Where.** Every research session runs in the research worktree, `../lce-research` on branch
  `research`, or in a cloud session on that branch. `/research` moves a session there and loads
  this charter.
- **Start.** Read the session hook's summary. When it says `main` has moved, merge `origin/main`
  into `research` first. Then read [STATE.md](STATE.md) and act on the inbox
  (`python scripts/inbox.py research --fetch`, or `/inbox`).
- **End.** Every session ends with `/handoff`: `STATE.md` updated, replies sent, committed, and
  pushed (`--wip` for unfinished work). When a body of work is ready for `main`, `/handoff --pr`
  opens the pull request, and the lead merges it.
- **Files.** Evidence artifacts go in their record as before. The [sandbox](sandbox/README.md)
  stays on its machine and is never committed.

## Charter

| | |
| :--- | :--- |
| **Role** | Research and advisory. Established 2026-09-26 at the user's request |
| **Writes** | Only inside `offices/research/`. Nothing outside it: not code, not dependencies, not the library, not another role's files. When something belongs elsewhere (a library entry, a line in `CLAUDE.md`, a radar row), a report **proposes** it, with its text, and the owner decides |
| **Hands off** | Anything another role should act on goes to [OUTBOX.md](OUTBOX.md) as a protocol message, never into their files |
| **Others** | Read and link here. They don't edit these files; a correction goes through the outbox or the user |

### What belongs here, and what doesn't

| Belongs here | Stays with its owner |
| :--- | :--- |
| Facts about external technologies (models, gateways, frameworks, packages), with sources and an "as of" date | Decisions and their rationale: ADRs and [DECISIONS.md](../../offices/lead/DECISIONS.md) (lead) |
| Every measurement, spike, benchmark, or live-run result, with its method and raw data where it survives | Plans, roadmap, backlog, risks (lead) |
| Positions and recommendations on open questions, addressed to the lead or the user | Teaching state and stage verification (mentor's office) |
| Maps of which choices in the code rest on which evidence | Runnable eval harnesses and tests (`evals/`, `tests/`; mentor) |

A decision record may *cite* evidence in one line. The evidence itself (setup, numbers,
reading, limits) lives here, under a stable ID the citation links to.

## How it's organized

Content is filed by **how it lives**, because that decides how you can use it:

| Layer | Holds | Lifecycle | Address |
| :--- | :--- | :--- | :--- |
| [`landscape/`](landscape/) | What is true about the outside world: technologies, vendors, packages | **Living.** Edited in place; every page carries an "as of" date and its sources | `landscape/<domain>/<subject>.md`; `README.md` is the domain entry |
| [`evidence/`](evidence/README.md) | What we (or earlier sessions) measured or verified in this repo | **Immutable.** Written once. A correction is a new record that supersedes the old one | `evidence/EV-<YYYY-MM-DD>-<slug>/README.md`, raw data under `artifacts/` |
| [`briefs/`](briefs/README.md) | Our position on one question, and what we recommend | **Revisable.** Updated when evidence changes, with a history table | `briefs/BR-<NNN>-<slug>/README.md`, supporting analysis beside it |

Three files cut across the layers:

- [STATE.md](STATE.md) is **read first** every session: status and agenda.
- [CATALOG.md](CATALOG.md) is **the index**: every record, with its ID, layer, domain, date,
  status, and path. Start here when you look for anything.
- [OUTBOX.md](OUTBOX.md) holds **every message to other roles**, in the protocol's format:
  findings they should know, decisions and relocations only they can make.

[`sandbox/`](sandbox/README.md) is scratch space, never committed; anything worth keeping moves
into a record's `artifacts/`.

## Finding things

| You need | Go to |
| :--- | :--- |
| Anything, by topic or ID | [CATALOG.md](CATALOG.md) |
| What a technology is and how good it is | `landscape/<domain>/` (e.g. [decision models](landscape/decision-models/README.md)) |
| Why the code makes a model choice (a pin, a tier) | [BR-002](briefs/BR-002-model-catalog-evidence-map/README.md), then the evidence it links |
| Proof behind a number cited in an ADR or config | the `EV-...` ID next to the number, or search the catalog |
| What we recommend on an open question | [`briefs/`](briefs/README.md) |

**For agents and code:** paths are stable and IDs never change or get reused. Cite a record
as `offices/research/evidence/<ID>/README.md` or by its bare ID (`EV-2026-09-25-laya-zero-shot`).
Slugs are lowercase kebab-case. Landscape pages are addressed by domain and subject name.

## Evidence labels

Every number carries one label:

| Label | Meaning |
| :--- | :--- |
| **[V]** | Verified here: run in this repo; the record keeps its method and raw data |
| **[R]** | Reconstructed: a result an earlier session recorded in prose; its raw data wasn't preserved and it wasn't re-run |
| **[S]** | Primary source read directly: official docs or the package's own source code |
| **[T]** | Third-party measurement we did not reproduce |
| **[C]** | Vendor claim |

## Rules

- **One fact, one file.** Each fact lives in one record; everything else links to it.
- **The product is the learner's skill, not the software.** This repo grows, on a planned
  curriculum, into a production-level system so that the learner gains the skill to build one.
  Advice is therefore judged at production load, never by what the teaching harness needs today
  (Principle 2, [ADR-0017](../../docs/adr/0017-production-standards-as-design-yardstick.md)):
  - **Efficiency counts as an engineering quality.** Latency, cost, and resource use are
    measured and compared as technical properties.
  - **Product-management reasoning never counts.** Current call volume, user count, "savings too
    small to matter", or ROI never justify skipping a standard or dropping a pattern worth
    learning.
  - **Every reason for or against is admissible:** evidence (unverified, measured worse,
    immature), sequencing (a named later stage), scope (a recorded office decision), or wrong at
    production scale too.
- **Live runs in test mode:** per command, `LLM_TEST_MODE=true`, never by editing `.env`
  (Principle 5).
- **Nothing speculative:** no empty folders or placeholder records. A domain or brief exists
  once it has content.
