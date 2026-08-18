"""Database tools for agent use."""

import sqlite3
from pathlib import Path
from typing import Any


def run_db_query(path: Path, query: str) -> Any:
    """Execute a single SQL statement against an SQLite database.

    Args:
        path: Path to the ``.db`` file (created if it doesn't exist).
        query: SQL statement to execute.

    Returns:
        The result of ``cursor.fetchall()``.
    """
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        return cur.fetchall()
    finally:
        conn.close()
