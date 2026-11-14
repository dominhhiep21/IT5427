"""Khung huấn luyện ở grain dòng hàng: khoá ghép, hai cột ngày, bốn bộ đếm (BR2.1)."""

from __future__ import annotations

import duckdb
import pandas as pd
import pytest

from src.analytics.service import AnalyticsService

SCHEMA = """
    CREATE TABLE fact_orders (
        order_id VARCHAR, customer_id VARCHAR, date_key VARCHAR, category VARCHAR,
        order_status VARCHAR, is_delivered BOOLEAN,
        order_delivered_customer_date TIMESTAMP, order_estimated_delivery_date TIMESTAMP,
        delivery_days DOUBLE, is_late BOOLEAN, has_items BOOLEAN, has_payment BOOLEAN,
        has_review BOOLEAN, order_approved_at TIMESTAMP,
        order_delivered_carrier_date TIMESTAMP
    );
    CREATE TABLE fact_order_items (
        order_id VARCHAR, order_item_id BIGINT, customer_id VARCHAR, product_id VARCHAR,
        seller_id VARCHAR, date_key VARCHAR, price DOUBLE, freight_value DOUBLE,
        item_total DOUBLE, price_outlier BOOLEAN, order_status VARCHAR,
        is_delivered BOOLEAN, seller_state VARCHAR
    );
    CREATE TABLE fact_payments (
        order_id VARCHAR, payment_sequential BIGINT, payment_type VARCHAR,
        payment_installments BIGINT, payment_value DOUBLE, date_key VARCHAR
    );
    CREATE TABLE dim_customer (customer_id VARCHAR, state VARCHAR, region VARCHAR);
    CREATE TABLE dim_date (date_key VARCHAR, month VARCHAR, weekday VARCHAR);
"""


def _connection(tmp_path) -> str:
    path = tmp_path / "mart.duckdb"
    con = duckdb.connect(str(path))
    con.execute(SCHEMA)

    orders = [
        # hai món, đủ hai mốc
        ("o1", "c1", "2018-01-10", True, False, "2018-01-11 08:00", "2018-01-13 09:00"),
        # một món, thiếu carrier date -> bị loại
        ("o2", "c1", "2018-01-11", True, False, "2018-01-12 08:00", None),
        # một món, trễ, thiếu approved -> hai cột ngày null
        ("o3", "c2", "2018-02-10", True, True, None, "2018-02-14 10:00"),
    ]
    for order_id, customer, date_key, delivered, late, approved, carrier in orders:
        con.execute(
            "INSERT INTO fact_orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                order_id,
                customer,
                date_key,
                "brinquedos",
                "delivered",
                delivered,
                None,
                None,
                None,
                late,
                True,
                True,
                False,
                approved,
                carrier,
            ],
        )
    items = [
        ("o1", 1, "c1", "p1", "s1", "2018-01-10", 10.0, 1.0, 11.0, False, "delivered", True, "SP"),
        ("o1", 2, "c1", "p2", "s2", "2018-01-10", 20.0, 2.0, 22.0, False, "delivered", True, None),
        ("o2", 1, "c1", "p1", "s1", "2018-01-11", 5.0, 0.5, 5.5, False, "delivered", True, "SP"),
        ("o3", 1, "c2", "p2", "s2", "2018-02-10", 30.0, 3.0, 33.0, False, "delivered", True, "RJ"),
    ]
    for row in items:
        con.execute("INSERT INTO fact_order_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", list(row))
    con.execute("INSERT INTO fact_payments VALUES ('o1', 1, 'credit_card', 3, 33.0, '2018-01-10')")
    con.execute("INSERT INTO fact_payments VALUES ('o3', 1, 'boleto', 1, 33.0, '2018-02-10')")
    con.execute("INSERT INTO dim_customer VALUES ('c1', 'SP', 'Sudeste')")
    con.execute("INSERT INTO dim_customer VALUES ('c2', 'RJ', 'Sudeste')")
    for date_key in ("2018-01-10", "2018-01-11", "2018-02-10"):
        con.execute("INSERT INTO dim_date VALUES (?, '2018-01', '2')", [date_key])
    for base in ("fact_orders", "fact_order_items", "fact_payments", "dim_customer", "dim_date"):
        con.execute(f"CREATE VIEW v_{base} AS SELECT * FROM {base}")
    con.close()
    return str(path)


def _frame(tmp_path):
    path = _connection(tmp_path)

    class _Config:
        duckdb_path = None
        duckdb_memory_limit = "512MB"
        duckdb_threads = 2

    from pathlib import Path

    _Config.duckdb_path = Path(path)
    return AnalyticsService(_Config()).training_frame()


def test_one_row_per_order_item_pair(tmp_path) -> None:
    frame, _ = _frame(tmp_path)
    assert len(frame) == 3
    assert not frame[["order_id", "order_item_id"]].duplicated().any()


def test_order_id_is_not_unique_at_row_grain(tmp_path) -> None:
    frame, _ = _frame(tmp_path)
    assert frame["order_id"].duplicated().any()


def test_frame_carries_the_new_columns(tmp_path) -> None:
    frame, _ = _frame(tmp_path)
    for column in ("order_item_id", "seller_state", "approval_days", "handling_days"):
        assert column in frame.columns


def test_day_columns_are_whole_days(tmp_path) -> None:
    frame, _ = _frame(tmp_path)
    first = frame.loc[frame["order_id"] == "o1"].iloc[0]
    assert int(first["approval_days"]) == 1
    assert int(first["handling_days"]) == 2


def test_null_milestone_keeps_the_row_with_null_days(tmp_path) -> None:
    frame, _ = _frame(tmp_path)
    third = frame.loc[frame["order_id"] == "o3"].iloc[0]
    # o3 thiếu `order_approved_at`, nên cả hai khoảng ngày đều không xác định — nhưng dòng vẫn còn.
    assert pd.isna(third["approval_days"])
    assert pd.isna(third["handling_days"])
    assert "o3" in set(frame["order_id"])


def test_order_without_carrier_date_is_excluded_and_counted(tmp_path) -> None:
    frame, counts = _frame(tmp_path)
    assert "o2" not in set(frame["order_id"])
    assert counts["excluded_missing_carrier"] == 1


def test_counts_come_from_the_returned_frame(tmp_path) -> None:
    frame, counts = _frame(tmp_path)
    assert counts["cohort_rows"] == len(frame)
    assert counts["cohort_orders"] == frame["order_id"].nunique()
    assert counts["late_rows"] == int(frame["is_late"].sum())


def test_order_level_aggregates_keep_their_meaning(tmp_path) -> None:
    frame, _ = _frame(tmp_path)
    first = frame.loc[frame["order_id"] == "o1"].iloc[0]
    assert int(first["item_count"]) == 2
    assert float(first["item_total"]) == pytest.approx(33.0)
    assert float(first["item_price_max"]) == pytest.approx(20.0)
