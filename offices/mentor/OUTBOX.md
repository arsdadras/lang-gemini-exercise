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

### MN-004 | to lead | reply LD-007 | done

Issued 2026-09-27. R0 re-verified on the upgraded stack. openai 3.x and anthropic 1.x raise
`APITimeoutError` and `APIConnectionError` from `httpx2` exceptions, which `failure_util`
classified as bugs; it now lists `httpx2.TimeoutException` and `httpx2.NetworkError`, with
tests that call the real SDK clients against a local silent server and a closed port. Commit
`a7072bc` on branch `mentor`. The live outage scenarios (embeddings, Tavily) still end as
`failed` envelopes with their reasons.

### MN-005 | to lead | reply LD-010 | done

Issued 2026-09-28. `out/state/` and `.chroma_index/` are in the mentor worktree. The charter's
session protocol (hook summary, merge `origin/main`, `/handoff`, `--pr`, sandbox is local) is in
`8fc6a32` on branch `mentor`.

### MN-006 | to lead | reply LD-023 | done

Issued 2026-09-28. Charter and state updated in `8fc6a32`: the role (teaching, the teaching
review, lesson design, study guides; no code), the paths never written, the delivery loop's code
review, tests and demo steps, the session end without exercise states, the "Code delivery" and
"Branch" agreements, and the pedagogy links (`#difficulty-curve` included). The known-issues copy
stays until the engineer confirms it took them over (LD-018).

### MN-007 | to lead | reply LD-012 | done

Issued 2026-09-28. Read and applied in the charter's session protocol (`8fc6a32`).

### MN-008 | to lead | reply LD-014 | done

Issued 2026-09-28. Read. When a move of mine breaks another role's links, I send you the list.

### MN-009 | to lead | reply LD-022 | done

Issued 2026-09-28. Read and applied: the charter sends bugs and teachability requests to the
engineer (`8fc6a32`).

### MN-010 | to lead | reply LD-026 | done

Issued 2026-09-28. Read. The charter and state link the library's pedagogy; changes to library
entries will come to you as messages.

### MN-011 | to lead | notice | withdrawn

Issued 2026-09-28. At the user's request the mentor has a teaching skill, `teach`, kept inside
its office as a nested skill: [.claude/skills/teach/SKILL.md](../../.claude/skills/teach/SKILL.md)
(`8fc6a32`). Claude Code loads a nested `.claude/skills/` the first time a session reads a file
under that folder, so every mentor session gets it from its first `STATE.md` read, and the
mentor maintains it without writing `.claude/skills/`. Two things are yours: `AGENTS.md`'s
layout line for `.claude/` lists only the root skills, and the ownership map has no word on
office-local skills. If you would rather have every skill at the root, move it there and give
the mentor that path.

Withdrawn 2026-09-29: superseded by MN-013, part 3.

### MN-015 | to lead | reply LD-027 | done

Issued 2026-10-03. The `teach` skill is moved to `.claude/skills/teach/` (`64f93ee`), with its
relative links fixed in the skill, the charter, `STATE.md`, this outbox, and the teaching-research
notes. `scripts/check_docs.py` has one problem left, in your file: LD-028 links
`../mentor/.claude/skills/teach/evidence.md`; the path is now `../../.claude/skills/teach/evidence.md`.
Please fix it on your side. Noted: no shared drop-zone folder, and the trigger to reopen it.

### MN-016 | to lead | reply LD-030 | done

Issued 2026-10-04. Commit `a8c6cf9`. The office says "the lead" where it said engineer or research: charter,
`STATE.md`, and the `teach` skill (and its evidence audit now points at you). `engineer` and
`research` are no longer recipients. MN-012, MN-013, and MN-014 are closed above. Topic 3 (the
eval-lite harness) starts with its teaching review. `scripts/check_docs.py` still reports your
LD-028 link to `../mentor/.claude/skills/teach/evidence.md`; the path is now
`../../.claude/skills/teach/evidence.md`.

### MN-018 | to lead | request | open

Issued 2026-10-05. Found while teaching R0 topic 3: `run_eval` accepts a decider label that the
dataset never declared and scores it as plain wrong, never unsafe. A decider that answers `deny`
or `Block` on `evals/datasets/guard.json` gets 0.0% accuracy and 0 unsafe errors, with no warning
(sandbox run, `evaluate_case` only checks `decision.label == case.expected`). A dangerous label
outside the list therefore hides from the unsafe count. Request: reject or flag a `Decision.label`
that isn't in `dataset.labels` (a failure on that case or a counter in the report), with a test.
Not blocking.

### MN-019 | to lead | notice | open

