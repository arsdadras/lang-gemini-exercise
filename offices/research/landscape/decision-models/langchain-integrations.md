# LangChain and LangGraph Integrations

[Decision models](README.md) › integrations. Read from the packages' **own source**:
`langchain-typesafe` 0.0.1a3 (the published wheel) and `laya` 0.3.20 (the repository), on
2026-09-26. The OpenRouter path and the dependency check were added **2026-09-27**. Labels: [V]
verified here, [S] primary source.

## langchain-typesafe

The Jev client, with experimental agent middlewares.

### Package

| | |
| :--- | :--- |
| Maintainer | LangChain, inside the `langchain-ai/langchain` monorepo; MIT **[S]** |
| Releases | `0.0.1a1` and `a2` on 2026-09-17, `a3` on 2026-09-20; still the latest on 2026-09-27. The classifier emits `LangChainBetaWarning` ("API may change") **[S][V]** |
| Requires | `httpx2 >=2,<3`, `langchain-core >=1.6.2,<2`; the `[experimental]` extra adds `langchain >=1.3.15` **[S]** |
| Against our lock (2026-09-27) | The stack upgrade (commit `0d27fa8`) put `langchain-core` at 1.6.5 and `langchain` at 1.4.2, and `httpx2` 2.13.1 is already locked (through `anthropic`, `langsmith`, and `openai`). `uv add "langchain-typesafe[experimental]"`, dry-run on a scratch copy of `pyproject.toml` and `uv.lock`, adds exactly one package and changes no version **[V]**. What remains is policy: it's a pre-release, and the radar's dependency policy needs a recorded reason and an exit date |
| Settings | `TYPESAFE_API_KEY`; `TYPESAFE_BASE_URL`, default `https://api.typesafe.ai`. Requests go to `<base_url>/v1/systemone` **[S]** |
| Through OpenRouter | `base_url="https://openrouter.ai/api"` with the OpenRouter key: 11 of 11 checks passed against the real Jev, including the async path, typed errors, and the experimental middleware ([EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md)) **[V]** |

### `TypeSafeClassifier`

A `RunnableSerializable[ClassifierRequest, ClassifierResponse]` **[S]**.

**Fields:**

- `model`, default `"jev-latest"`;
- `api_key` and `base_url`;
- `timeout`, default 30 s;
- optional injected `httpx2` clients, sync and async.

**Calls:** `invoke`, `ainvoke` (a real async path), and `batch`.

**Input:** `{"state": ..., "questions": {name: Noul | Choice | Score}}`. The state can be a
string, JSON, or LangChain messages, which it converts to OpenAI-style role/content dicts.

**Output:** a `ClassifierResponse` with:

- `.nouls`: P(true) per question;
- `.choices`: `choice`, `probabilities`, `confidence`;
- `.scores`: the expected `score` (may be fractional), `probabilities`, `confidence`;
- `.model`: the versioned ID that actually answered;
- `.usage`: token counts.

**Tracing:** tags the LangSmith run with `ls_provider`, `ls_model_name`, and token usage.

**What it drops through OpenRouter [V]:** the response model has no field for OpenRouter's
generation `id` or `usage.cost`, so both are discarded. `request_id` stays empty, because
OpenRouter doesn't send TypeSafe's request-ID header. For spend reconciliation or an audit
trail, compute the cost from `usage.input_tokens`, or read the raw body.

**Errors:** one class per HTTP status, each subclassing the matching `langchain_core` model
error:

| Status | Subclasses |
| :--- | :--- |
| 400, 422 | `ModelInvalidRequestError` |
| 401 | `ModelAuthenticationError` |
| 429 | `ModelRateLimitError`, carrying `retry_after_ms` |
| 5xx | `ModelAPIError` |

Connection and timeout errors also subclass Python's `ConnectionError` and `TimeoutError`.
Error strings never include response bodies or headers.

**No retry of its own:** it only parses `retry-after` into the error. The official
`typesafe_sdk` retries by default; this client does not.

**How it meets this repo's conventions** (read-only analysis):

- **Convention 11** (`utils/failure_util.py`) would classify these errors correctly without
  changes:
  - API errors expose `status_code` (408/429/5xx are transient, the rest permanent);
  - connection and timeout errors match the builtin classes it checks.

  `failure_util.py` was uncommitted work in another session on 2026-09-26, so re-check once it
  lands.
- **Retries:** since the classifier doesn't retry, Convention 11 gives it exactly one retry
  layer (`TRANSIENT_RETRY` on its node, or `ToolRetryMiddleware`). It's an external call, not a
  model call with a provider SDK behind it.
- **Convention 8:** typed Pydantic answers match it directly.

### Experimental middlewares

Both live in `langchain_typesafe.experimental.middleware`. They are LangChain v1
`AgentMiddleware`, the same kind this repo uses **[S]**.

**`AutoModeMiddleware(tools=[...], instructions=?, criteria=?)`**

