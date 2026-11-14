"""Cổng mốc sàn trên `data/reports/analysis.json` thật (NFR5, AC3.2.2) — không fixture."""

from __future__ import annotations

import pytest

from src.analytics.model import beats_floor
from src.analytics.report import read_report, report_path
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.ingest.reader import ingest_all
from src.integrate.pipeline import integrate_all
from src.pipeline.stages import run_stage


@pytest.mark.slow
def test_u3_floor_end_to_end(real_config) -> None:  # noqa: ANN001
    run = new_run_context("u3-floor", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)

    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    integrate_all(real_config, run, writer, logger, refresh_ibge=False)

    summary = run_stage(real_config, "stats")
    assert summary.success is True

    view = read_report(report_path(real_config))
    assert view.status == "day-du"
    report = view.report
    assert report is not None
    model = report.model
    assert model is not None

    # NFR5 — ngoại lệ có chủ đích: chỉ khẳng định mốc sàn, không ghim giá trị AUC.
    assert beats_floor(model.auc, model.baseline_auc) is True, (
        f"AUC {model.auc} không đạt mốc sàn so với baseline {model.baseline_auc} (NFR5)."
    )