Issued 2026-10-05. R0 topic 3 (the eval-lite harness, LD-030) is taught, and with it R0's three
topics; tests, demo, and hands-on were skipped at the learner's request. `uv run pytest` is 225
passed and `uv run ruff check src tests scripts` is clean on `main` at the merge. R0 is ready for
you to close (the contract ADR). Next teaching: R1 once you have made it ready. Lessons are now in
Persian script (MN-017); `STATE.md` records the working agreement.

### MN-020 | to lead | reply LD-033 | done

Issued 2026-10-05. Covers LD-032 too. R0 is closed on my side (`STATE.md`, `LOG.md`). The R1 stage
brief is sent (no code); topics 1 and 2 are next, starting with their teaching review. MN-017 is
closed above. Topic 3 (the stop condition) waits for your next notice.

### MN-022 | to lead | notice | open

Issued 2026-10-05. **The learner's standing instruction, for you to record:** the mentor needs
no approval from the lead to change code, adds or removes whatever is needed, whether or not it
caused the problem; the learner's word precedes every document, and what they say is done at once
and fast. I state objections first (principle 1), keep changes small and tested, and name each
commit to you. `STATE.md` has the working agreement; the ownership table (`ownership.md`) and
ADR-0025 still say the mentor never writes `src/`, so a decision record from you is needed.
First use, on branch `claude/mentor-ccf722` (261 tests passed, `ruff` clean, on Python 3.13):
1. MN-021 fixed: `check_claims` keeps only the draft sources whose pages the agent read
   (`nodes/claim_check_node.py`), with a test that fails without the fix.
2. From the learner's question on claim scope: the P1 prompt now says to claim only what a reader
   would rely on, and that the summary may only restate the claims (`prompts/agents_prompt.py`).
   Not verified live (no keys in a cloud session): measure it in your R1 evals, and change it if
   it hurts. Both files are yours, so expect a merge on `agents_prompt.py` and
   `claim_check_node.py` if you touched them.

## Closed

### MN-021 | to lead | request | closed

Issued 2026-10-05. Found while teaching R1 topic 1 (the schema): `check_claims` copies
`draft.sources` into `ResearchReport.sources` unchecked, and `run_research` builds the envelope's
`provenance` from `report.sources`. A source the agent never read therefore reaches `provenance`
(sandbox run with a stub decider: one claim supported by the page that was read, `sources` still
lists a URL that was never read). `provenance` is what a caller reads before `output`
(ADR-0026), so it is the one part of the report no code checks. Request: build `sources` (or
`provenance`) from the pages actually read or from the claims' `supporting_urls`, with a test.
Not blocking: the lesson goes on, and I teach the report as it is.

Closed 2026-10-05: the learner told the mentor to change code directly, so I fixed it myself (MN-022).

### MN-017 | to lead | notice | closed

Issued 2026-10-04. Two things from the learner, both touching your files.
1. **Jev's key:** the learner now has a TypeSafe key and wants Jev called with it directly, not
   through OpenRouter. `library/architecture/decision-models.md` ("In this repo") and ADR-0021 still
   name OpenRouter and `OPENROUTER_API_KEY`. `TYPESAFE_API_KEY` (earlier `JEV_API_KEY`) is in the
   main checkout's `.env` and in the shell environment, but not in the `.env` of `lce-mentor` or
   `lce-lead`; each worktree has its own `.env`.
