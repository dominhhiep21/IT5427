"""Rewrite and run the mediated "số đơn theo tháng" query on the source tables."""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterable
from dataclasses import dataclass

import duckdb
import pandas as pd

from src.common.exceptions import QueryExecutionError, SchemaError
from src.common.logging import NullLogger
from src.integration.models import (
    STATUS_VALUES,
    DonHang,
    QueryRunResult,
    RewriteStep,
)
from src.integration.schema import EntityMapping

TEMPLATE_ID = "don-theo-thang"
TEMPLATE_TITLE = "Số đơn theo tháng"
MONTHS_WINDOW = 12
SLOW_QUERY_MS = 2000

MEDIATED_QUERY_TEXT = (
    "SELECT thang(ngay_dat) AS thang, trang_thai, count(ma_don) AS so_don "
    "FROM don_hang GROUP BY thang, trang_thai"
)

SOURCE_TABLE = "olist_orders_dataset"

# Tên cột nguồn chỉ lấy từ dict hằng này, không ghép từ tham số hàm.
MEDIATED_TO_SOURCE: dict[str, str] = {
    "ma_don": "order_id",
    "ngay_dat": "order_purchase_timestamp",
    "trang_thai": "order_status",
}

SOURCE_SQL = (
    "SELECT strftime(order_purchase_timestamp, '%Y-%m') AS thang, "
    "order_status AS trang_thai, COUNT(order_id) AS so_don "
    f"FROM {SOURCE_TABLE} "
    "GROUP BY thang, trang_thai ORDER BY thang, trang_thai"
)


@dataclass(frozen=True)
class RewritePlan:
    """The mediated-to-source rewrite plan of one query."""

    plan_id: str
    steps: tuple[RewriteStep, ...]


def validate_mediated_query(text: str) -> None:
    """BR1.4: refuse a query that does not state the order status."""

    lowered = (text or "").lower()
    if "don_hang" not in lowered:
        raise QueryExecutionError("Truy vấn phải đọc từ thực thể don_hang.")
    if "trang_thai" not in lowered:
        raise QueryExecutionError("Truy vấn đếm đơn phải nêu rõ trạng thái đang đếm (thiếu trang_thai).")
    if "group by" not in lowered:
        raise QueryExecutionError("Truy vấn đếm đơn phải nhóm theo tháng và trạng thái (thiếu GROUP BY).")


def rewrite_plan(entity: EntityMapping, mediated_query: str = MEDIATED_QUERY_TEXT) -> RewritePlan:
    """BR1.6: build the source rewrite plan before anything is executed."""

    validate_mediated_query(mediated_query)
    for field_name, column in MEDIATED_TO_SOURCE.items():
        mapped = entity.field(field_name)
        if mapped.source_table != SOURCE_TABLE or mapped.source_column != column:
            raise SchemaError(
                f"Lược đồ ánh xạ {field_name!r} tới "
                f"{mapped.source_table}.{mapped.source_column}, "
                f"nhưng truy vấn mẫu cần {SOURCE_TABLE}.{column}."
            )
    return RewritePlan(
        plan_id=f"plan-{uuid.uuid4().hex[:12]}",
        steps=(RewriteStep(step=1, mediated_entity=entity.name, source_table=SOURCE_TABLE),),
    )


def _source_frame(orders: Iterable[DonHang] | pd.DataFrame) -> pd.DataFrame:
    if isinstance(orders, pd.DataFrame):
        return orders
    records = [
        {
            MEDIATED_TO_SOURCE["ma_don"]: order.ma_don,
            MEDIATED_TO_SOURCE["ngay_dat"]: order.ngay_dat,
            MEDIATED_TO_SOURCE["trang_thai"]: order.trang_thai,
        }
        for order in orders
    ]
    return pd.DataFrame(records, columns=list(MEDIATED_TO_SOURCE.values()))


def _shift_month(month: str, delta: int) -> str:
    year, number = (int(part) for part in month.split("-"))
    offset = year * 12 + (number - 1) + delta
    return f"{offset // 12:04d}-{offset % 12 + 1:02d}"


def _completeness(records: list[dict[str, object]]) -> tuple[list[str], list[str]]:
    """BR1.7 + BR1.8: keep 12 months from the newest, name what is missing."""

    present = sorted({str(record["thang"]) for record in records})
    if not present:
        return [], []
    newest = present[-1]
    window = [_shift_month(newest, -offset) for offset in range(MONTHS_WINDOW - 1, -1, -1)]
    in_window = [month for month in present if month >= window[0]]
    missing_months = [month for month in window if month not in in_window]
    statuses = {str(record["trang_thai"]) for record in records if str(record["thang"]) >= window[0]}
    partial = [f"thiếu tháng {month}" for month in missing_months]
    partial += [f"thiếu trạng thái {status}" for status in sorted(STATUS_VALUES - statuses)]
    return in_window, partial


def run_monthly_orders(
    orders: Iterable[DonHang] | pd.DataFrame,
    plan: RewritePlan | None,
    logger=None,
) -> QueryRunResult:
    """Run the rewritten query on an in-memory DuckDB connection."""

    logger = logger or NullLogger()
    if plan is None or not plan.steps:
        raise QueryExecutionError("Truy vấn chưa được viết lại thành SQL nguồn; không thực thi.")

    frame = _source_frame(orders)
    started = time.perf_counter()
    records: list[dict[str, object]] = []
    if not frame.empty:
        logger.info(
            "integration.query.started",
            plan_id=plan.plan_id,
            template_id=TEMPLATE_ID,
            source_sql=SOURCE_SQL,
        )
        connection = duckdb.connect()
        try:
            connection.register(SOURCE_TABLE, frame)
            try:
                rows = connection.execute(SOURCE_SQL).fetchall()
            except duckdb.Error as exc:
                logger.error(
                    "integration.query.failed",
                    "sql_error",
                    plan_id=plan.plan_id,
                    message=str(exc)[:200],
                )
                raise QueryExecutionError(f"Truy vấn nguồn lỗi: {exc}") from exc
        finally:
            connection.close()
        records = [{"thang": str(row[0]), "trang_thai": str(row[1]), "so_don": int(row[2])} for row in rows]

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    months, partial = _completeness(records)
    result = QueryRunResult(
        plan_id=plan.plan_id,
        template_id=TEMPLATE_ID,
        template_title=TEMPLATE_TITLE,
        mediated_query_text=MEDIATED_QUERY_TEXT,
        rewrite_plan=list(plan.steps),
        source_sql=SOURCE_SQL,
        rows=records,
        row_count=len(records),
        elapsed_ms=elapsed_ms,
        total_orders=sum(int(record["so_don"]) for record in records),
        months=months,
        partial=partial,
    )
    logger.info(
        "integration.query.completed",
        plan_id=plan.plan_id,
        row_count=result.row_count,
        elapsed_ms=elapsed_ms,
    )
    if elapsed_ms > SLOW_QUERY_MS:
        logger.warning("integration.query.slow", plan_id=plan.plan_id, elapsed_ms=elapsed_ms)
    return result
