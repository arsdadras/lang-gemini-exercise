# ADR-0013: Finishing P5: history and undo, durable memory, governed skills, and a context provider

- Status: Accepted
- Date: 2026-09-23

## Context

- **The return pass needs P5 complete.** The mentee asked the mentor to finish P5's remaining
  stages directly, so R0 can design the specialist contract over five specialists instead of
  four. P5 is taught again from B4 later, after R4, because R0-R4 may change parts it depends
  on (approvals, for one).
- **Open B4 items** (ADR-0012 consequences): approving a correction the user just asked for is
  friction; a rejected edit came back after every conversation; very long threads would become
  one huge consolidator transcript.
- **Verified before designing:** DeepAgents' summarization keeps `state["messages"]` intact
  (it records its summary in a private field and offloads evicted history to a file), so the
  consolidator never loses early messages to it. `PIIMiddleware(apply_to_tool_results=True)`
  redacts a tool's result in state and in what the model sees. `ToolRuntime` gives a tool the
  store and the runtime context.

## Decision

- **Every replacing change keeps the previous version** in `(user, "memory_history")`; `/history`
  lists them and `/undo` restores the latest. Undo is the user's own command, so it writes the
  store directly.
- **A correction the user explicitly asked for skips approval** (`user_requested` on the edit,
  `requested=True` into the gate). The model sets the flag, so it is not trusted on its own:
  what makes it acceptable is that the change stays recoverable. The guard still judges the new
  content and can still ask; secrets still block.
- **Rejected edits are remembered** in `(user, "memory_rejections")` and shown to the next
  consolidation, which must not propose them again unless the user raises the fact again. A
  prompt rule, not a code filter: a code filter would also block a fact the user repeats.
- **Long threads are consolidated in segments.** Each run covers only the messages after the
  thread's watermark; one starts mid-conversation once the unconsolidated transcript passes
  `LONG_THREAD_CONSOLIDATION_CHARS`. Line-level edits make overlapping segments safe: an edit
  whose line is gone is skipped.
- **C1:** the P5 app has its own SQLite store and checkpointer. Watermarks, pending reviews,
  and the last session are durable; a conversation left at exit is consolidated on the next
  start; a reviewed run drops its checkpoints (they hold a transcript copy). `/forget` deletes
  a user's memory, history, bookkeeping, and threads.
- **C2:** a live eval-lite (`evals/p5_memory_eval.py`) outside pytest: assistant recall,
  isolation, and false "saved" claims; consolidator updates, request flags, implicit conflicts,
  invented facts, and re-proposed rejections; the guard on labeled writes.
- **C3:** a skill designer graph is the only writer to shared skills: draft, refuse (packaged
  names, secrets, a guard `block` under `SKILL_PUBLISH_POLICY`), then publish only after human
  approval, to a shared store namespace routed at `/published-skills/`. The assistant reads
  published skills and can't write them.
- **C4:** P5 is a context provider, not a chat subagent: `get_user_context` returns the calling
  user's memory files, read-only, secrets redacted. A composing agent that talks to the outside
  redacts personal data from tool results with `PIIMiddleware`. The P5 + P1 mini-workflow is
  `lab-brief`.

## Consequences

- P5 can now be composed like P1-P4 (and inherits their lack of a shared contract, which R0
  addresses for all five).
- `requested` trusts a model's flag for one class of change; C2 measures the flag, and
  `/undo` is the safety net.
- Skills can't be requested by other agents yet: a subagent's approval isn't surfaced to the
  app until P6-B, so `/skill` is a CLI command.
- A sequential SQLite connection per database is enough for one CLI user; concurrent users are
  Term E.

## Alternatives considered

- **Always approve corrections:** rejected; asking again for a correction the user just asked
  for adds friction without adding safety once the change is recoverable.
- **Filter rejected edits in code:** rejected; it would block a fact the user brings up again.
- **Consolidate from the summarization output:** rejected; summaries drop facts, and the raw
  messages are still in state.
- **Skill requests through a subagent now:** deferred to P6-B, which surfaces subagent approvals.
- **P5 as a chat subagent:** rejected; a caller needs context, not a conversation.
