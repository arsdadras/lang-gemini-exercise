# ADR-0003: User identity travels as runtime context

- Status: Accepted
- Date: 2026-09-13

## Context

P5's store namespace factory read `runtime.config["configurable"]["user_id"]`. But the LangGraph
`Runtime` object that `StoreBackend` passes to that factory has no `config` attribute. The
factory therefore always fell back to the default user, and every user shared the
`("default_user", "memories")` namespace. Its unit test used a hand-made fake runtime that
*did* have `.config`, so the test passed while the real behavior was broken. Running a real
graph with two users on 2026-09-13 confirmed the bug.

## Decision

- Identity is runtime context. Build the agent with `create_deep_agent(context_schema=UserContext)`,
  and call it with `invoke`/`stream(..., context=UserContext(user_id=...))`.
- The namespace factory reads `runtime.context` and raises when identity is missing. There is
  no shared default user.
- `thread_id` stays in `config["configurable"]`, because it belongs to the checkpointer.
- Behavior at a framework boundary is tested through a real graph with a scripted fake model.
  Only the model is faked, never the framework (ADR-0004).

## Consequences

- Apps pass `context` on every call. Forgetting it fails loudly instead of mixing users' data.
- P5 Phase C extends CLI session resolution to the pair (`thread_id`, `user_id`).

## Alternatives considered

- **`get_config()` inside the factory:** works, but it keeps identity in untyped config
  plumbing.
- **Fall back to a default user when identity is missing:** rejected, because it causes the
  same silent data mixing again.
