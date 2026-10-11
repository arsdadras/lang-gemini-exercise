# ADR-0007: Agent model fallback uses `ModelFallbackMiddleware`

- Status: Accepted
- Date: 2026-09-13

## Context

A custom `retry_on_failure` middleware retried a failed model call on the same tier's other
providers. It caught every `Exception`, including LangGraph's `GraphBubbleUp` (the mechanism
behind interrupts). LangChain ships `ModelFallbackMiddleware`, which does the same job, lets
`GraphBubbleUp` through, and strips Anthropic cache markers before handing a request to a
non-Anthropic fallback model.

## Decision

`make_model_fallback(tier, primary=..., cascade=...)` builds a `ModelFallbackMiddleware` from
the model catalog (`llm_model.fallback_models`). Every agent built with `llm_model.get(tier)`
uses it. Graph nodes keep using `llm_model.chain(...)`.

## Consequences

- One place owns fallback ordering (the catalog). The retry loop itself is library code.
- Fallback models are built when the agent is built, so all configured provider keys must be
  present at that point.

## Alternatives considered

- **Keep the custom middleware:** rejected, because it reimplements a built-in with a worse
  interrupt behavior.
