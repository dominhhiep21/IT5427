"""Build the per-record evidence index from the source CSVs (L1 of `logical-components.md`)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.common.io import read_csv
from src.ingest.schemas import TABLE_SPECS
from src.linkage.models import (
    CUSTOMER,
    SELLER,
    clean_text,
    normalize_city,
    zip_prefix,
)

RECORD_TABLES = {CUSTOMER: "customers", SELLER: "sellers"}
RECORD_COLUMNS = {
    CUSTOMER: (
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
    ),
    SELLER: (
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
    ),
}
PAYMENT_DECIMALS = 2


@dataclass(frozen=True)
class Evidence:
    """Everything the scorer may look at for one record, built once (TS-U4-3)."""

    record_id: str
    city: str
    zip_prefix: str
    products: frozenset[str]
    payments: frozenset[float]
    order_count: int
    unique_id: str | None = None


@dataclass(frozen=True)
class EvidenceIndex:
    """The whole evidence set for one target entity, plus the source-level counts."""

    target_entity: str
    records: dict[str, Evidence]
    duplicate_groups: int
    records_missing_match_fields: int

    @property
    def records_scored(self) -> int:
        return sum(1 for evidence in self.records.values() if evidence.zip_prefix)


def _amount(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def evidence_for(
    records: pd.DataFrame,
    orders: pd.DataFrame | None,
    items: pd.DataFrame,
    payments: pd.DataFrame,
    target_entity: str,
) -> tuple[dict[str, Evidence], int]:
    """Turn the source frames into one `Evidence` per record; pure, so tests need no disk."""

    if target_entity not in RECORD_COLUMNS:
        raise ValueError(f"target_entity không hợp lệ: {target_entity!r}")

    products_by_order: dict[str, set[str]] = {}
    for order_id, product_id in items[["order_id", "product_id"]].itertuples(index=False, name=None):
        if product_id is None or product_id != product_id:
            continue
        products_by_order.setdefault(str(order_id), set()).add(str(product_id))

    payment_by_order: dict[str, float] = {}
    for order_id, value in payments[["order_id", "payment_value"]].itertuples(index=False, name=None):
        amount = _amount(value)
        if amount is None:
            continue
        key = str(order_id)
        payment_by_order[key] = payment_by_order.get(key, 0.0) + amount

    orders_by_record: dict[str, set[str]] = {}
    products_by_record: dict[str, set[str]] = {}
    if target_entity == CUSTOMER:
        frame = orders if orders is not None else pd.DataFrame({"customer_id": [], "order_id": []})
        for customer_id, order_id in frame[["customer_id", "order_id"]].itertuples(index=False, name=None):
            if order_id is None or order_id != order_id:
                continue
            orders_by_record.setdefault(str(customer_id), set()).add(str(order_id))
    else:
        columns = ["seller_id", "order_id", "product_id"]
        for seller_id, order_id, product_id in items[columns].itertuples(index=False, name=None):
            if product_id is None or product_id != product_id:
                continue
            orders_by_record.setdefault(str(seller_id), set()).add(str(order_id))
            products_by_record.setdefault(str(seller_id), set()).add(str(product_id))

    columns = RECORD_COLUMNS[target_entity]
    evidence_by_id: dict[str, Evidence] = {}
    for row in records[list(columns)].itertuples(index=False, name=None):
        if target_entity == CUSTOMER:
            record_id, unique_raw, zip_value, city_value = row
        else:
            record_id, zip_value, city_value = row
            unique_raw = ""
        record_id = str(record_id)
        unique_id = clean_text(unique_raw)
        order_ids = orders_by_record.get(record_id, set())
        products = products_by_record.get(record_id)
        if products is None:
            products = set()
            for order_id in order_ids:
                products |= products_by_order.get(order_id, set())
        payment_values = {
            round(payment_by_order[order_id], PAYMENT_DECIMALS)
            for order_id in order_ids
            if order_id in payment_by_order
        }
        evidence_by_id[record_id] = Evidence(
            record_id=record_id,
            city=normalize_city(city_value),
            zip_prefix=zip_prefix(zip_value),
            products=frozenset(products),
            payments=frozenset(payment_values),
            order_count=len(order_ids),
            unique_id=unique_id or None,
        )

    duplicate_groups = sum(
        1
        for count in Counter(
            evidence.unique_id for evidence in evidence_by_id.values() if evidence.unique_id
        ).values()
        if count >= 2
    )
    return evidence_by_id, duplicate_groups


def _source_path(config, table: str) -> Path:
    return Path(config.raw_csv_dir) / TABLE_SPECS[table].file_name


def build_index(config, target_entity: str) -> EvidenceIndex:
    """Read the source tables for `target_entity` and build its evidence index."""

    if target_entity not in RECORD_TABLES:
        raise ValueError(f"target_entity không hợp lệ: {target_entity!r}")
    record_table = RECORD_TABLES[target_entity]
    frames: dict[str, pd.DataFrame] = {
        record_table: read_csv(_source_path(config, record_table), TABLE_SPECS[record_table]),
        "order_items": read_csv(_source_path(config, "order_items"), TABLE_SPECS["order_items"]),
        "payments": read_csv(_source_path(config, "payments"), TABLE_SPECS["payments"]),
    }
    if target_entity == CUSTOMER:
        frames["orders"] = read_csv(_source_path(config, "orders"), TABLE_SPECS["orders"])

    evidence_by_id, duplicate_groups = evidence_for(
        frames[record_table],
        frames.get("orders"),
        frames["order_items"],
        frames["payments"],
        target_entity,
    )
    missing = sum(1 for evidence in evidence_by_id.values() if not evidence.zip_prefix)
    return EvidenceIndex(
        target_entity=target_entity,
        records=evidence_by_id,
        duplicate_groups=duplicate_groups,
        records_missing_match_fields=missing,
    )
