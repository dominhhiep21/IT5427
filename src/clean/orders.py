"""Cleaning for the orders table."""

from __future__ import annotations

import pandas as pd

from src.clean.common import invalid_parse_mask, parse_datetime

TIMESTAMP_COLUMNS = (
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    invalid = pd.Series(False, index=out.index)
    for column in TIMESTAMP_COLUMNS:
        parsed = parse_datetime(out[column])
        invalid = invalid | invalid_parse_mask(out[column], parsed)
        out[column] = parsed
    out["has_invalid_timestamp"] = invalid
    out["is_delivered"] = (
        out["order_status"].astype("string").str.strip().str.lower() == "delivered"
    )
    return out
