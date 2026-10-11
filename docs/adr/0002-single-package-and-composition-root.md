# ADR-0002: One `agentlab` package; apps are the composition root

- Status: Accepted
- Date: 2026-09-13

## Context

- **Every folder was a top-level package.** Each folder under `src/` was installed as its own
  top-level package: `agents`, `models`, `utils`, `data`, `tools`, `core`, and so on. Generic
  names like these collide with names that dependencies ship. It already happened once:
  `chromadb` ships a `schemas/` directory, Python merged it with ours into a namespace
  package, and imports broke.
- **Scratch code leaked into the library.** The mentee's scratch folder `alireza/` was part
  of the distribution, and `src/core/decorators.py` imported from it. Only the pytest
  `pythonpath` setting hid the break.
- **Importing had side effects.** Modules built agents, models, SQLite connections, and
  Tavily clients, and called `load_dotenv()`, all at import time. Importing one agent built
  every agent and required secrets to be present.

## Decision

- **One package.** A single import package `agentlab` under `src/` (standard src layout),
  distributed as `agentlab`. Apps are exposed as `lab-*` console scripts. Skill files ship as
  package data, and runtime state lives under `out/` (gitignored).
- **Factories only.** Library modules expose factories (`make_*`, `build_*`) and constants.
  Nothing is constructed at import.
- **Apps are the composition root.** Each app's `main()` calls `load_dotenv()`, builds the
  object graph, and runs the loop.
- **Secrets by name.** The model catalog stores environment variable *names*; values are read
  only when a model is built.

## Consequences

- Imports are explicit: `from agentlab.models import llm_model`. No collisions with
  dependency package names, and no pytest path hacks.
- Importing a module has no side effects and needs no secrets. Import still takes about 3.5s,
  which is library import cost, not construction.
- Tests and notebooks build exactly what they need, with injected checkpointers, stores,
  and models.

## Alternatives considered

- **Keep flat top-level packages and rename on each collision:** rejected, because it fixes
  collisions only after they break something.
- **Lazy imports to avoid construction cost:** rejected, because they hide dependencies and
  leave the side effects in place.
