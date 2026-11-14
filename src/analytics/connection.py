"""Kết nối DuckDB trong bộ nhớ cho phần phân tích và đối soát.

Vì sao không mở thẳng `warehouse/olist.duckdb`: tệp đó bị khóa khi pipeline đang ghi
(runbook, mục "DuckDB bị khóa"). Ở đây ta dựng lại đúng 11 view `v_*` trên các tệp Parquet
trong `data/marts/` — cùng định nghĩa với `DuckDbCatalog` — nên kết quả giống hệt mà chạy
được song song với dashboard. Ngoài ra còn gắn thêm các view `src_*` đọc thẳng CSV gốc để
đối soát "nguồn → kho" bằng một phép tính độc lập với pipeline.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from src.integrate.catalog import VIEW_TABLES

# View nguồn -> tệp CSV gốc trong `dataset/` (bất biến, không bao giờ ghi vào).
SOURCE_FILES: dict[str, str] = {
    "src_orders": "olist_orders_dataset.csv",
    "src_order_items": "olist_order_items_dataset.csv",
    "src_payments": "olist_order_payments_dataset.csv",
    "src_reviews": "olist_order_reviews_dataset.csv",
}


def _quoted(path: Path) -> str:
    return path.as_posix().replace("'", "''")


def open_analysis_connection(config, *, with_sources: bool = True) -> duckdb.DuckDBPyConnection:
    """Mở DuckDB trong bộ nhớ với view `v_*` (mart) và `src_*` (CSV gốc)."""

    missing = [table for table in VIEW_TABLES if not (config.marts_dir / f"{table}.parquet").exists()]
    if missing:
        raise FileNotFoundError(
            f"Thiếu mart {missing} trong {config.marts_dir}. Hãy chạy `python -m src.pipeline run --stage all` trước."
        )

    conn = duckdb.connect(":memory:")
    conn.execute(f"PRAGMA memory_limit='{config.duckdb_memory_limit}'")
    conn.execute(f"PRAGMA threads={config.duckdb_threads}")
    for table in VIEW_TABLES:
        path = _quoted(config.marts_dir / f"{table}.parquet")
        conn.execute(f"CREATE VIEW v_{table} AS SELECT * FROM read_parquet('{path}')")

    if with_sources:
        for view, file_name in SOURCE_FILES.items():
            csv_path = config.raw_csv_dir / file_name
            if not csv_path.exists():
                continue
            # all_varchar: đọc mọi cột dạng chuỗi rồi ép kiểu tường minh trong truy vấn đối soát,
            # để phép tính "từ nguồn" không phụ thuộc cách DuckDB tự đoán kiểu.
            conn.execute(
                f"CREATE VIEW {view} AS "
                f"SELECT * FROM read_csv('{_quoted(csv_path)}', header = true, all_varchar = true)"
            )
    return conn


def available_views(conn: duckdb.DuckDBPyConnection) -> set[str]:
    """Tên các bảng/view đang có trong kết nối (kể cả DataFrame đã `register`)."""

    rows = conn.execute("SELECT table_name FROM information_schema.tables").fetchall()
    return {row[0] for row in rows}
