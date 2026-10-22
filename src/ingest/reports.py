"""Persist ingest, cleaning, quality and reconciliation reports."""

from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from src.common.io import AtomicWriter
from src.common.types import (
    CleaningReport,
    IngestReport,
    QualityReport,
    ReconciliationReport,
)


class ReportWriter:
    def __init__(self, config, writer: AtomicWriter) -> None:
        self.config = config
        self.writer = writer

    def write_ingest(self, report: IngestReport) -> None:
        self.writer.write_json(
            asdict(report), self.config.reports_dir / "ingest-report.json"
        )

    def write_cleaning(self, report: CleaningReport) -> None:
        self.writer.write_json(
            asdict(report), self.config.reports_dir / "cleaning-report.json"
        )

    def write_quality(self, report: QualityReport) -> None:
        self.writer.write_json(
            asdict(report), self.config.reports_dir / "quality-report.json"
        )

    def write_reconciliation(self, report: ReconciliationReport) -> None:
        self.writer.write_json(
            asdict(report), self.config.reports_dir / "reconciliation.json"
        )


def reconcile_payments(
    datasets: dict[str, pd.DataFrame],
    run_id: str,
) -> ReconciliationReport:
    items = datasets["order_items"].copy()
    items["item_total"] = items["price"].fillna(0) + items["freight_value"].fillna(0)
    item_totals = items.groupby("order_id", dropna=False)["item_total"].sum()

    payment_totals = datasets["payments"].groupby("order_id", dropna=False)[
        "payment_value"
    ].sum()

    joined = pd.concat(
        [item_totals.rename("item_total"), payment_totals.rename("payment_total")],
        axis=1,
    )
    joined["diff"] = joined["payment_total"] - joined["item_total"]
    mismatch = joined["diff"].abs() > 0.01

    examples = (
        joined.loc[mismatch]
        .reset_index()
        .sort_values("diff", key=lambda series: series.abs(), ascending=False)
        .head(10)
        .to_dict(orient="records")
    )

    return ReconciliationReport(
        run_id=run_id,
        orders_compared=int(len(joined)),
        mismatch_count=int(mismatch.sum()),
        max_abs_diff=round(float(joined["diff"].abs().max()), 2),
        examples=examples,
    )
