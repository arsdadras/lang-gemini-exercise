# ADR-0005: Sandboxed code never sees secrets

- Status: Accepted
- Date: 2026-09-13

## Context

- **The interpreter shell inherited every secret.** The interpreter's `LocalShellBackend` used
  `inherit_env=True`, which copies `os.environ`. After `load_dotenv()`, that environment holds
  every API key and token in `.env`.
- **Nothing gated the coordinator's shell.** The coding coordinator ran that interpreter with no
  approval step.
- **Generated tests inherited it too.** P3's pytest subprocess, which runs LLM-generated test
  code, also inherited the full environment.
- **The repo-insight agent could read `.env`.** Its filesystem backend's root is the whole
  repository.
- **No leak was found.** Local checkpoint history holds no secret names, so this was a
  structural risk, not an incident.

## Decision

- **Allow-listed environment.** Shell backends and test subprocesses get only the variables in
  `SANDBOX_ENV_ALLOWLIST` (`configs/interpreter_config.py`, applied by `build_sandbox_env()`).
- **Read-only repo view.** The repo-insight agent denies `read` on `/.env` and `/.env.*` and
  denies every `write`, using `FilesystemPermission` rules.
- **HITL stays on for the interactive interpreter.** The standalone interpreter keeps approval
  on `execute`.
- **The coordinator's nested interpreter stays without approval for now.** Its CLI loop can't
  surface approvals raised inside a subagent yet. The app banner says so, and P6 Phase B fixes
  it.

## Consequences

- Sandboxed scripts that need an API key can't get one. That is intended.
- Real isolation (containers, a remote sandbox, session-scoped workspaces) belongs in Term E.

## Alternatives considered

- **A denylist of known secret names:** rejected, because it fails open for any new key.
- **A container sandbox now:** rejected as out of scope for Term P.
