"""End-to-end U2 integration test on real cleaned data."""

from __future__ import annotations

import pytest

from src.analytics.service import AnalyticsService
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.common.types import KpiFilters
from src.ingest.reader import ingest_all
from src.integrate.catalog import DuckDbCatalog
from src.integrate.pipeline import integrate_all


@pytest.mark.slow
def test_u2_end_to_end(real_config):
    run = new_run_context("u2-integration", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)

    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)

    result = integrate_all(real_config, run, writer, logger, refresh_ibge=False)
    counts = result.report.row_counts

    assert counts["dim_customer"] == 99_441
    assert counts["dim_product"] == 32_951
    assert counts["dim_seller"] == 3_095
    assert counts["dim_geography"] == 19_015
    assert counts["dim_date"] == 774
    assert counts["fact_order_items"] == 112_650
    assert counts["fact_orders"] == 99_441
    assert counts["fact_payments"] == 103_886
    assert counts["fact_reviews"] == 99_224

    assert result.reconciliation.passed
    assert result.reconciliation.metrics["revenue_delivered"] == 15_419_773.75
    assert result.reconciliation.metrics["late_orders"] == 7_826

    views = DuckDbCatalog(real_config).list_views()
    assert len(views) == 11
    assert "v_fact_order_items" in views

    service = AnalyticsService(real_config)
    summary = service.kpi_summary(KpiFilters())
    assert summary["revenue"] == 15_419_773.75
    assert summary["orders"] == 96_478
    assert summary["aov"] == 159.83
    assert summary["late_rate_pct"] == 8.11

    monthly = service.revenue_by_period(KpiFilters(), "month")
    assert monthly.loc[monthly["year"] == 2016, "is_sparse_period"].all()

    quarterly = service.revenue_by_period(KpiFilters(), "quarter")
    yearly = service.revenue_by_period(KpiFilters(), "year")
    assert len(quarterly) > 0
    assert len(yearly) == 3

    categories = service.revenue_by_dimension(KpiFilters(), "category")
    regions = service.revenue_by_dimension(KpiFilters(), "region")
    states = service.revenue_by_dimension(KpiFilters(), "state")
    assert round(categories["revenue"].sum(), 2) == 15_419_773.75
    assert len(regions) == 5
    assert len(states) == 27

    products = service.top_entities(KpiFilters(), "product", 5)
    sellers = service.top_entities(KpiFilters(), "seller", 5)
    assert len(products) == 5
    assert len(sellers) == 5

    delivery = service.delivery_kpis(KpiFilters(), "state")
    assert int(delivery["late_orders"].sum()) == 7_826
    assert len(service.delivery_kpis(KpiFilters(), "category")) > 0
    assert len(service.delivery_kpis(KpiFilters(), "month")) > 0

    sp_summary = service.kpi_summary(KpiFilters(state="SP"))
    assert sp_summary["orders"] < summary["orders"]

    with pytest.raises(ValueError):
        service.revenue_by_period(KpiFilters(), "day")
    with pytest.raises(ValueError):
        service.revenue_by_dimension(KpiFilters(), "seller")
    with pytest.raises(ValueError):
        service.top_entities(KpiFilters(), "category", 5)
    with pytest.raises(ValueError):
        service.delivery_kpis(KpiFilters(), "year")

    writer.cleanup()
