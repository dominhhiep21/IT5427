"""Cleaning for order items."""

from __future__ import annotations

import pandas as pd

from src.clean.common import iqr_bounds, parse_datetime, to_integer, to_numeric


def clean_order_items(df: pd.DataFrame, iqr_multiplier: float = 1.5) -> pd.DataFrame:
    out = df.copy()
    out["order_item_id"] = to_integer(out["order_item_id"])
    out["shipping_limit_date"] = parse_datetime(out["shipping_limit_date"])
    out["price"] = to_numeric(out["price"])
    out["freight_value"] = to_numeric(out["freight_value"])

    lower, upper = iqr_bounds(out["price"], iqr_multiplier)
    out["price_outlier"] = (
        out["price"].notna() & ((out["price"] < lower) | (out["price"] > upper))
    )
    return out
