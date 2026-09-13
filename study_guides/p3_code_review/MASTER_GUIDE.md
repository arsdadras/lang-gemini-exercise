# P3 Study Guide: Code Review and Test Generation

Rewritten 2026-09-13 to match the code. Paths are relative to `src/agentlab/`.

## The problem

Given source code, produce a structured review, generate tests, run them safely, repair
failing tests, and apply a refactor only after a human approves it. Every step is known in
advance, so this is a **workflow** (raw LangGraph), not an autonomous agent.

```
START -> reviewer -> [error?] -> test_generator -> [refactored code?] -> refactor_gate -> END
                                  (generate -> execute -> fix loop)       (interrupt -> apply)
```

## Phase A: state and structured output

- **State** (`state/code_review_state.py`): a `TypedDict` where only `code` is required. Each
  node returns a partial update. `error` is a fail-fast channel that routers check before
  continuing.
- **Schemas** (`output_schemas/code_review_output_schema.py`):
  - `ReviewResult` (score 1-10, summary, `CodeIssue` list, optional `refactored_code`);
  - `TestSuite` (framework, `test_code`, `TestCase` list);
  - `TestExecutionResult` (status, passed, exit code, output).
- **Structured calls** (`nodes/code_review_node.py`):
  `REVIEW_PROMPT | llm_model.chain("medium", structured=ReviewResult, cascade=True)`. The model
  must answer in the schema, and if the medium tier fails the call cascades to lower tiers.

## Phase B: execution, loops, approval, persistence

- **Sandboxed tests** (`utils/sandbox_util.run_tests_in_sandbox`):
  - writes `tested_module.py` and `test_module.py` into a temporary directory;
  - runs `python -m pytest` in a subprocess with a timeout;
  - the subprocess gets an **allow-listed environment**, because generated tests are untrusted
    code (ADR-0005).
- **Self-correction loop** (`graphs/test_gen_subgraph.py`):
  - `execute_tests` -> `route_after_execution`, which goes to `fix_tests` while tests fail and
    `test_retries < max_test_retries`;
  - the retry budget defaults to `MAX_TEST_RETRIES = 2` and can be overridden per run via
    `config["configurable"]["max_test_retries"]`;
  - `fix_tests` feeds pytest's output back into `TEST_FIX_PROMPT` and loops back to
    `execute_tests`.
- **Human approval** (`nodes/code_review_node.approved_refactor_node`):
  - `interrupt({"action_required", "summary", "refactored_code"})` pauses the graph and
    persists the state;
  - the app resumes with `graph.stream(Command(resume="approve" | "reject"), config)`;
  - `route_after_approval` sends the run to `apply_refactor` (which sets `applied_code`) or
    ends it.
- **Persistence:** the parent graph compiles with a checkpointer (the app uses SQLite at
  `out/state/checkpoints.db`). Interrupts, resume, and history all depend on it.

## Phase C: subgraphs, composition, time travel

- **Three compiled subgraphs** (`graphs/reviewer_subgraph.py`, `test_gen_subgraph.py`,
  `refactor_subgraph.py`), each mounted as a single node by `graphs/code_review_parentgraph.py`.
  - Each subgraph is testable and replaceable on its own.
  - The parent sees one node per stage; subgraph state flows through the shared schema.
- **Subagent adapter** (`subagents/code_review_subagent.py`): DeepAgents coordinators speak
  `messages`, but the pipeline speaks `CodeReviewState`. The adapter reads the last message as
  code, runs the graph on a fresh thread, and renders a Markdown report. The graph's own state
  never learns about chat.
- **Time travel** (`utils/time_travel_util.py`): `inspect_state_history` lists checkpoints;
  `fork_from_checkpoint` re-invokes from a chosen `checkpoint_id`.

## Running it

```bash
uv run lab-code-review examples/buggy_bank_account.py
uv run lab-code-review list            # recorded sessions
uv run lab-code-review step[0]         # inspect or resume the latest session
```

## Lessons worth keeping

- Choose workflow vs agent by asking: is the control path known in advance?
- Put failure in state (`error`) and route on it; don't let exceptions tear down the run.
- An approval gate is only as durable as the checkpointer behind it.
- Adapters keep each component's contract clean: chat at the edge, typed state inside.
- Treat generated code as untrusted input everywhere it runs.

## Tests

`tests/test_code_review.py` covers schemas, all routers, subgraph compilation, passing and
failing sandbox runs, secret isolation, SQLite checkpointing and history, and the subagent spec.
