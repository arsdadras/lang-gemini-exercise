"""Thread / conversation ID management."""

import uuid
from pathlib import Path

_THREAD_FILE = Path(__file__).resolve().parent.parent / "last_threads.txt"


def get_thread_id(*, thread_file: Path = _THREAD_FILE) -> str:
    """Return an existing thread ID or generate a new one.

    If a thread file exists the user is prompted to reuse the previous ID.
    Otherwise a fresh UUID4 is generated, persisted, and returned.

    Args:
        thread_file: Path to the file storing the last thread ID.
    """
    if thread_file.exists():
        current_id = thread_file.read_text().strip()
        choice = input(f"Run in same thread with id:{current_id}? (y/n): ")
        if choice.strip().lower() == "y":
            return current_id
    new_id = str(uuid.uuid4())
    thread_file.write_text(new_id)
    return new_id
