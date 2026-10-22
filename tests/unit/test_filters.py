"""Analytics filter re-export test."""

from __future__ import annotations

from src.analytics.filters import KpiFilters


def test_default_filter_status():
    assert KpiFilters().order_status == "delivered"
