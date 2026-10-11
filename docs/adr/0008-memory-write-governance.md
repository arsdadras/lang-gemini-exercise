# ADR-0008: Memory writes are governed by operation in code, content later by a guard

- Status: Accepted; enforcement superseded by [ADR-0010](0010-one-gate-in-memory-storage.md)
  (the rules moved from `interrupt_on` into the memory storage, which also judges content)
- Date: 2026-09-14

## Context

- **Memory was written without review.** The P5 prompt told the model to persist anything it
  heard, and nothing checked a write before it landed in `/memories/`.
- **Skills were writable and shared.** `/skills/` is backed by the packaged files on disk and
  read by every user's conversations, so one edited `SKILL.md` would change behavior for all.
- **The built-ins already cover path-aware approval.** `HumanInTheLoopMiddleware` accepts a
  per-tool `when` predicate, and DeepAgents compiles `FilesystemPermission(mode="interrupt")`
  into those predicates. Roadmap v3's plan for a custom `wrap_tool_call` middleware was stale.
- **Approving every write is unusable.** The assistant saves facts in passing; asking each time
  (or batching approvals for a session end the app can't detect) was rejected by the mentee.
- **The streamed CLI dropped interrupts.** `stream_agent_with_observability` skipped the
  `__interrupt__` chunk, so a paused run ended silently.

## Decision

- **Classify by operation, in code.** HITL `when` predicates decide from the tool call itself
  (`middlewares/memory_approval_middleware.py`). A new memory file, or an edit that keeps every
  old line, runs freely. Overwriting a stored file, an edit that drops text, or deleting under
  `/memories/` waits for approval. Paths are normalized with DeepAgents' `validate_path`, and
  an unknown file state fails closed.
- **Pass it as `interrupt_on`, not as a middleware.** DeepAgents applies `interrupt_on` to its
  general-purpose subagent too, so a delegated write can't skip the gate.
- **Skills are read-only for the assistant** (`FilesystemPermission` deny on `/skills/**`).
- **Content is judged later, by a separate classifier.** Whether a write is sensitive is B3's
  security guard: a single structured-output model call behind a generic `(action, policy) ->
  verdict` interface, run after the code layer, failing closed to a human. Until it exists,
  `memory-curation` tells the model to skip sensitive facts unless asked.
- **One writer for skills.** A `skill_designer` specialist (C3) is the only writer; publishing
  to the shared library is draft, guard, then human approval.
- **Streamed approvals.** `stream_with_hitl` reads pending interrupts from the checkpoint (a
  subagent's interrupt streams once per namespace), answers each by interrupt id, and re-sends
  runtime context on every resume.
- **Skills teach the procedure, code enforces the rule.** `memory-curation` shapes writes to be
  additive; `goal-plan` stores only a plan skeleton with an append-only progress log, so
  everyday progress never needs approval.

## Consequences

- An additive edit can still change meaning (a line appended that negates an earlier one);
  only the B3 guard can catch that.
- After a rejection the agent can reach the same result through other tool calls; each step is
  gated, but the behavior is measured in C2.
- Sensitive facts are not remembered until B3, even when useful.
- `SkillsMiddleware` caches the skill list per thread, so skill changes reach new threads only
  (relevant to C3).

## Alternatives considered

- **`FilesystemPermission(mode="interrupt")` on all of `/memories/**`:** rejected, it asks on
  every save.
- **Approval only when overwriting the profile:** rejected, a single edit can erase as much.
- **Prompt-only ("ask before saving"):** rejected, no guarantee.
- **The model classifying its own writes:** rejected as the gate, the actor would judge itself;
  kept as guidance inside the skill.
- **The guard as a full agent with tools and skills** (mentee's proposal): deferred, not
  rejected. It starts as a classifier with a generic interface and grows into an agent when a
  consumer needs tools (triggers in the handoff backlog: P7, P8, P11).
- **`run_with_hitl` for the P5 app:** rejected, it loses live progress.
- **Resuming with a timestamp-ordered list instead of ids:** not available; LangGraph refuses an
  unkeyed resume while several interrupts are pending, and ids survive node re-execution.
