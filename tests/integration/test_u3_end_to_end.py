"""End-to-end U3 tests: CLI stage, replay batch, dashboard layout."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.analytics.service import AnalyticsService
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.common.types import KpiFilters
from src.dashboard.app import create_app
from src.ingest.reader import ingest_all
from src.integrate.pipeline import integrate_all
from src.pipeline.micro_batch import process_inbox
from src.pipeline.replay import generate
from src.pipeline.stages import run_stage


@pytest.mark.slow
def test_u3_end_to_end(real_config, tmp_path: Path):
    run = new_run_context("u3-setup", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)
    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    integrate_all(real_config, run, writer, logger)

    summary = run_stage(real_config, "analyze")
    assert summary.success

    replay_dir = tmp_path / "replay"
    batches = generate(real_config, batches=1, target_dir=replay_dir)
    assert len(batches) == 1
    results = process_inbox(real_config, replay_dir)
    assert results
    assert all(result.status in {"success", "skipped"} for result in results)

    service = AnalyticsService(real_config)
    kpi = service.kpi_summary(KpiFilters())
    assert kpi["revenue"] == 15_419_773.75
    assert kpi["orders"] == 96_478

    app = create_app(real_config)
    assert app.title == "Olist | Bảng điều hành"
    assert len(app.callback_map) == 2

    writer.cleanup()
