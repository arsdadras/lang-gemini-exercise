from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SANDBOX_DIR = PROJECT_ROOT / "out" / "sandbox"



def resolve_safe_path(base_dir: Path, target_str: str) -> Path:
    """Resolve target path and enforce confinement within base_dir."""
    base_resolved = base_dir.resolve()
    clean_target = target_str.lstrip("/\\")
    resolved_target = (base_resolved / clean_target).resolve()

    if not resolved_target.is_relative_to(base_resolved):
        msg = (
            f"Security Error: Access denied to '{target_str}'. Path escapes"
            " sandbox workspace."
        )
        raise PermissionError(msg)

    return resolved_target


# Backward compatibility alias
_resolve_safe_path = resolve_safe_path

