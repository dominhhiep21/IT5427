"""Order cleaning tests."""

from __future__ import annotations

import pandas as pd

from src.clean.orders import clean_orders


def test_orders_parse_timestamps_and_flags(small_orders):
    cleaned = clean_orders(small_orders)

    assert pd.api.types.is_datetime64_any_dtype(cleaned["order_purchase_timestamp"])
    assert cleaned.loc[cleaned["order_id"] == "o1", "is_delivered"].iloc[0]
    assert not cleaned.loc[cleaned["order_id"] == "o2", "is_delivered"].iloc[0]
    assert cleaned.loc[cleaned["order_id"] == "o3", "has_invalid_timestamp"].iloc[0]
    assert len(cleaned) == 3
