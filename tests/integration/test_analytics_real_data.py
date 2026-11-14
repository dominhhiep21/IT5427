"""Phân tích và đối soát trên bộ Olist đầy đủ: chốt các con số dùng trong báo cáo và buổi bảo vệ."""

from __future__ import annotations

import pytest

from src.analytics import insights
from src.analytics.connection import open_analysis_connection
from src.analytics.reconciliation import FAIL, INFO, PASS, SKIP
from src.analytics.report import build_analysis_report, run_bundle
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.ingest.reader import ingest_all
from src.integrate.pipeline import integrate_all


@pytest.mark.slow
def test_analytics_on_full_olist_dataset(real_config):
    run = new_run_context("analytics-real", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)
    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    integrate_all(real_config, run, writer, logger, refresh_ibge=False)

    conn = open_analysis_connection(real_config)
    try:
        bundle = run_bundle(conn)
    finally:
        conn.close()
    frames, recon = bundle.frames, bundle.reconciliation

    # Mục 16 — đối soát: ba đường tính độc lập khớp nhau và khớp baseline.
    assert recon.passed
    assert recon.has_sources
    assert recon.counts() == {PASS: 8, FAIL: 0, INFO: 9, SKIP: 0}
    assert recon.get("DS-05").values == {
        "fact_revenue": 15_419_773.75,
        "aggregate_revenue": 15_419_773.75,
        "source_revenue": 15_419_773.75,
    }
    assert set(recon.get("DS-06").values.values()) == {96_478}
    assert set(recon.get("DS-07").values.values()) == {7_826}
    assert recon.get("DS-09").values["naive_join_revenue"] == 16_114_019.06
    assert recon.get("DS-09").values["inflation_pct"] == 4.5
    assert recon.get("DS-10").values["naive_join_revenue"] == 15_361_245.11
    assert recon.get("DS-11").values["summed_orders_in_aggregate"] == 97_276
    assert recon.get("DS-13").values["orders_mismatched"] == 303
    assert recon.get("DS-14").values["late_by_calendar_day"] == 6_534
    assert recon.get("DS-15").values["delivered_without_date"] == 8
    assert recon.get("DS-16").values["extra_review_rows"] == 551

    # Mục 17 — kinh doanh.
    head = frames["kpi_headline"].iloc[0]
    assert head.revenue == 15_419_773.75
    assert head.orders == 96_478
    assert head.aov == 159.83
    assert head.customers == 93_358
    assert head.late_rate_pct == 8.11
    assert head.avg_review_score == 4.16

    monthly = frames["monthly_trend"]
    dense = monthly[~monthly["is_sparse_period"]]
    assert dense.loc[dense["revenue"].idxmax(), "period"] == "2017-11"
    assert round(monthly["revenue"].sum(), 2) == 15_419_773.75
    assert frames["peak_days"].iloc[0].order_date == "2017-11-24"
    assert frames["yearly_same_period"]["revenue"].tolist() == [3_472_898.25, 8_451_584.77]
    assert frames["customer_repeat"].iloc[0].repeat_rate_pct == 3.0

    # Mục 18 — sản phẩm và người bán.
    categories = frames["category_ranking"]
    assert categories.iloc[0].category == "beleza_saude"
    assert round(categories["revenue"].sum(), 2) == 15_419_773.75
    assert frames["seller_concentration"].iloc[0].top_20pct_share_pct == 81.62
    assert len(frames["top_sellers"]) == 10

    # Mục 19 — giao vận.
    overview = frames["delivery_overview"].iloc[0]
    assert (overview.avg_delivery_days, overview.median_delivery_days) == (12.56, 10.22)
    regions = frames["delivery_by_region"]
    assert int(regions["late_orders"].sum()) == 7_826
    assert (regions.iloc[0].region, regions.iloc[0].late_rate_pct) == ("Nordeste", 14.33)
    assert len(frames["delivery_by_state"]) == 27

    # Mục 20 — đánh giá.
    by_late = frames["review_by_late"].set_index("delivery_status")
    assert by_late.loc["Đúng hạn", "avg_review_score"] == 4.29
    assert by_late.loc["Giao trễ", "avg_review_score"] == 2.57
    assert frames["review_by_delay"]["avg_review_score"].is_monotonic_decreasing
    assert int(frames["review_distribution"]["orders"].sum()) == bundle.chi_square.n == 95_832
    assert bundle.chi_square.dof == 4
    assert bundle.chi_square.chi2 == pytest.approx(14_218.96, abs=0.01)
    assert bundle.chi_square.cramers_v == pytest.approx(0.385, abs=0.001)
    assert bundle.chi_square.significant()

    text = build_analysis_report(bundle)
    assert "đúng ngày Black Friday 2017" in text
    assert all(f"## Mục {task}" in text for task in insights.TASK_TITLES)

    writer.cleanup()