- **Hook:** `wrap_tool_call`, sync and async.
- **What it does:** for the listed tools only, it asks one `noul`: "is this call risky or
  insufficiently authorized?" The state is the last 30 messages, the tool call, and the tool's
  description. At P ≥ 0.5 it returns an error `ToolMessage` and never runs the tool.
- **Limits worth knowing:**
  - **The 0.5 threshold is a hard-coded constant**, though a docstring implies it's
    configurable.
  - **It blocks and never asks a human**, which differs from Convention 7 (consequential tools
    get HITL).
  - A classifier error propagates, so the call fails rather than running.
  - Tool arguments are left out of traces.
  - It builds its own classifier from `TYPESAFE_BASE_URL` and `TYPESAFE_API_KEY`. Set to the
    OpenRouter values, it blocked a destructive, unrequested call and let a requested read
    run **[V]**.

**`ModelRouterMiddleware(choices={route: ModelChoice(model, criteria)}, instructions=?)`**

- **Hooks:** `before_agent` and `wrap_model_call`.
- **What it does:** once per run, it classifies the latest human message with a `choice`,
  stores the result as `model_route`, and swaps the model through `request.override(model=...)`.
- **Limits worth knowing:**
  - **Argmax only:** there's no confidence threshold and no fallback when unsure, so it is not
    a calibrated cascade.
  - Classifier errors propagate.
  - A model given as a string is built with `init_chat_model`, outside our `llm_model`
    registry. A `BaseChatModel` instance is used as-is, but its tier fallback still has to be
    added separately.

Both are useful references for wiring a decider into v1 middleware. Neither implements the
asymmetric, fail-safe cascade the office plans; that would be our own component around
`TypeSafeClassifier`.

## Beyond LangChain (2026-09-27)

Listed from the public catalog and read at summary level **[T]**. Useful mainly as evidence of
which seams the ecosystem converged on.

| Where | What it adds |
| :--- | :--- |
| LangChain.js | The same classifier Runnable and middleware in TypeScript |
| LangSmith | Jev as an evaluator in experiments; LangChain says it has views for decision models' inputs and probabilities **[C]** |
| Langfuse | A native Jev evaluator: typed questions write scores to matching observations |
| Pydantic AI | A model provider that derives Jev questions from Pydantic output types, with typed routing and fallback |
| LiteLLM | Complexity routing, and a relevance guardrail that compacts tool results before the agent reads them |
| Vercel `eve` | Jev as the framework's default "evaluate" model |
| Composio | Tool shortlisting, a choice from a bounded set, closed-set arguments, and destructive-action gates |
| BAML, TanStack AI, Effect, Ax | Typed decide/classify operations mapped onto Choice, Noul, and Score |
| `llamacpp-jev` | Any local model behind llama.cpp served on `/v1/systemone`: a third self-hosted backend besides Laya and Open-Jev |
| TypeSafe's agent skill | An official skill for Claude Code, Codex, and other agents on writing TypeSafe integrations; installable as a Claude Code plugin **[S]** |

The convergence point matches this page's conclusion: one typed client over a shared protocol,
with the backend chosen by configuration.

## Laya's own integration

`laya.integrations.langchain`, 537 lines **[S]**:

| Class | Kind | Notes |
| :--- | :--- | :--- |
| `LayaRouter(criteria, confidence_threshold=0.0, fallback=None, state_key=None)` | Runnable, used as a LangGraph conditional edge | Has a threshold and a fallback route: the cascade in miniature. The threshold **defaults to 0.0, so gating is off**; the 0.80 in the docs is only an example |
| `LayaGuardrail(questions=?, action="raise" \| "filter" \| "annotate")` | Runnable | Default questions come from its injection, jailbreak, and leak preset |
| `LayaTriage` | Runnable | A fixed preset: intent, urgency, frustration, churn |
| `LayaEvaluator(questions)` | Runnable | You supply the rubric, e.g. a groundedness `noul` |

- **Sync only:** there's no `ainvoke`, so under async LangGraph execution the forward pass blocks.
- **Two modes:** in-process (loads torch and the checkpoints), or remote through `base_url` to a
  `laya-serve` (no torch in the client). Remote calls refuse cross-origin and
  HTTPS-downgrade redirects.
- **Not `AgentMiddleware`:** these are Runnables for LCEL and graph nodes, not
  `before_model`/`after_model` hooks.

## The shared seam: `/v1/systemone`

The official Jev client ran unchanged against two different servers **[V]**:

- `laya-serve`: 8 of 8 checks, covering sync, async, and batch calls, messages as state, typed
  401/422 errors, and the tool-risk middleware
  ([EV-2026-09-26-jev-wire-compat](../../evidence/EV-2026-09-26-jev-wire-compat/README.md));
- OpenRouter's System One API, serving the real Jev: 11 of 11
  ([EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md)).

So with one client, the backend is a configuration choice, pinned by URL and model ID: Jev
through OpenRouter, Jev direct, self-hosted Laya, or Open-Jev. Swapping it changes no call
site.
