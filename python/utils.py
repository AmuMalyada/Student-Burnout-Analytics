"""Shared utilities for the MindPulse analytics project."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_EXTERNAL = PROJECT_ROOT / "data" / "external"
REPORTS = PROJECT_ROOT / "reports"
SQL_DIR = PROJECT_ROOT / "sql"
DB_PATH = DATA_PROCESSED / "mindpulse.sqlite"


def ensure_directories() -> None:
    """Create expected project directories if they do not exist."""
    for path in [DATA_RAW, DATA_PROCESSED, DATA_EXTERNAL, REPORTS, SQL_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def standardize_column_name(column: str) -> str:
    """Convert a source column name to snake_case."""
    column = column.strip().replace("/", "_").replace("\\", "_")
    column = re.sub(r"[^\w\s]", "", column)
    column = re.sub(r"\s+", "_", column)
    column = re.sub(r"_+", "_", column)
    return column.lower().strip("_")


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of a dataframe with standardized snake_case columns."""
    clean = df.copy()
    clean.columns = [standardize_column_name(str(column)) for column in clean.columns]
    return clean


def to_repo_relative(path: Path) -> str:
    """Render a path relative to the project root using forward slashes.

    Keeps machine-specific absolute paths (usernames, local folder layout)
    out of committed report files.
    """
    resolved = Path(path).resolve()
    try:
        relative = resolved.relative_to(PROJECT_ROOT)
    except ValueError:
        return resolved.as_posix()
    return relative.as_posix()


def write_json(payload: dict[str, Any], path: Path) -> None:
    """Write a JSON document using a stable, readable, cross-platform format."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, default=str))
        handle.write("\n")


def read_csv_safely(path: Path) -> pd.DataFrame:
    """Read a CSV file with fallback encodings and delimiter handling."""
    for encoding in ("utf-8", "utf-8-sig", "latin1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, encoding="latin1")


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Persist a dataframe as CSV with consistent LF line endings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")


def connect_database() -> sqlite3.Connection:
    """Open the project SQLite database."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def execute_sql_file(connection: sqlite3.Connection, path: Path) -> None:
    """Execute a SQL script if it exists."""
    if path.exists():
        connection.executescript(path.read_text(encoding="utf-8"))
