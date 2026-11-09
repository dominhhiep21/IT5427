"""Unit tests for the mediated "số đơn theo tháng" query and its rewrite."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from src.common.exceptions import QueryExecutionError, SchemaError
from src.common.logging import JsonLogger, new_run_context
from src.config import load_config
from src.integration import query as query_module
from src.integration.models import STATUS_VALUES, DonHang
from src.integration.schema import load_schema

ROOT = Path(__file__).resolve().parents[2]

SCHEMA_YAML = """
schema_kind: GAV
entities:
  - name: don_hang
    description: Một dòng cho mỗi đơn hàng
    source_tables:
      - olist_orders_dataset
      - olist_customers_dataset
    fields:
      - field_name: ma_don
        source_table: olist_orders_dataset
        source_column: order_id
        data_type: string
        loaded: true
      - field_name: ngay_dat
        source_table: olist_orders_dataset
        source_column: order_purchase_timestamp
        data_type: timestamp
        loaded: true
      - field_name: trang_thai
        source_table: olist_orders_dataset
        source_column: order_status
        data_type: string
        loaded: true
      - field_name: ma_khach
        source_table: olist_orders_dataset
        source_column: customer_id
        data_type: string
        loaded: true
      - field_name: bang_giao
        source_table: olist_customers_dataset
        source_column: customer_state
        data_type: string
        loaded: false
"""


def _entity(tmp_path: Path):
    path = tmp_path / "mediated-schema.yaml"
    path.write_text(SCHEMA_YAML, encoding="utf-8")
    return load_schema(path).entity("don_hang")


def _tmp_log_config(tmp_path: Path):
    config_path = tmp_path / "logs-config.yaml"
    dataset = tmp_path / "dataset"
    dataset.mkdir(exist_ok=True)
    config_path.write_text(
        f"""
paths:
  raw_csv_dir: "{dataset.as_posix()}"
  data_dir: data
  logs_dir: logs
  temp_dir: data/.tmp
