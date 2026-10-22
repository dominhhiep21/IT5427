"""Product and category cleaning tests."""

from __future__ import annotations

from src.clean.products import clean_products


def test_category_fallback_and_translation_flag(small_products, small_translation):
    cleaned = clean_products(small_products, small_translation)

    p2 = cleaned.loc[cleaned["product_id"] == "p2"].iloc[0]
    p3 = cleaned.loc[cleaned["product_id"] == "p3"].iloc[0]
    p1 = cleaned.loc[cleaned["product_id"] == "p1"].iloc[0]

    assert p2["product_category_name"] == "unknown"
    assert bool(p2["category_missing"]) is True
    assert bool(p2["translation_missing"]) is False
    assert p3["product_category_name"] == "pc_gamer"
    assert bool(p3["category_missing"]) is False
    assert bool(p3["translation_missing"]) is True
    assert p1["product_category_name_english"] == "bed_bath_table"
    assert len(cleaned) == 3
