"""Unit test cho tầng `stats` trong pipeline và bộ `choices` của CLI (FR5.1, BR1.11, BR2.8)."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import pytest

from src.analytics import statistics as statistics_module
from src.analytics.model import train_from_frame
from src.analytics.report import (
    REPORT_VERSION,
    AnalysisReport,
    ModelBlock,
    read_report,
    report_path,
    write_report,
)
from src.analytics.statistics import PREVIOUS_REPORT_UNREADABLE_EVENT, build_analysis_report
from src.analytics.service import AnalyticsService
from src.pipeline import stages as stages_module
from src.pipeline.cli import build_parser
from src.pipeline.stages import STAGES, run_stage

ORDERS_SQL = """
    CREATE OR REPLACE VIEW v_fact_orders AS
    SELECT 'o' || CAST(i AS VARCHAR) AS order_id,
           'c' || CAST(i AS VARCHAR) AS customer_id,
           strftime(DATE '2016-09-01' + INTERVAL (i % 730) DAY, '%Y-%m-%d') AS date_key,
           TRUE AS is_delivered,
           (i % 10) = 0 AS is_late,
           TRUE AS has_items,
           TRUE AS has_payment,
           'delivered' AS order_status,
           DATE '2016-09-01' + INTERVAL (i % 730) DAY + INTERVAL 1 DAY AS order_approved_at,
           DATE '2016-09-01' + INTERVAL (i % 730) DAY + INTERVAL 3 DAY AS order_delivered_carrier_date
    FROM range(1, 731) AS t(i)
"""

CUSTOMERS_SQL = """
    CREATE OR REPLACE VIEW v_dim_customer AS
    SELECT 'c' || CAST(i AS VARCHAR) AS customer_id,
           CASE i % 3 WHEN 0 THEN 'SP' WHEN 1 THEN 'RJ' ELSE 'BA' END AS state,
           CASE i % 3 WHEN 2 THEN 'Nordeste' ELSE 'Sudeste' END AS region
    FROM range(1, 731) AS t(i)
"""

ITEMS_SQL = """
    CREATE OR REPLACE VIEW v_fact_order_items AS
    SELECT 'o' || CAST(i AS VARCHAR) AS order_id,
           CAST(1 AS INTEGER) AS order_item_id,
           'c' || CAST(i AS VARCHAR) AS customer_id,
           'p' || CAST((i % 20) AS VARCHAR) AS product_id,
           's1' AS seller_id,
           strftime(DATE '2016-09-01' + INTERVAL (i % 730) DAY, '%Y-%m-%d') AS date_key,
           CAST(10 + (i % 90) AS DOUBLE) AS price,
           CAST(1 + (i % 7) AS DOUBLE) AS freight_value,
           CAST(11 + (i % 90) AS DOUBLE) AS item_total,
           'delivered' AS order_status,
           TRUE AS is_delivered,
           'SP' AS seller_state
    FROM range(1, 731) AS t(i)
"""

DATES_SQL = """
    CREATE OR REPLACE VIEW v_dim_date AS
    SELECT DISTINCT date_key,
           CAST(strftime('%Y', CAST(date_key AS DATE)) AS INTEGER) AS year,
           CAST(strftime('%m', CAST(date_key AS DATE)) AS INTEGER) AS month,
           CAST(strftime('%w', CAST(date_key AS DATE)) AS INTEGER) AS weekday,
           FALSE AS is_sparse_period
    FROM v_fact_orders
"""

PAYMENTS_SQL = """
    CREATE OR REPLACE VIEW v_fact_payments AS
    SELECT 'o' || CAST(i AS VARCHAR) AS order_id,
           CAST(1 AS INTEGER) AS payment_sequential,
           'credit_card' AS payment_type,
           CAST(1 + (i % 6) AS INTEGER) AS payment_installments,
           CAST(10.0 AS DOUBLE) AS payment_value
    FROM range(1, 731) AS t(i)
"""

PRODUCTS_SQL = """
    CREATE OR REPLACE VIEW v_dim_product AS
    SELECT 'p' || CAST(i AS VARCHAR) AS product_id, 'cat' AS category
    FROM range(0, 20) AS t(i)
"""

REVIEWS_SQL = """
    CREATE OR REPLACE VIEW v_fact_reviews AS
    SELECT CAST(NULL AS VARCHAR) AS order_id, CAST(NULL AS DOUBLE) AS review_score
    WHERE FALSE
"""


def build_mart(config) -> Path:
    """Dựng mart 24 tháng trong DuckDB tạm: 730 đơn đã giao, ba bang, hai vùng, có thanh toán."""

    config.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(config.duckdb_path))
    try:
        for statement in (
            ORDERS_SQL,
            CUSTOMERS_SQL,
            ITEMS_SQL,
            DATES_SQL,
            PRODUCTS_SQL,
            REVIEWS_SQL,
            PAYMENTS_SQL,
        ):
            conn.execute(statement)
    finally:
        conn.close()
    return config.duckdb_path


class CapturingLogger:
    """Ghi lại sự kiện để khẳng định dòng cảnh báo của BR1.11."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def info(self, event, **fields):
        self.events.append({"event": event, **fields})

    def warning(self, event, **fields):
        self.events.append({"event": event, **fields})

    def error(self, event, error_code, **fields):
        self.events.append({"event": event, "error_code": error_code, **fields})


def test_stages_lists_stats_after_the_four_existing_stages():
    assert STAGES == ("ingest", "clean", "integrate", "analyze", "stats")


