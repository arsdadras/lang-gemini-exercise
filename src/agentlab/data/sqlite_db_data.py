"""SQLite-backed LangGraph checkpoint persistence for the CLI apps, one database per app."""

import sqlite3
from contextlib import closing
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore


def get_sqlite_checkpointer(db_path: Path) -> SqliteSaver:
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


def get_recent_threads(db_path: Path, limit: int | None = None) -> list[str]:
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


def prune_checkpoints(db_path: Path, *, keep_latest: int = 20) -> int:
    """Delete checkpoints older than the ``keep_latest`` newest per thread; return deleted count."""
    if keep_latest < 1:
        msg = f"keep_latest must be >= 1, got {keep_latest}"
        raise ValueError(msg)
    if not db_path.exists():
        return 0
    with closing(sqlite3.connect(str(db_path))) as conn:
        try:
            threads = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT thread_id FROM checkpoints"
                ).fetchall()
            ]
        except sqlite3.OperationalError:
            return 0
        deleted = 0
        for thread_id in threads:
            old_ids = [
                row[0]
                for row in conn.execute(
                    "SELECT DISTINCT checkpoint_id FROM checkpoints "
                    "WHERE thread_id = ? ORDER BY checkpoint_id DESC LIMIT -1 OFFSET ?",
                    (thread_id, keep_latest),
                ).fetchall()
            ]
            if not old_ids:
                continue
            placeholders = ",".join("?" for _ in old_ids)
            params = (thread_id, *old_ids)
            with conn:
                cur = conn.execute(
                    f"DELETE FROM checkpoints WHERE thread_id = ? AND checkpoint_id IN ({placeholders})",
                    params,
                )
                deleted += max(cur.rowcount, 0)
                try:
                    conn.execute(
                        f"DELETE FROM writes WHERE thread_id = ? AND checkpoint_id IN ({placeholders})",
                        params,
                    )
                except sqlite3.OperationalError:
                    pass
    return deleted
