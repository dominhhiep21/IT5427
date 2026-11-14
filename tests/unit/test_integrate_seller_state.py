"""seller_state phải đến từ dim_seller.state, không từ địa chỉ khách, và không làm mất dòng."""

from __future__ import annotations

import pandas as pd

from src.integrate.dimensions import DimensionBuilder
from src.integrate.facts import FactBuilder


def _cleaned(seller_ids: list[str]) -> dict[str, pd.DataFrame]:
    orders = pd.DataFrame(
        {
            "order_id": [f"o{index}" for index in range(len(seller_ids))],
            "customer_id": ["c1"] * len(seller_ids),
            "order_purchase_timestamp": pd.to_datetime(["2017-01-01"] * len(seller_ids)),
            "order_status": ["delivered"] * len(seller_ids),
            "is_delivered": [True] * len(seller_ids),
            "order_delivered_customer_date": pd.to_datetime(["2017-01-10"] * len(seller_ids)),
            "order_estimated_delivery_date": pd.to_datetime(["2017-01-20"] * len(seller_ids)),
            "order_approved_at": pd.to_datetime(["2017-01-01"] * len(seller_ids)),
            "order_delivered_carrier_date": pd.to_datetime(["2017-01-05"] * len(seller_ids)),
        }
    )
    sellers = pd.DataFrame(
        {
            "seller_id": ["s1"],
            "seller_zip_code_prefix": [1001],
            "seller_city": ["sao paulo"],
            "seller_city_normalized": ["sao paulo"],
            "seller_state": ["SP"],
        }
    )
    order_items = pd.DataFrame(
        {
            "order_id": [f"o{index}" for index in range(len(seller_ids))],
            "order_item_id": [1] * len(seller_ids),
            "product_id": ["p1"] * len(seller_ids),
            "seller_id": seller_ids,
            "price": [10.0] * len(seller_ids),
            "freight_value": [1.0] * len(seller_ids),
            "price_outlier": [False] * len(seller_ids),
        }
    )
    products = pd.DataFrame(
        {
            "product_id": ["p1"],
            "product_category_name": ["brinquedos"],
            "category_missing": [False],
        }
    )
    return {
        "orders": orders,
        "sellers": sellers,
        "order_items": order_items,
        "products": products,
        "payments": pd.DataFrame({"order_id": orders["order_id"]}),
        "reviews": pd.DataFrame({"order_id": orders["order_id"]}),
        "customers": pd.DataFrame(
            {
                "customer_id": ["c1"] * len(seller_ids),
                "customer_unique_id": ["u1"] * len(seller_ids),
                "customer_zip_code_prefix": [1001] * len(seller_ids),
                "customer_city": ["sao paulo"] * len(seller_ids),
                "customer_city_normalized": ["sao paulo"] * len(seller_ids),
                "customer_state": ["RJ"] * len(seller_ids),
            }
        ),
        "geolocation_zip": pd.DataFrame(
            {
                "zip_code_prefix": [1001],
                "lat_median": [-23.5],
                "lng_median": [-46.6],
                "city_mode": ["sao paulo"],
                "state_mode": ["SP"],
            }
        ),
    }


def _build(seller_ids: list[str]) -> pd.DataFrame:
    cleaned = _cleaned(seller_ids)
    region_map = pd.DataFrame({"state": ["SP"], "region": ["Sudeste"]})
    dims = {"dim_seller": DimensionBuilder().build_seller(cleaned["sellers"], region_map)}
    return FactBuilder().build_order_items(cleaned, dims)


def test_seller_state_comes_from_dim_seller() -> None:
    fact_items = _build(["s1"])
    assert fact_items.loc[0, "seller_state"] == "SP"


def test_unknown_seller_yields_null_without_raising() -> None:
    fact_items = _build(["s9"])
    assert pd.isna(fact_items.loc[0, "seller_state"])


def test_unknown_seller_keeps_the_row() -> None:
    fact_items = _build(["s9"])
    assert len(fact_items) == 1


def test_join_does_not_multiply_rows() -> None:
    fact_items = _build(["s1", "s9"])
    assert len(fact_items) == 2


def test_seller_state_is_two_uppercase_letters_when_present() -> None:
    fact_items = _build(["s1"])
    value = str(fact_items.loc[0, "seller_state"])
    assert len(value) == 2 and value.isupper() and value.isalpha()
