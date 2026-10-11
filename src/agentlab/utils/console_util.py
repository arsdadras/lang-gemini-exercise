"""Console helpers for the CLI apps."""

import contextlib
import io
import sys


def configure_utf8_stdout() -> None:
    """Switch stdout to UTF-8 so model output can't crash a cp1252 Windows console."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        with contextlib.suppress(io.UnsupportedOperation):
            reconfigure(encoding="utf-8")
