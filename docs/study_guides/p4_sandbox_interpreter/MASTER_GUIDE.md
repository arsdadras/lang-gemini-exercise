# P4 Study Guide: Sandbox Interpreter and Coding Coordinator

Rewritten 2026-09-13 to match the code. Paths are relative to `src/agentlab/`.

## The problem

Let an agent do real work in an environment: write scripts, run them, read the output, fix
errors, and leave deliverable files behind. Then compose that capability with research (P1)
and code review (P3) under a coordinator.

## Phase A: a workspace as the agent's environment

- **Agent:** `agents/interpreter_agent.make_interpreter_agent` calls `create_deep_agent` with a
  shell-capable backend. DeepAgents then provides file tools (`ls`, `read_file`, `write_file`,
  `edit_file`, `glob`, `grep`), `execute`, and `task`.
- **Backend** (`utils/sandbox_util.make_sandbox_backend`): a `SandboxBackend`, which is a
  `LocalShellBackend` rooted at `out/sandbox/` with a timeout and an output cap.
  - `virtual_mode=True` confines the **file tools** to the root. It doesn't confine **shell
    commands**, which is why approval matters (Phase B).
  - The shell environment is allow-listed: `PATH`, `SYSTEMROOT`, temp dirs, and a few others,
    and never API keys (ADR-0005).
  - Models like to invent a `/workspace/` prefix, so the backend maps a leading `workspace`
    segment to the root. File tools and the shell then see the same files.
- **Prompt** (`prompts/agents_prompt.build_interpreter_agent_prompt`): write a script, execute
  it, verify the result, self-correct; save deliverables under `artifacts/`.

## Phase B: governance, artifacts, durability

- **Approval before shell commands:**
  - `interrupt_on={"execute": True}` pauses before every `execute` call;
  - `utils/run_with_hitl_util.run_with_hitl` shows the pending action and resumes with
    `Command(resume={"decisions": [{"type": "approve"}]})`, or with a rejection plus an
    optional reason that the agent reads as feedback.
  - File-level permission rules can't constrain a shell (a command can `cat` or `rm` anything),
    so approval, not path rules, is the safeguard here.
- **Artifacts:**
  - deliverables live in `out/sandbox/artifacts/`;
  - `list_sandbox_artifacts` returns `ArtifactMetadata` (path, type, size, mtime);
  - `get_artifact_path` rejects traversal with `Path.is_relative_to`.
- **Durability:**
  - the default checkpointer is SQLite (`out/state/checkpoints.db`);
  - on startup the app checks `agent.get_state(config).next` and resumes an approval a crashed
    session left pending;
  - `utils/session_util.resolve_session` maps a CLI argument (`new`, `secret`, `resume`,
    `step[N]`, `list`, or a name) to a thread id, and builds the agent with a factory: `None`
    selects the durable checkpointer, `InMemorySaver` selects secret mode.
- **Dual-state problem:** checkpoints capture messages and interrupts, not the filesystem.
  Rewinding a thread does not rewind the sandbox.

## Phase C: composition

- **Subagent adapter** (`subagents/interpreter_subagent.py`): wraps an *injected* interpreter
  agent, built by the caller, so `subagents/` never imports `agents/`. It snapshots
  `artifacts/` before a delegation, invokes the agent on a fresh thread, and appends a
  "Deliverables Update" listing `[NEW]` and `[MODIFIED]` files with exact paths. (Since R0 the
  same facts are the envelope's side effects, rendered as a `Changed:` line; see
  `schemas/output/specialist_output_schema.py`.)
- **Coordinator** (`agents/coding_coordinator_agent.py`):
  - a DeepAgent over `code_interpreter` (P4), `code_review_subagent` (P3), and `researcher` (P1);
  - `TodoListMiddleware` for planning, plus model fallback;
  - its prompt teaches goal decomposition and hand-offs (research -> compute -> review), and
    requires copying deliverable paths verbatim;
  - its nested interpreter currently runs without per-command approval, because the CLI can't
    surface approvals raised inside a subagent yet (P6 Phase B).
- **Streaming** (`utils/streaming_util.stream_agent_with_observability`):
  `stream(..., stream_mode="updates", subgraphs=True)` prints todo updates, delegations, tool
  calls, and tool results live.

## Running it

```bash
uv run lab-interpreter          # approve each shell command
uv run lab-interpreter secret   # nothing written to the checkpoint DB
uv run lab-coordinator new
```

## Lessons worth keeping

- The environment is part of the agent's interface. Confinement, environment variables, and
  timeouts are design decisions, not plumbing.
- Keep each responsibility in one place: the subagent adapter owns deliverable discovery, so the
  UI only renders it. (This came from the mentee's critique, which removed a duplicate diff from
  the app.)
- Describe goals and hand-off patterns in coordinator prompts; don't script every step.
- Inject dependencies downward instead of importing upward.
- An agent registry was built here and later removed (ADR-0006). Wait for a real consumer
  before adding an abstraction.

## Tests

- `tests/test_sandbox.py`: workspace alias, environment allowlist (including a real shell call
  that can't read a planted secret), artifacts, traversal.
- `tests/test_run_with_hitl.py`: approval and rejection decisions, and the resume loop.
- `tests/test_session_util.py`: every session mode.
- `tests/test_streaming_util.py`: streaming event handling.
