"""U1 end-to-end trên dữ liệu thật: ba cột mart mới và bất biến số dòng + 5 KPI."""

from __future__ import annotations

import pandas as pd
import pytest

from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.ingest.reader import ingest_all
from src.integrate.catalog import DuckDbCatalog
from src.integrate.pipeline import integrate_all


def _run_pipeline(real_config):  # noqa: ANN001
    run = new_run_context("u1-columns", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)
    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    return integrate_all(real_config, run, writer, logger, refresh_ibge=False)


@pytest.mark.slow
def test_u1_row_counts_and_kpis_unchanged(real_config) -> None:  # noqa: ANN001
    """BR1.1, NFR4.1 — thêm cột không đổi một dòng nào và 5 KPI vẫn khớp."""

    result = _run_pipeline(real_config)
    counts = result.report.row_counts

    assert counts["fact_orders"] == 99_441
    assert counts["fact_order_items"] == 112_650
    assert counts["dim_customer"] == 99_441
    assert counts["dim_seller"] == 3_095
    assert counts["dim_geography"] == 19_015
    assert result.reconciliation.passed
    assert len(DuckDbCatalog(real_config).list_views()) == 11


@pytest.mark.slow
def test_u1_new_columns_readable_from_mart(real_config) -> None:  # noqa: ANN001
    """BR1.6, BR1.7 — ba cột đọc được từ mart thật; cột người bán không tên `state`."""

    _run_pipeline(real_config)

    orders = pd.read_parquet(real_config.marts_dir / "fact_orders.parquet")
    items = pd.read_parquet(real_config.marts_dir / "fact_order_items.parquet")

    assert "order_approved_at" in orders.columns
    assert "order_delivered_carrier_date" in orders.columns
    assert "seller_state" in items.columns
    assert "state" not in items.columns
