"""Dimension builder tests."""

from __future__ import annotations

from src.integrate.dimensions import DimensionBuilder


def test_dimensions_small(small_cleaned, region_map):
    dims = DimensionBuilder().build_all(small_cleaned, region_map)

    assert len(dims["dim_customer"]) == 2
    assert len(dims["dim_seller"]) == 1
    assert len(dims["dim_product"]) == 3
    assert len(dims["dim_geography"]) == 3
    assert len(dims["dim_date"]) == 60
    assert set(dims["dim_customer"]["region"]) == {"Sudeste"}
    assert dims["dim_date"]["is_sparse_period"].sum() == 0
    assert dims["dim_date"]["date_key"].iloc[0] == "2017-01-01"
    assert dims["dim_date"]["date_key"].iloc[-1] == "2017-03-01"
