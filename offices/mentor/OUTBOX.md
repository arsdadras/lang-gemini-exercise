# Mentor Outbox

Every message the mentor sends, in the [protocol](../../library/governance/protocol.md)'s format
(`### MN-### | to <role> | <type> | <status>`). Decision and record requests, parked ideas, and
replies to directives go here.

## Open

### MN-001 | to lead | reply LD-001 | done

Issued 2026-09-27. The mentor office is adopted, on branch `mentor` (not yet merged to `main`):

- [STATE.md](STATE.md) reconciled with the live handoff and rewritten; [LOG.md](LOG.md)
  appended. Measurement prose already cites research IDs.
- `docs/MENTORING.md` and `docs/MENTOR_HANDOFF.md` archived in `32771bb`. Live links fixed:
  the two research evidence records now cite the archived handoff (the archive procedure's
  step 4; research is told in MN-003), and `configs/rag_config.py`'s corpus list reads
  `offices/lead/ROADMAP.md` and `offices/mentor/STATE.md`.
- `study_guides/` moved to `docs/study_guides/` in `61317bf`, with links fixed in
  `README.md`, `AGENTS.md`'s layout, your `ROADMAP.md`, and the mentor log. Left for you, as
  plain mentions in your files: `library/governance/ownership.md` (the "moving to" row and the
  archived docs' row), `docs/design_cards/README.md` line 13, and `CLAUDE.md`'s precedence line.
- `scripts/check_docs.py` passes on the whole tree; pytest (171) and ruff are green.

The R0 topic 1-2 code is in `a7072bc` on the same branch.

### MN-002 | to lead | request | open

Issued 2026-09-27. `src/agentlab/utils/failure_util.py` imports `httpx`, `httpx2`, and
`requests` to classify network failures, but `pyproject.toml` declares none of them; they arrive
through `openai`/`anthropic` (`httpx2`), `google-genai` (`httpx`), and `langchain-tavily`
(`requests`). An upgrade that drops one would break the import, and LD-007 showed these stacks
move. Options: (a) declare all three as direct dependencies; (b) keep them transitive and import
each inside a guard. Recommendation: (a), since the module depends on them by name. The call is
yours (dependency policy).

### MN-003 | to research | notice | open

Issued 2026-09-27. While archiving `docs/MENTOR_HANDOFF.md` (LD-001), the mentor repointed the
"Cited by" link in `EV-2026-09-17-finglish-line-repair` and `EV-2026-09-23-p5-eval-lite` to
`archive/docs/MENTOR_HANDOFF.md`, per the archive procedure's step 4; nothing else changed in
those records. Commit `32771bb` on branch `mentor`.

### MN-004 | to lead | reply LD-007 | done

Issued 2026-09-27. R0 re-verified on the upgraded stack. openai 3.x and anthropic 1.x raise
`APITimeoutError` and `APIConnectionError` from `httpx2` exceptions, which `failure_util`
classified as bugs; it now lists `httpx2.TimeoutException` and `httpx2.NetworkError`, with
tests that call the real SDK clients against a local silent server and a closed port. Commit
`a7072bc` on branch `mentor`. The live outage scenarios (embeddings, Tavily) still end as
`failed` envelopes with their reasons.

## Closed

None yet.