def test_run_stage_rejects_a_name_outside_the_stage_list(config):
    with pytest.raises(ValueError):
        run_stage(config, "model")


def test_argparse_accepts_the_stats_stage():
    args = build_parser().parse_args(["run", "--stage", "stats"])

    assert args.stage == "stats"


def test_argparse_choices_mirror_the_stage_list():
    parser = build_parser()
    subparsers = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    stage_action = next(action for action in subparsers.choices["run"]._actions if action.dest == "stage")

    assert set(stage_action.choices) == set(STAGES) | {"all"}


def test_parser_keeps_three_subcommands():
    parser = build_parser()
    subparsers = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))

    assert sorted(subparsers.choices) == ["micro-batch", "replay", "run"]


def test_argparse_rejects_a_stage_outside_choices():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["run", "--stage", "model"])


def small_model(config, logger=None):
    """Huấn luyện thật trên mart tạm 730 đơn: cùng đường mã, chỉ khác cỡ mẫu kỳ vọng (BR2.1)."""

    frame, counts = AnalyticsService(config).training_frame()
    return train_from_frame(
        frame, expected_delivered=730, expected_late=73, logger=logger, cohort_counts=counts
    )


def small_fitted(config, logger=None):
    """Đóng gói mô hình nhỏ trên mart tạm (C2b): cùng đường mã, chỉ khác cỡ mẫu."""

    from sklearn.preprocessing import StandardScaler

    from src.analytics.model import (
        NUMERIC_FEATURES,
        _categories,
        build_feature_frame,
        encode_features,
        split_frame,
    )
    from src.analytics.persistence import fit_persistable

    frame, _ = AnalyticsService(config).training_frame()
    train_rows, _ = split_frame(frame)
    features = build_feature_frame(train_rows)
    matrix, _ = encode_features(features, features)
    scaler = StandardScaler().fit(features[list(NUMERIC_FEATURES)].astype("float64"))
    return fit_persistable(
        matrix,
        train_rows["is_late"].fillna(value=False).astype(bool),
        categories=_categories(features),
        scaler_means=list(scaler.mean_),
        scaler_scales=list(scaler.scale_),
    )


def test_stats_stage_writes_a_report_with_all_five_tests(config, monkeypatch):
    build_mart(config)
    monkeypatch.setattr(stages_module, "train_model", small_model)
    monkeypatch.setattr(stages_module, "fit_from_config", small_fitted)

    summary = run_stage(config, "stats")

    assert summary.success is True
    assert [stage.stage for stage in summary.stages] == ["stats"]
    view = read_report(report_path(config))
    # U2 chạy trong cùng tầng nên tệp đủ cả hai khối (BR2.8).
    assert view.status == "day-du"
    assert view.missing == ()
    block = view.report.stats
    assert block.late_rate.total == 730
    assert block.late_rate.successes == 73
    assert len(block.comparisons) == 1
    assert block.comparisons[0].excluded == 0
    assert block.correlation.n == 730
    assert block.group_test.dof == 1
    assert len(block.seasonal.months) == 24
    assert block.skipped == []
    model = view.report.model
    assert model.target == "is_late"
    assert model.counts["flagged"] + model.counts["not_flagged"] == model.counts["total"]
    assert model.counts["total"] == model.split["test_n"]


def test_stats_stage_runs_the_model_step_after_the_stats_step(config, monkeypatch):
    build_mart(config)
    order: list[str] = []
    collect = statistics_module.collect_stats

    def recording_collect(*args, **kwargs):
        order.append("stats")
        return collect(*args, **kwargs)

    def recording_train(*args, **kwargs):
        order.append("model")
        return small_model(config)

    monkeypatch.setattr(statistics_module, "collect_stats", recording_collect)
    monkeypatch.setattr(stages_module, "train_model", recording_train)
    monkeypatch.setattr(stages_module, "fit_from_config", small_fitted)

    run_stage(config, "stats")

    assert order == ["stats", "model"]
    view = read_report(report_path(config))
    assert view.status == "day-du"
    assert view.report.stats is not None
    assert view.report.stats.late_rate.total == 730


def test_stats_stage_keeps_the_model_block_of_the_other_unit(config, monkeypatch):
    build_mart(config)
    monkeypatch.setattr(stages_module, "train_model", small_model)
    monkeypatch.setattr(stages_module, "fit_from_config", small_fitted)
    report_path(config).unlink(missing_ok=True)
    write_report(
        config,
        AnalysisReport(
            version=REPORT_VERSION,
            generated_at="2026-11-10T00:00:00+00:00",
            stats=None,
            model=ModelBlock(target="is_late"),
        ),
    )

    run_stage(config, "stats")

    view = read_report(report_path(config))
    assert view.status == "day-du"
    assert view.report.model.target == "is_late"
    assert view.report.model.split["test_n"] > 0
    assert view.report.stats is not None


def test_build_report_warns_and_drops_the_model_when_the_old_file_is_unreadable(config):
    build_mart(config)
    report_path(config).write_text("{hỏng", encoding="utf-8")
    logger = CapturingLogger()

    report = build_analysis_report(config, generated_at="2026-11-10T00:00:00+00:00", logger=logger)

    assert report.model is None
    assert report.stats is not None
    assert report.version == REPORT_VERSION
    assert any(event["event"] == PREVIOUS_REPORT_UNREADABLE_EVENT for event in logger.events)