""",
        encoding="utf-8",
    )
    return load_config(config_path)


def _logger(config) -> JsonLogger:
    run = new_run_context("integration", config.logs_dir, config.temp_dir)
    return JsonLogger(run, console=False)


def _orders(rows: list[tuple[str, datetime, str]]) -> list[DonHang]:
    return [
        DonHang(
            ma_don=ma_don,
            ngay_dat=ngay_dat,
            trang_thai=trang_thai,
            ma_khach="c1",
        )
        for ma_don, ngay_dat, trang_thai in rows
    ]


def _month_starts(count: int, start_year: int = 2017, start_month: int = 1) -> list[datetime]:
    stamps = []
    for index in range(count):
        offset = start_year * 12 + (start_month - 1) + index
        stamps.append(datetime(offset // 12, offset % 12 + 1, 15))
    return stamps


def _full_window(statuses: tuple[str, ...] = tuple(sorted(STATUS_VALUES))) -> list:
    rows = []
    for month_index in range(12):
        year = 2017 + (month_index // 12)
        month = month_index + 1
        for status in statuses:
            rows.append(
                (
                    f"o-{month_index}-{status}",
                    datetime(year, month, 10),
                    status,
                )
            )
    return rows


def test_query_without_status_condition_is_rejected():
    with pytest.raises(QueryExecutionError):
        query_module.validate_mediated_query("SELECT count(ma_don) AS so_don FROM don_hang GROUP BY thang")


def test_query_without_group_by_is_rejected():
    with pytest.raises(QueryExecutionError):
        query_module.validate_mediated_query("SELECT trang_thai, count(ma_don) FROM don_hang")


def test_rewrite_plan_maps_don_hang_to_the_orders_table(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))

    assert len(plan.steps) == 1
    step = plan.steps[0]
    assert step.mediated_entity == "don_hang"
    assert step.source_table == "olist_orders_dataset"
    assert step.join_condition == ""


def test_rewritten_sql_uses_the_three_source_columns_without_join(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    result = query_module.run_monthly_orders(_orders([("o1", datetime(2017, 1, 5), "delivered")]), plan)

    sql = result.source_sql.upper()
    assert "OLIST_ORDERS_DATASET" in sql
    assert "ORDER_PURCHASE_TIMESTAMP" in sql
    assert "ORDER_STATUS" in sql
    assert "ORDER_ID" in sql
    assert "JOIN" not in sql


def test_run_requires_a_rewrite_plan(monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("không được mở DuckDB khi thiếu kế hoạch viết lại")

    monkeypatch.setattr(query_module.duckdb, "connect", explode)
    with pytest.raises(QueryExecutionError):
        query_module.run_monthly_orders(_orders([("o1", datetime(2017, 1, 5), "delivered")]), None)


def test_result_has_one_row_per_month_and_status(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    orders = _orders(
        [
            ("o1", datetime(2018, 8, 1), "delivered"),
            ("o2", datetime(2018, 8, 2), "delivered"),
            ("o3", datetime(2018, 8, 3), "shipped"),
        ]
    )

    result = query_module.run_monthly_orders(orders, plan)

    assert result.row_count == 2
    assert result.rows[0]["thang"] == "2018-08"
    counts = {row["trang_thai"]: row["so_don"] for row in result.rows}
    assert counts == {"delivered": 2, "shipped": 1}


def test_total_orders_equals_the_sum_of_rows(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    orders = _orders(
        [
            ("o1", datetime(2018, 8, 1), "delivered"),
            ("o2", datetime(2018, 7, 1), "shipped"),
            ("o3", datetime(2018, 7, 4), "shipped"),
        ]
    )

    result = query_module.run_monthly_orders(orders, plan)

    assert result.total_orders == 3
    assert result.total_orders == sum(row["so_don"] for row in result.rows)


def test_months_are_the_twelve_latest_from_the_newest_month(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    orders = _orders([(f"o{index}", stamp, "delivered") for index, stamp in enumerate(_month_starts(14))])

    result = query_module.run_monthly_orders(orders, plan)

    assert len(result.months) == 12
    assert result.months[0] == "2017-03"
    assert result.months[-1] == "2018-02"


def test_row_count_and_elapsed_ms_are_present(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    result = query_module.run_monthly_orders(_orders([("o1", datetime(2018, 8, 1), "delivered")]), plan)

    assert result.row_count == len(result.rows)
    assert result.elapsed_ms >= 0


def test_result_carries_template_and_plan_ids(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    result = query_module.run_monthly_orders(_orders([("o1", datetime(2018, 8, 1), "delivered")]), plan)

    assert result.plan_id == plan.plan_id
    assert result.template_id == "don-theo-thang"
    assert result.template_title
    assert result.mediated_query_text


def test_result_on_empty_source_is_empty_not_zero(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))

    result = query_module.run_monthly_orders([], plan)

    assert result.rows == []
    assert result.months == []
    assert result.partial == []
    assert result.row_count == 0


def test_run_works_without_a_logger(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))

    result = query_module.run_monthly_orders(_orders([("o1", datetime(2018, 8, 1), "delivered")]), plan)

    assert result.row_count == 1


def test_validate_rejects_a_query_on_another_entity():
    with pytest.raises(QueryExecutionError):
        query_module.validate_mediated_query("SELECT trang_thai FROM outra_tabela GROUP BY trang_thai")


def test_rewrite_plan_rejects_a_schema_with_other_columns(tmp_path: Path):
    path = tmp_path / "mediated-schema.yaml"
    path.write_text(
        SCHEMA_YAML.replace(
            "source_column: order_purchase_timestamp",
            "source_column: order_approved_at",
        ),
        encoding="utf-8",
    )
    entity = load_schema(path).entity("don_hang")

    with pytest.raises(SchemaError):
        query_module.rewrite_plan(entity)


def test_run_accepts_a_prebuilt_source_frame(tmp_path: Path):
    import pandas as pd

    plan = query_module.rewrite_plan(_entity(tmp_path))
    frame = pd.DataFrame(
        [
            {
                "order_id": "o1",
                "order_purchase_timestamp": datetime(2018, 8, 1),
                "order_status": "delivered",
            }
        ]
    )

    result = query_module.run_monthly_orders(frame, plan)

    assert result.total_orders == 1


def test_query_failure_is_wrapped_and_logged(tmp_path: Path, monkeypatch):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    config = _tmp_log_config(tmp_path)
    logger = _logger(config)
    monkeypatch.setattr(query_module, "SOURCE_SQL", "SELECT * FROM bang_khong_ton_tai")

    with pytest.raises(QueryExecutionError):
        query_module.run_monthly_orders(_orders([("o1", datetime(2018, 8, 1), "delivered")]), plan, logger)

    events = [
        json.loads(line)
        for line in logger.run.log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    failed = [event for event in events if event["event"] == "integration.query.failed"]
    assert failed
    assert failed[0]["error_code"] == "sql_error"


def test_slow_query_writes_a_warning(tmp_path: Path, monkeypatch):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    config = _tmp_log_config(tmp_path)
    logger = _logger(config)
    monkeypatch.setattr(query_module, "SLOW_QUERY_MS", -1)

    query_module.run_monthly_orders(_orders([("o1", datetime(2018, 8, 1), "delivered")]), plan, logger)

    events = [
        json.loads(line)
        for line in logger.run.log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(event["event"] == "integration.query.slow" for event in events)


def test_partial_reports_missing_month_and_missing_status(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    orders = _orders(
        [
            ("o1", datetime(2018, 8, 1), "delivered"),
            ("o2", datetime(2018, 6, 1), "delivered"),
        ]
    )

    result = query_module.run_monthly_orders(orders, plan)

    assert "2018-07" in " ".join(result.partial)
    assert "shipped" in " ".join(result.partial)


def test_partial_is_empty_for_a_complete_window(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))

    result = query_module.run_monthly_orders(_orders(_full_window()), plan)

    assert result.partial == []
    assert len(result.months) == 12


def test_query_on_the_full_volume_stays_under_two_seconds(tmp_path: Path):
    plan = query_module.rewrite_plan(_entity(tmp_path))
    rows = []
    for index in range(99_441):
        month = index % 12 + 1
        rows.append(
            (
                f"o{index}",
                datetime(2018, month, index % 28 + 1),
                "delivered",
            )
        )
    orders = _orders(rows)

    result = query_module.run_monthly_orders(orders, plan)

    assert result.elapsed_ms < 2000
    assert result.total_orders == 99_441
