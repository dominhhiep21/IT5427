"""Baseline checks against the real Olist CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.clean.geolocation import clean_geolocation
from src.clean.items import clean_order_items
from src.clean.products import clean_products, clean_translation

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "dataset"


@pytest.mark.slow
def test_geolocation_baseline():
    raw = pd.read_csv(DATASET / "olist_geolocation_dataset.csv", dtype=str)
    cleaned, stats = clean_geolocation(raw)

    assert len(cleaned) == 19_015
    assert stats.raw_rows == 1_000_163
    assert stats.deduped_rows == 738_332
    assert stats.outside_bbox == 42
    assert stats.zips_without_coord == 5
    assert stats.multi_city_zips == 8_555


@pytest.mark.slow
def test_category_baseline():
    products = pd.read_csv(DATASET / "olist_products_dataset.csv", dtype=str)
    translation = pd.read_csv(
        DATASET / "product_category_name_translation.csv", dtype=str
    )
    cleaned = clean_products(products, clean_translation(translation))

    assert len(cleaned) == 32_951
    assert int(cleaned["category_missing"].sum()) == 610
    assert int(cleaned["translation_missing"].sum()) == 13
    assert cleaned.loc[
        cleaned["translation_missing"], "product_category_name"
    ].nunique() == 2


@pytest.mark.slow
def test_price_outlier_baseline():
    items = pd.read_csv(DATASET / "olist_order_items_dataset.csv", dtype=str)
    cleaned = clean_order_items(items)
    assert len(cleaned) == 112_650
    assert int(cleaned["price_outlier"].sum()) == 8_427
