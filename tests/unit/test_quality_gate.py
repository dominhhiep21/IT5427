"""Quality gate tests."""

from __future__ import annotations

import pandas as pd
import pytest

from src.clean.customers import clean_customers
from src.clean.geolocation import clean_geolocation
from src.clean.items import clean_order_items
from src.clean.orders import clean_orders
from src.clean.payments import clean_payments
from src.clean.products import clean_products, clean_translation
from src.clean.reviews import clean_reviews
from src.clean.sellers import clean_sellers
from src.common.exceptions import QualityGateError
from src.quality.gate import QualityGate


def _datasets(
    small_orders,
    small_customers,
    small_sellers,
    small_products,
    small_translation,
    small_items,
    small_payments,
    small_reviews,
    small_geo,
):
    geo, _ = clean_geolocation(small_geo)
    return {
        "orders": clean_orders(small_orders),
        "customers": clean_customers(small_customers),
        "sellers": clean_sellers(small_sellers),
        "products": clean_products(small_products, small_translation),
        "translation": clean_translation(small_translation),
        "order_items": clean_order_items(small_items),
        "payments": clean_payments(small_payments),
        "reviews": clean_reviews(small_reviews),
        "geolocation_zip": geo,
    }


def test_incremental_gate_passes(
    small_orders,
    small_customers,
    small_sellers,
    small_products,
    small_translation,
    small_items,
    small_payments,
    small_reviews,
    small_geo,
):
    gate = QualityGate()
    report = gate.run(
        _datasets(
            small_orders,
            small_customers,
            small_sellers,
            small_products,
            small_translation,
            small_items,
            small_payments,
            small_reviews,
            small_geo,
        ),
        mode="incremental",
        run_id="test",
    )
    assert report.passed


def test_duplicate_order_fails(
    small_orders,
    small_customers,
    small_sellers,
    small_products,
    small_translation,
    small_items,
    small_payments,
    small_reviews,
    small_geo,
):
    datasets = _datasets(
        small_orders,
        small_customers,
        small_sellers,
        small_products,
        small_translation,
        small_items,
        small_payments,
        small_reviews,
        small_geo,
    )
    datasets["orders"] = pd.concat(
        [datasets["orders"], datasets["orders"].iloc[[0]]], ignore_index=True
    )
    report = QualityGate().run(datasets, mode="incremental", run_id="test")
    assert not report.passed
    with pytest.raises(QualityGateError):
        QualityGate().enforce(report)


def test_orphan_item_fails(
    small_orders,
    small_customers,
    small_sellers,
    small_products,
    small_translation,
    small_items,
    small_payments,
    small_reviews,
    small_geo,
):
    datasets = _datasets(
        small_orders,
        small_customers,
        small_sellers,
        small_products,
        small_translation,
        small_items,
        small_payments,
        small_reviews,
        small_geo,
    )
    datasets["order_items"].loc[0, "order_id"] = "missing"
    report = QualityGate().run(datasets, mode="incremental", run_id="test")
    assert not report.passed
