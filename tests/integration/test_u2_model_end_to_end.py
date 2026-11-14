"""End-to-end U2 trên dữ liệu thật: grain dòng hàng, 14 đặc trưng, báo cáo v3, tệp mô hình."""

from __future__ import annotations

import time

import pytest

from src.analytics.model import (
    EXPECTED_DELIVERED,
    EXPECTED_LATE,
    FEATURES,
    FORBIDDEN_COLUMNS,
    MODEL_DIGITS,
    SPLIT_DATE,
    TARGET,
    THRESHOLD_METHOD,
    build_feature_frame,
    delivered_population,
    train_model,
)
from src.analytics.persistence import load_model
from src.analytics.report import read_report, report_path
from src.analytics.service import AnalyticsService
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.ingest.reader import ingest_all
from src.integrate.pipeline import integrate_all
from src.pipeline.stages import run_stage

# NFR1.1 — tầng `stats`; NFR2.1 — toàn bộ bước mô hình nằm trong đó, gồm cả lượt đọc mart.
STAGE_BUDGET_SECONDS = 300
TRAIN_BUDGET_SECONDS = 240


@pytest.mark.slow
def test_u2_model_end_to_end(real_config) -> None:  # noqa: ANN001
    run = new_run_context("u2-model", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)

    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    integrate_all(real_config, run, writer, logger, refresh_ibge=False)

    started = time.perf_counter()
    summary = run_stage(real_config, "stats")
    stage_elapsed = time.perf_counter() - started

    assert summary.success is True
    assert stage_elapsed < STAGE_BUDGET_SECONDS

    view = read_report(report_path(real_config))
    assert view.status == "day-du"
    assert view.report.stats is not None
    block = view.report.model
    assert block is not None

    # BR2.1 trên dữ liệu thật: quần thể grain dòng hàng, 110.195 dòng / 96.476 đơn / 8.713 trễ.
    frame, counts = AnalyticsService(real_config).training_frame()
    population = delivered_population(frame, counts["cohort_rows"], counts["late_rows"])
    assert len(population) == EXPECTED_DELIVERED == 110_195
    assert counts["cohort_orders"] == 96_476
    assert int(population[TARGET].astype(bool).sum()) == EXPECTED_LATE == 8_713
    assert counts["excluded_missing_carrier"] == 2

    # BR2.3 trên khung đặc trưng thật: đúng 14 tên, không cột nào chỉ biết sau khi giao.
    features = build_feature_frame(population)
    assert list(features.columns) == list(FEATURES)
    assert set(features.columns) & set(FORBIDDEN_COLUMNS) == set()

    # BR2.2: chia theo order_id, tổng cỡ mẫu khớp quần thể.
    assert block.split["train_end"] < block.split["test_start"]
    assert block.split["test_start"] == SPLIT_DATE
    assert block.split["train_n"] + block.split["test_n"] == 110_195

    # BR2.5–BR2.7, BR2.9 trên khối đã ghi ra tệp.
    assert block.counts["threshold_method"] == THRESHOLD_METHOD
    assert block.counts["flagged"] + block.counts["not_flagged"] == block.counts["total"]
    assert block.counts["total"] == block.split["test_n"]
    assert block.counts["auc_below_target"] is (block.auc < 0.70)
    assert block.unit == "dòng hàng"
    assert block.beats_baseline is (block.auc > block.baseline_auc)
    assert 0 < block.threshold < 1
    for value in (block.auc, block.threshold, block.precision, block.recall, block.baseline_auc):
        assert round(value, MODEL_DIGITS) == value

    # NFR1.1/NFR2.1: bước mô hình đo riêng, vẫn trong ngân sách.
    model_started = time.perf_counter()
    fresh = train_model(real_config)
    model_elapsed = time.perf_counter() - model_started
    assert model_elapsed < TRAIN_BUDGET_SECONDS

    # BR2.4/AC2.4.6: hai lần chạy cùng dữ liệu cho cùng khối, kể cả `auc_tree`.
    assert fresh.to_dict() == block.to_dict()

    # C2b: tệp mô hình nạp lại được và mang đúng danh sách cột đã huấn luyện.
    loaded = load_model(real_config.models_dir)
    assert loaded is not None
    assert len(loaded.feature_names) > len(FEATURES)
