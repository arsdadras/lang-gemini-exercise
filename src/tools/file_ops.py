"""File-system tools for agent use.

Provides primitives for creating files and writing content in various
formats (text, JSON, raw bytes).  Each writer follows a uniform
``(path, content) -> path`` contract so they can be used as *operation*
callbacks via :class:`FileData`.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Operation = Callable[[Path, Any], Any]


@dataclass
class FileData:
    """Payload descriptor for :func:`create_file`."""

    content: Any = None
    operation: Operation | None = None


def create_file(
    folder: str | None = None,
    file: str | None = None,
    extension: str = ".md",
    data: FileData | None = None,
    *,
    base_dir: Path | None = None,
) -> Path | Any:
    """Create a file, optionally running an *operation* on it.

    Args:
        folder: Sub-directory under *base_dir*. Created if it doesn't exist.
        file: File stem (without extension). Defaults to ``"untitled"``.
        extension: File extension including the dot.
        data: Optional :class:`FileData` with content and/or an operation.
        base_dir: Root directory. Defaults to the package directory.
    """
    parent_path = base_dir if base_dir is not None else Path(__file__).parent

    ext = extension if extension.startswith(".") else f".{extension}"
    target_dir = parent_path if folder is None else parent_path / folder
    if folder is not None:
        target_dir.mkdir(exist_ok=True, parents=True)

    fname = file if file is not None else "untitled"
    result_path = target_dir / f"{fname}{ext}"

    if data is None or data.operation is None:
        result_path.touch(exist_ok=True)
        return result_path

    return data.operation(result_path, data.content)


# ── Writers ────────────────────────────────────────────────────────────────


def write_text(path: Path, content: Any) -> Path:
    """Write string content as UTF-8 text."""
    path.write_text(str(content), encoding="utf-8")
    return path


def write_json(path: Path, content: Any) -> Path:
    """Serialise *content* as pretty-printed JSON."""
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_bytes(path: Path, content: Any) -> Path:
    """Write raw bytes."""
    path.write_bytes(content)
    return path
