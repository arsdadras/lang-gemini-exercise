"""Tests for file and DB tools."""

from pathlib import Path

from tools import FileData, create_file, write_json, write_text
from tools.db_ops import run_db_query


def test_create_empty_file(tmp_path: Path) -> None:
    result = create_file(file="test_note", base_dir=tmp_path)
    assert result.exists()
    assert result.name == "test_note.md"


def test_create_file_in_subfolder(tmp_path: Path) -> None:
    result = create_file(folder="sub", file="doc", base_dir=tmp_path)
    assert result.exists()
    assert result.parent.name == "sub"


def test_create_file_with_write_text(tmp_path: Path) -> None:
    data = FileData(content="hello world", operation=write_text)
    result = create_file(
        file="greeting", extension=".txt", data=data, base_dir=tmp_path
    )
    assert result.read_text() == "hello world"


def test_write_json(tmp_path: Path) -> None:
    target = tmp_path / "data.json"
    write_json(target, {"key": "value"})
    assert target.exists()
    assert '"key"' in target.read_text()


def test_run_db_query_creates_table(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    run_db_query(db_path, "CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)")
    rows = run_db_query(db_path, "SELECT name FROM sqlite_master WHERE type='table'")
    assert ("t",) in rows
