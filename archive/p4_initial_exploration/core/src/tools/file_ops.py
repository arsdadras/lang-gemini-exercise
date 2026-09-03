"""Sandbox file operation tools with strict path confinement."""

from pathlib import Path

from configs.interpreter import DEFAULT_SANDBOX_DIR
from langchain_core.tools import tool
from utils.resolve_safe_path import resolve_safe_path


def make_file_tools(workspace_dir: Path | str | None = None):
    """Create isolated sandbox file tools bound to a specific workspace directory."""
    base_path = Path(workspace_dir) if workspace_dir else DEFAULT_SANDBOX_DIR
    base_path.mkdir(parents=True, exist_ok=True)

    @tool("write_file")
    def write_file(file_path: str, content: str) -> str:
        """Write text content to a file inside the sandboxed workspace.

        Args:
            file_path: Relative file path inside the sandbox (e.g. 'reports/summary.txt').
            content: The text content to write into the file.
        """
        try:
            target = resolve_safe_path(base_path, file_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} characters to '{file_path}'."
        except Exception as e:  # noqa: BLE001
            return f"Error writing file: {e}"

    @tool("read_file")
    def read_file(file_path: str) -> str:
        """Read text content from a file inside the sandboxed workspace.

        Args:
            file_path: Relative file path inside the sandbox to read.
        """
        try:
            target = resolve_safe_path(base_path, file_path)
            if not target.exists():
                return f"Error: File '{file_path}' does not exist."
            if not target.is_file():
                return f"Error: '{file_path}' is a directory, not a file."
            return target.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            return f"Error reading file: {e}"

    @tool("list_files")
    def list_files(directory: str = ".") -> str:
        """List files and subdirectories located inside the sandboxed workspace.

        Args:
            directory: Subdirectory to list, relative to workspace root (default: '.').
        """
        try:
            target = resolve_safe_path(base_path, directory)
            if not target.exists():
                return f"Directory '{directory}' does not exist."
            if not target.is_dir():
                return f"'{directory}' is not a directory."

            base_resolved = base_path.resolve()
            items = []
            for item in sorted(target.iterdir()):
                rel = item.relative_to(base_resolved)
                kind = "DIR " if item.is_dir() else "FILE"
                items.append(f"[{kind}] {rel}")

            if not items:
                return f"Workspace directory '{directory}' is empty."
            return "\n".join(items)
        except Exception as e:  # noqa: BLE001
            return f"Error listing files: {e}"

    return write_file, read_file, list_files


# Default singleton file tools for default sandbox directory
write_file, read_file, list_files = make_file_tools()
