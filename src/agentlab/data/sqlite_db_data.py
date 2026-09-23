"""SQLite-backed LangGraph checkpoint persistence shared by the CLI apps."""

import sqlite3
from contextlib import closing
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore

from agentlab.configs.paths_config import CHECKPOINT_DB_PATH


def get_sqlite_checkpointer(db_path: Path = CHECKPOINT_DB_PATH) -> SqliteSaver:
    """Open a process-lifetime SQLite connection and wrap it in a ``SqliteSaver``.

    The saver owns the connection until the process exits. ``check_same_thread``
    is off because LangGraph may write checkpoints from worker threads.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    return SqliteSaver(conn)


def get_sqlite_store(db_path: Path) -> SqliteStore:
    """Open a process-lifetime SQLite long-term store, creating its tables on first use.

    ``check_same_thread`` is off because the store is used from background threads too; the
    store serializes access with its own lock.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    store = SqliteStore(
        sqlite3.connect(str(db_path), check_same_thread=False, isolation_level=None),
    )
    store.setup()
    return store


def get_recent_threads(
    limit: int | None = None,
    db_path: Path = CHECKPOINT_DB_PATH,
) -> list[str]:
    """Return distinct thread IDs ordered by their latest checkpoint, newest first."""
    if not db_path.exists():
        return []
    query = (
        "SELECT thread_id, MAX(checkpoint_id) AS latest "
        "FROM checkpoints GROUP BY thread_id ORDER BY latest DESC"
    )
    params: tuple[int, ...] = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (limit,)
    with closing(sqlite3.connect(str(db_path))) as conn:
        try:
            rows = conn.execute(query, params).fetchall()
        except sqlite3.OperationalError:  # database exists but has no checkpoints yet
            return []
    return [row[0] for row in rows]
