"""Read and validate raw CSVs, then persist raw Parquet."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.common.io import AtomicWriter, read_csv, sha256_file
from src.common.logging import JsonLogger
from src.common.types import IngestFileReport, IngestReport, RunContext, TableSpec
from src.ingest.schemas import TABLE_SPECS


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ingest_table(
    spec: TableSpec,
    raw_csv_dir: Path,
    raw_output_dir: Path,
    writer: AtomicWriter,
    logger: JsonLogger,
) -> tuple[pd.DataFrame, IngestFileReport]:
    path = raw_csv_dir / spec.file_name
    df = read_csv(path, spec)
    digest = sha256_file(path)
    writer.write_parquet(df, raw_output_dir / f"{spec.name}.parquet")
    report = IngestFileReport(
        table=spec.name,
        file=str(path),
        rows=len(df),
        expected_rows=spec.expected_rows,
        columns=len(df.columns),
        sha256=digest,
        read_at=_utc_now_iso(),
    )
    logger.info(
        "ingest_table",
        table=spec.name,
        rows_in=len(df),
        rows_out=len(df),
        sha256=digest,
    )
    return df, report


def ingest_all(
    config,
    run: RunContext,
    writer: AtomicWriter,
    logger: JsonLogger,
) -> tuple[dict[str, pd.DataFrame], IngestReport]:
    datasets: dict[str, pd.DataFrame] = {}
    report = IngestReport(run_id=run.run_id)
    for spec in TABLE_SPECS.values():
        df, file_report = ingest_table(
            spec=spec,
            raw_csv_dir=config.raw_csv_dir,
            raw_output_dir=config.raw_dir,
            writer=writer,
            logger=logger,
        )
        datasets[spec.name] = df
        report.files.append(file_report)
    report.passed = all(item.rows == item.expected_rows for item in report.files)
    logger.info(
        "ingest_complete",
        tables=len(report.files),
        rows_in=sum(item.rows for item in report.files),
        passed=report.passed,
    )
    return datasets, report
