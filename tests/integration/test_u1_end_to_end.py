"""End-to-end U1 integration test on the real Olist dataset."""

from __future__ import annotations

import pytest

from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.ingest.reader import ingest_all
from src.ingest.reports import ReportWriter, reconcile_payments
from src.quality.gate import QualityGate


@pytest.mark.slow
def test_u1_end_to_end(real_config):
    run = new_run_context("integration", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)

    raw, ingest_report = ingest_all(real_config, run, writer, logger)
    assert len(ingest_report.files) == 9
    assert ingest_report.passed
    assert len(raw["orders"]) == 99_441
    assert len(raw["geolocation"]) == 1_000_163

    cleaned, cleaning_report = clean_all(raw, real_config, run, writer, logger)
    assert len(cleaned["orders"]) == 99_441
    assert len(cleaned["order_items"]) == 112_650
    assert len(cleaned["payments"]) == 103_886
    assert len(cleaned["reviews"]) == 99_224
    assert len(cleaned["products"]) == 32_951
    assert len(cleaned["geolocation_zip"]) == 19_015
    assert int(cleaned["products"]["category_missing"].sum()) == 610
    assert int(cleaned["products"]["translation_missing"].sum()) == 13
    assert cleaned["products"].loc[
        cleaned["products"]["translation_missing"], "product_category_name"
    ].nunique() == 2
    assert int(cleaned["order_items"]["price_outlier"].sum()) == 8_427
    assert cleaned["reviews"].loc[
        cleaned["reviews"]["multiple_reviews_per_order"], "order_id"
    ].nunique() == 547

    join_check = cleaned["orders"].merge(
        cleaned["customers"], on="customer_id", how="left"
    ).merge(
        cleaned["geolocation_zip"],
        left_on="customer_zip_code_prefix",
        right_on="zip_code_prefix",
        how="left",
    )
    assert len(join_check) == 99_441

    gate = QualityGate(logger)
    report = gate.run(
        cleaned,
        mode="full",
        geo_stats=cleaning_report.geolocation,
        run_id=run.run_id,
    )
    gate.enforce(report)
    assert report.passed

    reconciliation = reconcile_payments(cleaned, run.run_id)
    assert reconciliation.mismatch_count == 378

    reports = ReportWriter(real_config, writer)
    reports.write_ingest(ingest_report)
    reports.write_cleaning(cleaning_report)
    reports.write_quality(report)
    reports.write_reconciliation(reconciliation)
    writer.cleanup()
