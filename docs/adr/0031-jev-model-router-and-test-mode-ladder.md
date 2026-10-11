# ADR-0031: A Jev model router beside the tier catalog, and a test-mode ladder

- Status: Accepted
- Date: 2026-10-08
- Origin: user direction (a mentor session). The mentor agreed with the router, with one
  amendment recorded under Alternatives, and built it without a live call, as the user asked.
- Revisit when: the router's labeled set is measured (`evals/model_route_eval.py`), or a call
  site needs a different model by the kind of work (code, writing, research), not only by its
  difficulty.

## Context

- Every call site names its tier by hand (`llm_model.get("medium")`), once, at design time. The
  work a call site gets varies per request: a one-line lookup and a design question reach the
  same tier. The dossier's second tier mechanism, routing per request, was planned for D1
  ([decision-models.md](../../library/architecture/decision-models.md#model-tiers)).
- Test mode had one step up from the free model (Gemini 3.8 Flash, on Google's API too). The user
  asked for a ladder instead, and a rule about the gateways: GapGPT always has credit but is
  sometimes down; OpenRouter is always up but its key is usually empty; Google's quota is large
  for Gemini 3.5 Flash-Lite only, so no other Google model is ever called there.

## Decision

1. **Test mode is a ladder of opt-in tiers,** each used only when the one below was not enough
   because of the model, selected by `LLM_TEST_PROFILE`:

   | Profile | Models, in order | Gateways |
   | :--- | :--- | :--- |
   | `default` (`free`) | Gemini 3.5 Flash-Lite | GapGPT, OpenRouter, Google's API |
   | `strong` | Claude Haiku 5.5, GPT-6 Luna | each on GapGPT, then OpenRouter |
   | `strongest` | Gemini 3.8 Flash, Claude Sonnet 5.5, GPT-6.1 Sol | each on GapGPT, then OpenRouter |
   | `local` | Qwen 4B, Qwen 2B | Ollama |

   Above `free` there is no Google leg and no model outside its rung; when every leg fails the
   call fails, and the next rung is chosen by a person. Claude Haiku 5.5 was removed from `free`
   and moved up: it is a better model, not a backup of the free one.
2. **Haiku 5.5 is registered on GapGPT** (`claude-haiku-5-5`) although GapGPT does not list it
   yet, so the day it does, nothing changes in code. Until then each call to it fails fast on
   GapGPT and falls through to its OpenRouter backup. This also applies to the `low` tier.
3. **A Jev model router, `models/router_model.py`, runs beside `llm_model` and replaces nothing.**
   A call site that names its tier is untouched. One that wants the model chosen by the task
   calls `model_router.chain(task, structured=Schema)` (a graph node) or `model_router.plan(task)`
   (an agent: `primary`, and `fallbacks` for its fallback middleware).
   - **Jev decides the class of work, code decides the model.** One request, two typed questions
     (`model_route@1`): `difficulty`, a score over four levels, and `stakes`, the probability
     that a mistake is costly or hard to undo. The state carries each tier's profile and the
     models in it, read from the catalog so there is one list; the task follows, redacted of
     secrets and marked as data.
   - **Asymmetric thresholds:** "low" needs 0.8 on the two easy levels together, "high" needs
     0.5 on the expert level alone, and everything else is "medium". Stakes lift a task to at
     least "medium" and never buy "high". A caller's `floor` and a task longer than about 30k
     tokens lift the tier and never lower it. All of it is provisional until the set is measured.
   - **Fail open to "medium"** on a decider outage (an external failure); a bug raises. In test
     mode the decider is not asked at all and the test profile's tier is used.
   - **The chain is GapGPT, then the OpenRouter backup, then the `last_resort` tier:** Gemini 3.5
     Flash-Lite on Google's API, then a free OpenRouter model. The tier's other providers are
     not tried: in a gateway outage they would add four failed calls, and the user's order skips
     them. The routed tiers are `low`, `medium`, `high`; `opensource` joins when it is measured
     (RSK-08).
4. **Evidence:** `evals/datasets/model_routes.json` (54 tasks, 12 of them Finglish) and
   `evals/model_route_eval.py`, run by hand. Nothing here was called live: the unit tests use a
   scripted decider and stub models.

## Consequences

- No call site moves to the router yet. The standard asks for a measured set and a shadow run
  before a backend change; each adoption is its own decision, and the first candidates are
  the nodes whose work varies most per request (the RAG answer, the research report).
- Three IDs are registered without a live call: `claude-haiku-5-5`, `gpt-6-luna`, and
  `gpt-6.1-sol` on GapGPT (their OpenRouter IDs are in OpenRouter's public list). A wrong
  spelling costs one failed call and then the OpenRouter backup answers. `scripts/smoke_live.py`
  now runs all three ladder profiles, so the next live run settles it.
- A degraded route is silent to the caller: a "high" task can end on Gemini 3.5 Flash-Lite when
  both gateways are down. The decision log (`agentlab.routing`) records the tier asked for, not
  the model that answered; the trace shows the latter.
- The free OpenRouter model is the last hope and may keep the prompt (free endpoints often do).
  It is reached only after every paid route failed; remove it if the data policy forbids that.
- `smoke_live.py` and the README named a `reliable` profile that ADR-0015's update had removed;
  both are corrected.

## Alternatives considered

- **Ask Jev to pick the model directly, from model names and descriptions** (the user's first
  framing). Rejected, and amended into the above: a decision model reads the task and the
  criteria text; it has never seen what "Sonnet 5.5" is good at, so a choice over model names
  is a guess on lexical similarity. The rule is atomic questions in, a mapping in code out
  ([decision-models.md](../../library/architecture/decision-models.md#writing-the-questions)).
  Jev still gets the model information (the tier profiles and their models); the answers it
  gives are about the task, which it can judge.
- **A router that also picks by specialty (code, writing, research).** Deferred: no measurement
  says which provider of a tier does better at which; the catalog's scores are hand estimates.
  The trigger is R2's catalog calibration.
- **Replace the tiers with the router.** Rejected: the user asked for a separate system, and a
  call site with a fixed, tested tier is a safe default.
- **Same-tier alternates before the last resort.** Rejected for the reason in 3.
- **Keep Gemini 3.8 Flash on Google's API in `strong`.** Rejected by the user: Google's quota
  covers Flash-Lite only.
