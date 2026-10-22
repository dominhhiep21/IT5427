"""Fact builder tests."""

from __future__ import annotations

from src.integrate.dimensions import DimensionBuilder
from src.integrate.facts import FactBuilder


def test_facts_small(small_cleaned, region_map):
    dims = DimensionBuilder().build_all(small_cleaned, region_map)
    facts = FactBuilder().build_all(small_cleaned, dims)

    items = facts["fact_order_items"]
    orders = facts["fact_orders"]
    payments = facts["fact_payments"]
    reviews = facts["fact_reviews"]

    assert len(items) == 5
    assert len(orders) == 3
    assert len(payments) == 3
    assert len(reviews) == 3

    first = items.loc[items["order_id"] == "o1"].iloc[0]
    assert first["item_total"] == 11
    assert first["is_delivered"]

    o1 = orders.loc[orders["order_id"] == "o1"].iloc[0]
    assert bool(o1["is_late"]) is True
    assert o1["delivery_days"] == 6.0
    assert bool(o1["has_items"]) is True
    assert bool(o1["has_payment"]) is True
    assert bool(o1["has_review"]) is True
    assert o1["category"] == "cama_mesa_banho"
