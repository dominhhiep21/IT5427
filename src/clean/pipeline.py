"""Run all cleaning steps and persist cleaned Parquet tables."""

from __future__ import annotations

import pandas as pd

from src.clean.common import flag_counts, null_counts
from src.clean.customers import clean_customers
from src.clean.geolocation import clean_geolocation
from src.clean.items import clean_order_items
from src.clean.orders import clean_orders
from src.clean.payments import clean_payments
from src.clean.products import clean_products, clean_translation
from src.clean.reviews import clean_reviews
from src.clean.sellers import clean_sellers
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger
from src.common.types import CleaningReport, CleaningTableReport, RunContext


def clean_all(
    raw: dict[str, pd.DataFrame],
    config,
    run: RunContext,
    writer: AtomicWriter,
    logger: JsonLogger,
) -> tuple[dict[str, pd.DataFrame], CleaningReport]:
    translation = clean_translation(raw["translation"])
    customers = clean_customers(raw["customers"])
    sellers = clean_sellers(raw["sellers"])
    products = clean_products(raw["products"], translation)
    orders = clean_orders(raw["orders"])
    order_items = clean_order_items(raw["order_items"], config.iqr_multiplier)
    payments = clean_payments(raw["payments"])
    reviews = clean_reviews(raw["reviews"])
    geolocation_zip, geo_stats = clean_geolocation(
        raw["geolocation"],
        lat_min=config.geo_lat_min,
        lat_max=config.geo_lat_max,
        lng_min=config.geo_lng_min,
        lng_max=config.geo_lng_max,
    )

    cleaned: dict[str, pd.DataFrame] = {
        "translation": translation,
        "customers": customers,
        "sellers": sellers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "reviews": reviews,
        "geolocation_zip": geolocation_zip,
    }

    flag_columns = {
        "products": ("category_missing", "translation_missing"),
        "orders": ("has_invalid_timestamp", "is_delivered"),
        "order_items": ("price_outlier",),
        "reviews": ("multiple_reviews_per_order",),
    }

    report = CleaningReport(run_id=run.run_id, geolocation=geo_stats)
    for name, frame in cleaned.items():
        writer.write_parquet(frame, config.cleaned_dir / f"{name}.parquet")
        rows_in = len(raw["geolocation"]) if name == "geolocation_zip" else len(raw[name])
        table_report = CleaningTableReport(
            table=name,
            rows_in=rows_in,
            rows_out=len(frame),
            null_counts=null_counts(frame),
            flag_counts=flag_counts(frame, flag_columns.get(name, ())),
        )
        report.tables.append(table_report)
        logger.info(
            "clean_table",
            table=name,
            rows_in=rows_in,
            rows_out=len(frame),
            flags=table_report.flag_counts,
        )

    logger.info(
        "clean_geolocation_complete",
        raw_rows=geo_stats.raw_rows,
        deduped_rows=geo_stats.deduped_rows,
        outside_bbox=geo_stats.outside_bbox,
        zips=geo_stats.zips,
        zips_without_coord=geo_stats.zips_without_coord,
    )
    return cleaned, report
