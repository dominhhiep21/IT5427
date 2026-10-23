"""Micro-batch ingestion from inbox/{batch_id}/{table}.csv."""

from __future__ import annotations

import hashlib
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from src.clean.customers import clean_customers
from src.clean.geolocation import clean_geolocation
from src.clean.items import clean_order_items
from src.clean.orders import clean_orders
from src.clean.payments import clean_payments
from src.clean.products import clean_products, clean_translation
from src.clean.reviews import clean_reviews
from src.clean.sellers import clean_sellers
from src.common.io import AtomicWriter, read_csv, read_parquet
from src.common.logging import JsonLogger, new_run_context
from src.common.types import RunContext
from src.ingest.schemas import TABLE_SPECS
from src.integrate.pipeline import integrate_all
from src.pipeline.manifest import ManifestStore
from src.pipeline.upsert import upsert
from src.quality.gate import QualityGate

TABLE_KEYS = {
    "orders": ["order_id"],
    "customers": ["customer_id"],
    "sellers": ["seller_id"],
    "products": ["product_id"],
    "order_items": ["order_id", "order_item_id"],
    "payments": ["order_id", "payment_sequential"],
    "reviews": ["review_id", "order_id"],
    "translation": ["product_category_name"],
    "geolocation_zip": ["zip_code_prefix"],
}


@dataclass
class BatchResult:
    batch_id: str
    status: str
    tables: list[str] = field(default_factory=list)
    rows_upserted: int = 0
    duration_seconds: float = 0.0
    run_id: str = ""
    error: str = ""


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _clean_batch_table(table: str, frame: pd.DataFrame, temp_cleaned: Path):
    if table == "orders":
        return "orders", clean_orders(frame)
    if table == "customers":
        return "customers", clean_customers(frame)
    if table == "sellers":
        return "sellers", clean_sellers(frame)
    if table == "products":
        translation = read_parquet(temp_cleaned / "translation.parquet")
        return "products", clean_products(frame, translation)
    if table == "order_items":
        return "order_items", clean_order_items(frame)
    if table == "payments":
        return "payments", clean_payments(frame)
    if table == "reviews":
        return "reviews", clean_reviews(frame)
    if table == "translation":
        return "translation", clean_translation(frame)
    if table == "geolocation":
        geo, _ = clean_geolocation(frame)
        return "geolocation_zip", geo
    raise ValueError(f"Unknown batch table: {table}")


def process_inbox(config, inbox_dir: Path | None = None) -> list[BatchResult]:
    inbox = Path(inbox_dir) if inbox_dir else config.inbox_dir
    inbox.mkdir(parents=True, exist_ok=True)
    manifest = ManifestStore(inbox / "manifest.json")
    results: list[BatchResult] = []

    for batch_dir in sorted(path for path in inbox.iterdir() if path.is_dir()):
        csv_files = sorted(batch_dir.glob("*.csv"))
        if not csv_files:
            continue
        run = new_run_context("micro-batch", config.logs_dir, config.temp_dir)
        writer = AtomicWriter(run, config.parquet_compression)
        logger = JsonLogger(run)
        started = time.perf_counter()
        result = BatchResult(batch_id=batch_dir.name, status="failed", run_id=run.run_id)
        files_meta = []

        try:
            for path in csv_files:
                table = path.stem
                if table not in TABLE_SPECS:
                    raise ValueError(f"Unknown table file: {path.name}")
                digest = _hash(path)
                files_meta.append(
                    {"table": table, "file": str(path), "sha256": digest, "status": "pending"}
                )

            if files_meta and all(manifest.has_success(item["sha256"]) for item in files_meta):
                result.status = "skipped"
                result.tables = [item["table"] for item in files_meta]
                for meta in files_meta:
                    meta["status"] = "skipped"
                manifest.record(
                    {
                        "batch_id": result.batch_id,
                        "files": files_meta,
                        "status": "skipped",
                        "error": "",
                    }
                )
                writer.cleanup()
                results.append(result)
                continue

            temp_cleaned = run.temp_dir / "cleaned"
            shutil.copytree(config.cleaned_dir, temp_cleaned)

            for path, meta in zip(csv_files, files_meta):
                table = path.stem
                frame = read_csv(path, TABLE_SPECS[table])
                if len(frame) > config.max_batch_rows:
                    raise ValueError(
                        f"{path.name} has {len(frame)} rows > {config.max_batch_rows}"
                    )
                cleaned_table, cleaned_frame = _clean_batch_table(
                    table, frame, temp_cleaned
                )
                target = temp_cleaned / f"{cleaned_table}.parquet"
                existing = read_parquet(target) if target.exists() else pd.DataFrame()
                combined = upsert(existing, cleaned_frame, TABLE_KEYS[cleaned_table])
                writer.write_parquet(combined, target)
                result.tables.append(cleaned_table)
                result.rows_upserted += len(cleaned_frame)
                meta["status"] = "success"
                meta["rows"] = len(frame)

            gate = QualityGate(logger)
            report = gate.run(
                {
                    name: read_parquet(temp_cleaned / f"{name}.parquet")
                    for name in TABLE_KEYS
                },
                mode="incremental",
                run_id=run.run_id,
            )
            gate.enforce(report)

            for name in TABLE_KEYS:
                source = temp_cleaned / f"{name}.parquet"
                if source.exists():
                    os.replace(source, config.cleaned_dir / f"{name}.parquet")

            integrate_all(config, run, writer, logger)
            result.status = "success"
            logger.info("batch_success", batch_id=result.batch_id, rows=result.rows_upserted)
            writer.cleanup()
        except Exception as exc:
            result.status = "failed"
            result.error = str(exc)[:500]
            for meta in files_meta:
                if meta["status"] != "success":
                    meta["status"] = "failed"
            logger.error("batch_failed", "BATCH_ERROR", batch_id=result.batch_id, error=result.error)

        result.duration_seconds = round(time.perf_counter() - started, 2)
        manifest.record(
            {
                "batch_id": result.batch_id,
                "files": files_meta,
                "status": result.status,
                "error": result.error,
            }
        )
        results.append(result)

    return results
