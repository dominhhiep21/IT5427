"""Generate historical micro-batches for replay/velocity demonstration."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from src.common.io import read_parquet
from src.ingest.schemas import TABLE_SPECS


def _raw_columns(table: str) -> list[str]:
    return list(TABLE_SPECS[table].columns)


def generate(config, batches: int = 3, target_dir: Path | None = None) -> list[Path]:
    if batches < 1:
        raise ValueError("batches must be >= 1")
    target = Path(target_dir) if target_dir else config.inbox_dir / "replay"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)

    orders = read_parquet(config.cleaned_dir / "orders.parquet").copy()
    items = read_parquet(config.cleaned_dir / "order_items.parquet")
    payments = read_parquet(config.cleaned_dir / "payments.parquet")
    reviews = read_parquet(config.cleaned_dir / "reviews.parquet")

    orders["month"] = pd.to_datetime(orders["order_purchase_timestamp"]).dt.strftime("%Y-%m")
    months = sorted(orders["month"].dropna().unique())[-batches:]

    created: list[Path] = []
    for month in months:
        month_orders = orders[orders["month"] == month]
        order_ids = set(month_orders["order_id"])
        batch_dir = target / month
        batch_dir.mkdir(parents=True, exist_ok=True)

        month_orders[_raw_columns("orders")].to_csv(
            batch_dir / "orders.csv", index=False, encoding="utf-8"
        )
        items[items["order_id"].isin(order_ids)][_raw_columns("order_items")].to_csv(
            batch_dir / "order_items.csv", index=False, encoding="utf-8"
        )
        payments[payments["order_id"].isin(order_ids)][_raw_columns("payments")].to_csv(
            batch_dir / "payments.csv", index=False, encoding="utf-8"
        )
        reviews[reviews["order_id"].isin(order_ids)][_raw_columns("reviews")].to_csv(
            batch_dir / "reviews.csv", index=False, encoding="utf-8"
        )
        created.append(batch_dir)

    return created
