"""Review cleaning tests."""

from __future__ import annotations

from src.clean.reviews import clean_reviews


def test_multiple_reviews_flag(small_reviews):
    cleaned = clean_reviews(small_reviews)

    o1 = cleaned.loc[cleaned["order_id"] == "o1", "multiple_reviews_per_order"]
    o2 = cleaned.loc[cleaned["order_id"] == "o2", "multiple_reviews_per_order"]
    assert o1.all()
    assert not o2.any()
    assert len(cleaned) == 3