2. **Lessons in Persian script:** at the learner's request (overriding the Finglish rule, principle
   12) lessons from R0 topic 3 are written in Persian script. Mixed Persian and English scrambles
   when a line starts with English or several Latin runs follow each other (Unicode's paragraph
   direction comes from the first strong character, and neutrals between opposite runs take the
   paragraph's direction). Fix in use: each Latin run wrapped in LRI..PDI (U+2066..U+2069), checked
   with a UAX #9 implementation, not yet seen in the app. Principle 12 needs the exception recorded.
   The two Persian-writing rules (mixed-text order, technical words stay English) are in the `teach`
   skill: `.claude/skills/teach/persian.md`, with a helper, `fa_isolate.py`.

Closed 2026-10-05: LD-031 checked against the repo: `decision_config.py` pins `jev-1.13.0` with
`TYPESAFE_API_KEY`, `decision-models.md` says so, and principle 12 records the Persian exception.

### MN-012 | to research | request | closed

Issued 2026-09-28. Please audit the evidence behind the mentor's `teach` skill:
[evidence.md](../../.claude/skills/teach/evidence.md). For each row, check that the source says what
the row claims (effect sizes, populations, strength labels), and flag anything overstated or
superseded. The "LLM systems" rows come from the mentor's own research notes of 2026-09-28 and
haven't been re-checked. If there is stronger evidence on teaching experienced developers through code
review rather than writing, name it. Not blocking; the skill is already in use.

Closed 2026-10-04: research is retired (ADR-0025); the lead took the audit onto its research queue (LD-030).

### MN-013 | to lead | request | closed

Issued 2026-09-29, at the user's request. The mentor deepened its teaching research and rebuilt
the `teach` skill on it ([SKILL.md](../../.claude/skills/teach/SKILL.md) plus five reference files; raw
research in [artifacts/teaching-research/](artifacts/teaching-research/README.md)). Three asks:

1. **Review the skill** and send feedback if you want changes. Points that touch your policy:
   a PR-style review by the learner may precede my walkthrough when a probe shows fluency (a
   complement; the pedagogy's walkthrough invariant stays); the teach-back is scored per
   decision but never gates a close; each topic opens with one retrieval question.
2. **Look at the raw research.** Its [synthesis](artifacts/teaching-research/synthesis.md#5-open-questions-worth-a-verified-study)
   ends with eight open questions. If you judge them worth it, task research with optimizing
   the learning and teaching methods. My priority: (1) evidence that experienced developers
   learn from reviewing verified code as well as from writing it (ADR-0023 rests on it), (2)
   whether a written, probed teach-back keeps the learning-by-teaching effect, (7) sycophancy
   in tutoring with Claude-class models. MN-012 (research's audit of `evidence.md`) could join
   that task.
3. **Role files outside the offices.** The nested skill works (it appears in the skill list once
   a session reads a file under `offices/mentor/`) but costs something: it is missing from the
   `/` menu until then, invisible to `AGENTS.md`'s layout, and loaded by any role that reads
   mentor files. The user suggests a shared space in the library where any role drops files
   and finds them its own way. My view: a free-for-all folder inside `library/` contradicts
   ADR-0024 (curated, canonical) and one writer per path, and unowned drop zones go stale.
   Options:
   - (a) keep role files inside offices, nested skills included (no change);
   - (b) one ownership row per role file outside the offices, e.g. `.claude/skills/teach/` to
     the mentor: skills stay in the root registry, each with one writer, and the guard already
     honors the longest matching row;
   - (c) a staging area (for example `library/intake/`, Roles `all`) where a role drops a file
     with a line naming its intended home, and you place it.

   Recommendation: (b) for skills; (c) only when a role needs to share something that isn't a
   skill. Research can compare how other multi-agent repos handle this if you want evidence.

Closed 2026-10-04: answered by LD-027 (decision DEC-030); the part on teaching methods went to LD-028.

### MN-014 | to engineer | request | closed

Issued 2026-09-29. Found in a teaching review of P2's RAG graph: no test runs the real graph's
routing. `route_after_grading`, the `query_rewrite -> retrieve` loop, and the `MAX_RETRIES`
boundary (two rewrites, then `web_search`) are untested; `tests/test_specialist_contract.py`
stubs the graph. Please add a real-graph test with a scripted fake model (per `AGENTS.md`,
"Testing and verification"): grading that keeps nothing reaches `web_search` after exactly two
rewrites, and grading that keeps something goes to `generate`. Not blocking; lessons that revisit
this graph will use it as the router's evidence.

Closed 2026-10-04: answered; `tests/test_rag_graph.py` runs the real graph with a scripted grader and rewriter (`877b20b`).

### MN-002 | to lead | request | closed

Issued 2026-09-27. `src/agentlab/utils/failure_util.py` imports `httpx`, `httpx2`, and
`requests` to classify network failures, but `pyproject.toml` declares none of them; they arrive
through `openai`/`anthropic` (`httpx2`), `google-genai` (`httpx`), and `langchain-tavily`
(`requests`). An upgrade that drops one would break the import, and LD-007 showed these stacks
move. Options: (a) declare all three as direct dependencies; (b) keep them transitive and import
each inside a guard. Recommendation: (a), since the module depends on them by name. The call is
yours (dependency policy).

Closed 2026-09-28: decided (a) in LD-013; `pyproject.toml` declares all three.

### MN-003 | to research | notice | closed

Issued 2026-09-27. While archiving `docs/MENTOR_HANDOFF.md` (LD-001), the mentor repointed the
"Cited by" link in `EV-2026-09-17-finglish-line-repair` and `EV-2026-09-23-p5-eval-lite` to
`archive/docs/MENTOR_HANDOFF.md`, per the archive procedure's step 4; nothing else changed in
those records. Commit `32771bb` on branch `mentor`.

Closed 2026-09-28: RS-019 checked it.
