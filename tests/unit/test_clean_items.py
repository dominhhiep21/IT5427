"""Order item cleaning tests."""

from __future__ import annotations

from src.clean.items import clean_order_items


def test_price_outlier_flag_keeps_rows(small_items):
    cleaned = clean_order_items(small_items, iqr_multiplier=1.5)

    assert len(cleaned) == len(small_items)
    assert bool(cleaned.loc[cleaned["price"] == 1000, "price_outlier"].iloc[0]) is True
    assert bool(cleaned.loc[cleaned["price"] == 10, "price_outlier"].iloc[0]) is False
