"""End-to-end của tầng `stats` trên dữ liệu thật (NFR1.1, NFR1.3, NFR3.4, FR1.1–FR1.5)."""

from __future__ import annotations

import json
import time

import pytest

from src.analytics.report import RATE_DIGITS, REPORT_VERSION, read_report, report_path
from src.analytics.service import AnalyticsService
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.kpis import REVENUE_DEFINITION
from src.common.logging import JsonLogger, new_run_context
from src.common.memory import MemoryProbe
from src.common.types import KpiFilters
from src.ingest.reader import ingest_all
from src.integrate.pipeline import integrate_all
from src.pipeline.stages import run_stage

STAGE_BUDGET_SECONDS = 300


def month_index(label: str) -> int:
    year, month = label.split("-")
    return int(year) * 12 + int(month) - 1


@pytest.mark.slow
def test_u1_stats_end_to_end(real_config):
    run = new_run_context("u1-stats", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)

    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    integrate_all(real_config, run, writer, logger, refresh_ibge=False)

    probe = MemoryProbe()
    probe.reset_peak()
    started = time.perf_counter()
    summary = run_stage(real_config, "stats")
    elapsed = time.perf_counter() - started
    peak_mb = probe.snapshot()

    assert summary.success is True
    assert elapsed < STAGE_BUDGET_SECONDS
    assert peak_mb < real_config.memory_fail_mb

    path = report_path(real_config)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["version"] == REPORT_VERSION

    view = read_report(path)
    # Bước mô hình của U2 chạy trong cùng tầng `stats`, nên tệp đủ cả hai khối (BR2.8).
    assert view.status == "day-du"
    assert view.missing == ()
    assert view.report.model is not None
    block = view.report.stats

    assert block.alpha == 0.05
    assert block.confidence == 1 - block.alpha
    assert block.late_rate.total == 96_478
    assert block.late_rate.successes == 7_826
    # Báo cáo đã làm tròn 4 chữ số khi ghi (BR1.8), nên so với giá trị đã làm tròn.
    assert block.late_rate.rate == round(7_826 / 96_478, RATE_DIGITS)
    assert block.late_rate.ci_low <= block.late_rate.rate <= block.late_rate.ci_high

    assert len(block.comparisons) == 1
    comparison = block.comparisons[0]
    assert comparison.first != comparison.second
    assert comparison.excluded >= 0
    assert comparison.ci_low <= comparison.difference <= comparison.ci_high
    assert comparison.significant == (comparison.p_value < block.alpha)

    # Chỉ dòng hàng của đơn delivered — bộ lọc trạng thái tường minh của `KpiFilters`; 2.453 trong
    # 112.650 dòng hàng thuộc đơn không delivered nên không vào tương quan.
    assert block.correlation.n == 110_197
    assert -1 <= block.correlation.r <= 1
    assert block.correlation.ci_low <= block.correlation.r <= block.correlation.ci_high

    assert block.group_test is not None
    assert block.group_test.dof == 4
    assert block.group_test.min_expected >= 5

    assert block.seasonal is not None
    assert block.seasonal.revenue_definition == REVENUE_DEFINITION
    assert block.seasonal.method == "classical_additive_12"
    assert block.seasonal.period == 12
    assert len(block.seasonal.months) >= 24
    indexes = [month_index(label) for label in block.seasonal.months]
    assert indexes == list(range(indexes[0], indexes[0] + len(indexes)))
    assert sum(block.seasonal.observed) == pytest.approx(15_419_773.75, abs=1.0)
    assert block.skipped == []

    service = AnalyticsService(real_config)
    filters = KpiFilters()
    summary_kpis = service.kpi_summary(filters)
    assert summary_kpis["revenue"] == 15_419_773.75
    assert summary_kpis["orders"] == 96_478
    assert summary_kpis["late_rate_pct"] == 8.11
    assert summary_kpis["aov"] == 159.83

    # NFR1.2: mỗi phép đọc dữ liệu và mỗi phép kiểm định dưới 60 giây, đo quanh từng lời gọi.
    reads = (
        ("kpi_summary", lambda: service.kpi_summary(filters)),
        ("late_rates_by_state", lambda: service.late_rates_by_state(filters)),
        ("price_freight_pairs", lambda: service.price_freight_pairs(filters)),
        ("late_rates_by_region", lambda: service.late_rates_by_region(filters)),
        ("revenue_by_period", lambda: service.revenue_by_period(filters, "month")),
    )
    for name, read in reads:
        started_read = time.perf_counter()
        read()
        assert time.perf_counter() - started_read < 60, name

    # NFR1.7: số nhóm bị chặn bởi số bang và số tháng, không bởi số dòng.
    assert len(service.late_rates_by_state(filters)) <= 27
    assert len(service.revenue_by_period(filters, "month")) <= 36

    # NFR3.4: hai lần chạy liên tiếp cho cùng một tệp sau khi bỏ `generated_at`.
    first_stats = dict(payload["stats"])
    first_stats.pop("generated_at")
    run_stage(real_config, "stats")
    second = json.loads(path.read_text(encoding="utf-8"))
    second_stats = dict(second["stats"])
    second_stats.pop("generated_at")
    assert second_stats == first_stats
    assert second["version"] == payload["version"]
