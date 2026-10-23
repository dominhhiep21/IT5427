"""Stage orchestration for the Olist pipeline."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from src.analytics.service import AnalyticsService
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter, read_parquet
from src.common.logging import JsonLogger, new_run_context
from src.common.types import KpiFilters
from src.ingest.reader import ingest_all
from src.ingest.reports import ReportWriter
from src.integrate.pipeline import integrate_all
from src.quality.gate import QualityGate

STAGES = ("ingest", "clean", "integrate", "analyze")


@dataclass
class StageResult:
    stage: str
    status: str
    rows_in: int = 0
    rows_out: int = 0
    duration_seconds: float = 0.0
    error: str = ""


@dataclass
class RunSummary:
    run_id: str
    command: str
    stages: list[StageResult] = field(default_factory=list)
    success: bool = True
    started_at: str = ""
    finished_at: str = ""


def _load_raw(config) -> dict:
    tables = (
        "translation",
        "customers",
        "sellers",
        "products",
        "orders",
        "order_items",
        "payments",
        "reviews",
        "geolocation",
    )
    return {
        table: read_parquet(config.raw_dir / f"{table}.parquet")
        for table in tables
    }


def _load_cleaned(config) -> dict:
    tables = (
        "translation",
        "customers",
        "sellers",
        "products",
        "orders",
        "order_items",
        "payments",
        "reviews",
        "geolocation_zip",
    )
    return {
        table: read_parquet(config.cleaned_dir / f"{table}.parquet")
        for table in tables
    }


def _run_all(config, refresh_ibge: bool, logger: JsonLogger, run, writer) -> RunSummary:
    summary = RunSummary(
        run_id=run.run_id,
        command="run --stage all",
        started_at=run.started_at.isoformat(),
    )
    reports = ReportWriter(config, writer)

    start = time.perf_counter()
    raw, ingest_report = ingest_all(config, run, writer, logger)
    reports.write_ingest(ingest_report)
    summary.stages.append(
        StageResult(
            "ingest",
            "success" if ingest_report.passed else "failed",
            rows_in=sum(item.rows for item in ingest_report.files),
            rows_out=sum(item.rows for item in ingest_report.files),
            duration_seconds=round(time.perf_counter() - start, 2),
        )
    )

    start = time.perf_counter()
    cleaned, cleaning_report = clean_all(raw, config, run, writer, logger)
    reports.write_cleaning(cleaning_report)
    summary.stages.append(
        StageResult(
            "clean",
            "success",
            rows_in=sum(len(frame) for frame in raw.values()),
            rows_out=sum(len(frame) for frame in cleaned.values()),
            duration_seconds=round(time.perf_counter() - start, 2),
        )
    )

    start = time.perf_counter()
    gate = QualityGate(logger)
    quality = gate.run(
        cleaned,
        mode="full",
        geo_stats=cleaning_report.geolocation,
        run_id=run.run_id,
    )
    reports.write_quality(quality)
    gate.enforce(quality)
    summary.stages.append(
        StageResult(
            "quality",
            "success",
            rows_in=sum(len(frame) for frame in cleaned.values()),
            rows_out=sum(len(frame) for frame in cleaned.values()),
            duration_seconds=round(time.perf_counter() - start, 2),
        )
    )

    start = time.perf_counter()
    integrate_all(config, run, writer, logger, refresh_ibge=refresh_ibge)
    summary.stages.append(
        StageResult(
            "integrate",
            "success",
            duration_seconds=round(time.perf_counter() - start, 2),
        )
    )

    start = time.perf_counter()
    AnalyticsService(config).kpi_summary(KpiFilters())
    summary.stages.append(
        StageResult(
            "analyze",
            "success",
            duration_seconds=round(time.perf_counter() - start, 2),
        )
    )

    summary.success = all(stage.status == "success" for stage in summary.stages)
    summary.finished_at = datetime.now(timezone.utc).isoformat()
    _write_summary(config, summary, writer)
    writer.cleanup()
    return summary


def _write_summary(config, summary: RunSummary, writer: AtomicWriter) -> None:
    writer.write_json(
        asdict(summary), config.reports_dir / "run-summary.json"
    )


def run_all(config, refresh_ibge: bool = False) -> RunSummary:
    run = new_run_context("all", config.logs_dir, config.temp_dir)
    writer = AtomicWriter(run, config.parquet_compression)
    logger = JsonLogger(run)
    try:
        summary = _run_all(config, refresh_ibge, logger, run, writer)
        logger.summary(
            f"run={run.run_id} success={summary.success} "
            f"stages={[s.stage for s in summary.stages]}"
        )
        return summary
    except Exception as exc:
        logger.error("run_failed", "PIPELINE_ERROR", error=str(exc))
        raise


def run_stage(config, stage: str, refresh_ibge: bool = False) -> RunSummary:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    run = new_run_context(stage, config.logs_dir, config.temp_dir)
    writer = AtomicWriter(run, config.parquet_compression)
    logger = JsonLogger(run)
    summary = RunSummary(run_id=run.run_id, command=f"run --stage {stage}")
    start = time.perf_counter()
    try:
        if stage == "ingest":
            raw, report = ingest_all(config, run, writer, logger)
            ReportWriter(config, writer).write_ingest(report)
            rows = sum(len(frame) for frame in raw.values())
            summary.stages.append(
                StageResult(stage, "success", rows, rows, round(time.perf_counter() - start, 2))
            )
        elif stage == "clean":
            raw = _load_raw(config)
            cleaned, report = clean_all(raw, config, run, writer, logger)
            ReportWriter(config, writer).write_cleaning(report)
            summary.stages.append(
                StageResult(
                    stage,
                    "success",
                    sum(len(frame) for frame in raw.values()),
                    sum(len(frame) for frame in cleaned.values()),
                    round(time.perf_counter() - start, 2),
                )
            )
        elif stage == "integrate":
            integrate_all(config, run, writer, logger, refresh_ibge=refresh_ibge)
            summary.stages.append(
                StageResult(stage, "success", duration_seconds=round(time.perf_counter() - start, 2))
            )
        elif stage == "analyze":
            summary_data = AnalyticsService(config).kpi_summary(KpiFilters())
            summary.stages.append(
                StageResult(stage, "success", duration_seconds=round(time.perf_counter() - start, 2))
            )
            logger.info("analyze_smoke", **summary_data)
        summary.success = True
        summary.finished_at = datetime.now(timezone.utc).isoformat()
        _write_summary(config, summary, writer)
        writer.cleanup()
        logger.summary(f"run={run.run_id} stage={stage} success=True")
        return summary
    except Exception as exc:
        logger.error("stage_failed", "PIPELINE_ERROR", stage=stage, error=str(exc))
        summary.success = False
        summary.stages.append(
            StageResult(stage, "failed", error=str(exc), duration_seconds=round(time.perf_counter() - start, 2))
        )
        _write_summary(config, summary, writer)
        raise
