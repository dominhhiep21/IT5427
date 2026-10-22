"""DuckDB connection factory."""

from __future__ import annotations

from pathlib import Path

import duckdb


class ConnectionFactory:
    def __init__(self, config) -> None:
        self.config = config
        self.config.duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    def _configure(self, conn: duckdb.DuckDBPyConnection) -> None:
        conn.execute(f"PRAGMA memory_limit='{self.config.duckdb_memory_limit}'")
        conn.execute(f"PRAGMA threads={self.config.duckdb_threads}")

    def write(self) -> duckdb.DuckDBPyConnection:
        conn = duckdb.connect(str(self.config.duckdb_path), read_only=False)
        self._configure(conn)
        return conn

    def read_only(self) -> duckdb.DuckDBPyConnection:
        conn = duckdb.connect(str(self.config.duckdb_path), read_only=True)
        try:
            self._configure(conn)
        except Exception:
            pass
        return conn
