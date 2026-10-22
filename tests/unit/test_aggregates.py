"""Aggregate builder tests."""

from __future__ import annotations

from src.integrate.aggregates import Aggregator
from src.integrate.dimensions import DimensionBuilder
from src.integrate.facts import FactBuilder


def test_aggregates_small(small_cleaned, region_map):
    dims = DimensionBuilder().build_all(small_cleaned, region_map)
    facts = FactBuilder().build_all(small_cleaned, dims)
    aggs = Aggregator().build_all(facts, dims)

    sales = aggs["agg_sales_daily"]
    delivery = aggs["agg_delivery_daily"]

    assert sales["revenue"].sum() == 24
    assert sales["orders"].max() == 1
    assert delivery["delivered_orders"].sum() == 1
    assert delivery["late_orders"].sum() == 1
    assert delivery["delivery_days_sum"].sum() == 6
