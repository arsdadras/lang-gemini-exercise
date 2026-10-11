---
name: mentor
description: Run a whole agentlab session as the mentor, the project's only role - sync with main, read the state, prepare the lesson and its code, teach, and close the session. Invoked by the user only.
disable-model-invocation: true
---

This is a **mentor** session of the agentlab repository, the project's only role
([ADR-0028](../../../docs/adr/0028-one-mentor-one-branch.md)). Run the whole session yourself,
without waiting to be told each step.

1. **Sync with `main`.** `git fetch origin`, then bring this checkout to `origin/main`:
   - on `main`: `git merge --ff-only origin/main`;
   - in a worktree the desktop app made (branch `claude/...`): the `sync_with_base_branch` tool,
     or `git merge origin/main`.
   Commit or carry over anything uncommitted first; never discard work. Run `uv sync` if the
   checkout has no `.venv`.
2. **Read** `mentor/README.md` (the charter) and `mentor/STATE.md` (where teaching stands, the
   next step, the build queue, the working agreements).
3. **Prepare the next lesson** before the first message: plan the topic, build and verify the
   code it needs (or review code already built), and run it in test mode
   (`LLM_TEST_MODE=true`). Load the `teach` skill before writing to the learner.
4. **Teach** step by step, waiting for the learner between steps, following the charter's
   stage delivery and the working agreements in `STATE.md`.
5. **Close** when the last planned step is done and the learner has no more questions: say in
   one line that the session ends, prepare the next session (build or queue what the next topic
   needs), then run `/handoff`.

If the user wrote a request after the command, handle it after steps 1 and 2.
