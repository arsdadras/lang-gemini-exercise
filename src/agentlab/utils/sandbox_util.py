"""Sandbox helpers: the interpreter's shell backend, isolated pytest runs, deliverable discovery."""

import os
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePosixPath
from typing import Literal

from deepagents.backends import LocalShellBackend

from agentlab.configs.interpreter_config import (
    DEFAULT_EXECUTE_TIMEOUT,
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_SANDBOX_DIR,
    DEFAULT_VIRTUAL_MODE,
    SANDBOX_ENV_ALLOWLIST,
)
from agentlab.schemas.output.code_review_output_schema import TestRun
from agentlab.schemas.output.interpreter_output_schema import (
    Deliverable,
    DeliverableType,
)

DELIVERABLES_DIRNAME = "deliverables"
_WORKSPACE_ALIAS = "workspace"
_ARTIFACT_TYPES: dict[str, DeliverableType] = {
    ".csv": "csv",
    ".json": "json",
    ".png": "chart",
    ".jpg": "chart",
    ".jpeg": "chart",
    ".svg": "chart",
    ".pdf": "chart",
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".log": "text",
}


def build_sandbox_env(
    allowlist: Iterable[str] = SANDBOX_ENV_ALLOWLIST,
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Copy only allow-listed variables from ``source`` (default: ``os.environ``).

    Inheriting the whole process environment would hand LLM-driven commands every
    API key that ``load_dotenv()`` placed there.
    """
    environ = os.environ if source is None else source
    wanted = {name.upper() for name in allowlist}
    return {key: value for key, value in environ.items() if key.upper() in wanted}


class SandboxBackend(LocalShellBackend):
    """``LocalShellBackend`` that maps a leading ``workspace`` path segment to the sandbox root.

    Models often invent a ``/workspace/`` prefix for file tools while ``execute``
    runs with the sandbox root as its working directory; mapping the alias keeps
    both looking at the same files. Shell commands are never rewritten.
    This overrides a private ``LocalShellBackend`` hook, so ``tests/test_sandbox.py``
    pins the behavior across DeepAgents upgrades.
    """

    def _resolve_path(self, key: str) -> Path:
        normalized = key.replace("\\", "/")
        is_absolute = normalized.startswith("/")
        parts = PurePosixPath(normalized).parts
        if is_absolute:
            parts = parts[1:]
        if parts[:1] != (_WORKSPACE_ALIAS,):
            return super()._resolve_path(key)
        remainder = "/".join(parts[1:])
        if not remainder:
            return super()._resolve_path(".")
        return super()._resolve_path(f"/{remainder}" if is_absolute else remainder)


def make_sandbox_backend(root_dir: Path = DEFAULT_SANDBOX_DIR) -> SandboxBackend:
    """Build the interpreter backend: confined file tools and an allow-listed shell environment."""
    (root_dir / DELIVERABLES_DIRNAME).mkdir(parents=True, exist_ok=True)
    return SandboxBackend(
        root_dir=root_dir,
        virtual_mode=DEFAULT_VIRTUAL_MODE,
        env=build_sandbox_env(),
        timeout=DEFAULT_EXECUTE_TIMEOUT,
        max_output_bytes=DEFAULT_MAX_OUTPUT_BYTES,
    )


def run_tests_in_sandbox(
    code: str,
    test_code: str,
    timeout_seconds: int = 15,
) -> TestRun:
    """Run generated pytest code against ``code`` in a throwaway directory.

    Generated tests are untrusted code, so the subprocess only gets the
    allow-listed environment.
    """
    if not test_code.strip():
        return TestRun(
            status="error",
            passed=False,
            exit_code=-1,
            output="No test code provided to execute.",
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir)
        (workdir / "tested_module.py").write_text(code, encoding="utf-8")
        test_file = workdir / "test_module.py"
        test_file.write_text(test_code, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", str(test_file)],
                cwd=workdir,
                env=build_sandbox_env(),
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return TestRun(
                status="timed_out",
                passed=False,
                exit_code=-1,
                output=f"Test execution timed out after {timeout_seconds} seconds.",
            )
        except OSError as exc:
            return TestRun(
                status="error",
                passed=False,
                exit_code=-1,
                output=f"Could not start pytest: {exc}",
            )

    passed = completed.returncode == 0
    output = completed.stdout + (f"\n{completed.stderr}" if completed.stderr else "")
    return TestRun(
        status="passed" if passed else "failed",
        passed=passed,
        exit_code=completed.returncode,
        output=output,
    )


def list_sandbox_deliverables(
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> list[Deliverable]:
    """List every file under the sandbox's ``deliverables/`` directory."""
    deliverables_dir = sandbox_dir / DELIVERABLES_DIRNAME
    if not deliverables_dir.is_dir():
        return []

    deliverables: list[Deliverable] = []
    for item in sorted(deliverables_dir.rglob("*")):
        if not item.is_file():
            continue
        stat = item.stat()
        deliverables.append(
            Deliverable(
                name=item.name,
                path=item.relative_to(sandbox_dir).as_posix(),
                deliverable_type=_ARTIFACT_TYPES.get(item.suffix.lower(), "other"),
                description=f"{item.suffix.upper().lstrip('.')} deliverable ({stat.st_size} bytes)",
                size_bytes=stat.st_size,
                modified_at=stat.st_mtime,
            ),
        )
    return deliverables


DeliverableSnapshot = dict[str, tuple[int | None, float | None]]
DeliverableChange = Literal["new", "modified"]


def snapshot_sandbox_deliverables(
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> DeliverableSnapshot:
    """Capture each deliverable's (size, mtime), to diff against after an agent turn."""
    return {
        a.path: (a.size_bytes, a.modified_at)
        for a in list_sandbox_deliverables(sandbox_dir)
    }


def diff_sandbox_deliverables(
    before: DeliverableSnapshot,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> list[tuple[DeliverableChange, Deliverable]]:
    """Compare a prior snapshot to the current deliverables: what's new, what changed.

    An deliverable absent from ``before`` is new; one present with a different
    (size, mtime) pair was modified in place. Deletions aren't reported — nothing
    that generates deliverables currently removes them mid-run.
    """
    changes: list[tuple[DeliverableChange, Deliverable]] = []
    for deliverable in list_sandbox_deliverables(sandbox_dir):
        previous = before.get(deliverable.path)
        if previous is None:
            changes.append(("new", deliverable))
        elif previous != (deliverable.size_bytes, deliverable.modified_at):
            changes.append(("modified", deliverable))
    return changes


def get_deliverable_path(
    relative_path: str,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> Path:
    """Resolve an deliverable path, rejecting anything outside ``deliverables/``."""
    deliverables_dir = (sandbox_dir / DELIVERABLES_DIRNAME).resolve()
    target = (sandbox_dir / relative_path).resolve()
    if not target.is_relative_to(deliverables_dir):
        msg = (
            f"Path traversal attempt: {relative_path} is outside deliverables directory"
        )
        raise ValueError(msg)
    return target
