"""Ba cột mart mới: hai mốc thời gian trên fact_orders, seller_state trên fact_order_items."""

from __future__ import annotations

import pandas as pd

from src.integrate.dimensions import DimensionBuilder
from src.integrate.facts import FactBuilder


def _cleaned() -> dict[str, pd.DataFrame]:
    orders = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "customer_id": ["c1", "c2", "c3"],
            "order_purchase_timestamp": pd.to_datetime(["2017-01-01", "2017-02-01", "2017-03-01"]),
            "order_status": ["delivered", "delivered", "delivered"],
            "is_delivered": [True, True, True],
            "order_delivered_customer_date": pd.to_datetime(["2017-01-10", "2017-02-10", "2017-03-10"]),
            "order_estimated_delivery_date": pd.to_datetime(["2017-01-20", "2017-02-20", "2017-03-20"]),
            "order_approved_at": pd.to_datetime(["2017-01-01", None, "2017-03-02"]),
            "order_delivered_carrier_date": pd.to_datetime(["2017-01-05", "2017-02-06", None]),
        }
    )
    sellers = pd.DataFrame(
        {
            "seller_id": ["s1", "s2"],
            "seller_zip_code_prefix": [1001, 2002],
            "seller_city": ["sao paulo", "rio de janeiro"],
            "seller_city_normalized": ["sao paulo", "rio de janeiro"],
            "seller_state": ["SP", "RJ"],
        }
    )
    order_items = pd.DataFrame(
        {
            "order_id": ["o1", "o2", "o3"],
            "order_item_id": [1, 1, 1],
            "product_id": ["p1", "p1", "p2"],
            "seller_id": ["s1", "s2", "s9"],
            "price": [100.0, 50.0, 10.0],
            "freight_value": [10.0, 5.0, 1.0],
            "price_outlier": [False, False, False],
        }
    )
    products = pd.DataFrame(
        {
            "product_id": ["p1", "p2"],
            "product_category_name": ["brinquedos", "livros"],
            "category_missing": [False, False],
        }
    )
    payments = pd.DataFrame({"order_id": ["o1", "o2", "o3"]})
    reviews = pd.DataFrame({"order_id": ["o1"]})
    customers = pd.DataFrame(
        {
            "customer_id": ["c1", "c2", "c3"],
            "customer_unique_id": ["u1", "u2", "u3"],
            "customer_zip_code_prefix": [1001, 2002, 3003],
            "customer_city": ["sao paulo", "rio de janeiro", "bh"],
            "customer_city_normalized": ["sao paulo", "rio de janeiro", "bh"],
            "customer_state": ["SP", "RJ", "MG"],
        }
    )
    geolocation_zip = pd.DataFrame(
        {
            "zip_code_prefix": [1001, 2002, 3003],
            "lat_median": [-23.5, -22.9, -19.9],
            "lng_median": [-46.6, -43.2, -43.9],
            "city_mode": ["sao paulo", "rio de janeiro", "bh"],
            "state_mode": ["SP", "RJ", "MG"],
        }
    )
    return {
        "orders": orders,
        "sellers": sellers,
        "order_items": order_items,
        "products": products,
        "payments": payments,
        "reviews": reviews,
        "customers": customers,
        "geolocation_zip": geolocation_zip,
    }


def _dims(cleaned: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    region_map = pd.DataFrame({"state": ["SP", "RJ"], "region": ["Sudeste", "Sudeste"]})
    return {"dim_seller": DimensionBuilder().build_seller(cleaned["sellers"], region_map)}


def test_fact_orders_has_both_timestamps() -> None:
    cleaned = _cleaned()
    fact_orders = FactBuilder().build_orders(cleaned, _dims(cleaned))
    assert "order_approved_at" in fact_orders.columns
    assert "order_delivered_carrier_date" in fact_orders.columns


def test_fact_orders_row_count_unchanged() -> None:
    cleaned = _cleaned()
    fact_orders = FactBuilder().build_orders(cleaned, _dims(cleaned))
    assert len(fact_orders) == len(cleaned["orders"])


def test_fact_order_items_has_seller_state() -> None:
    cleaned = _cleaned()
    fact_items = FactBuilder().build_order_items(cleaned, _dims(cleaned))
    assert "seller_state" in fact_items.columns


def test_fact_order_items_has_no_bare_state_column() -> None:
    cleaned = _cleaned()
    fact_items = FactBuilder().build_order_items(cleaned, _dims(cleaned))
    assert "state" not in fact_items.columns


def test_fact_order_items_row_count_unchanged() -> None:
    cleaned = _cleaned()
    fact_items = FactBuilder().build_order_items(cleaned, _dims(cleaned))
    assert len(fact_items) == len(cleaned["order_items"])


def test_new_timestamp_columns_are_nullable_timestamps() -> None:
    cleaned = _cleaned()
    fact_orders = FactBuilder().build_orders(cleaned, _dims(cleaned))
    for column in ("order_approved_at", "order_delivered_carrier_date"):
        assert pd.api.types.is_datetime64_any_dtype(fact_orders[column])
        assert fact_orders[column].isna().any(), f"{column} phải giữ được giá trị thiếu"


def test_existing_columns_still_present() -> None:
    cleaned = _cleaned()
    dims = _dims(cleaned)
    facts = {
        "fact_orders": FactBuilder().build_orders(cleaned, dims),
        "fact_order_items": FactBuilder().build_order_items(cleaned, dims),
    }
    assert {
        "order_id",
        "customer_id",
        "date_key",
        "category",
        "order_status",
        "is_delivered",
        "delivery_days",
        "is_late",
        "has_items",
        "has_payment",
        "has_review",
    }.issubset(facts["fact_orders"].columns)
    assert {
        "order_id",
        "order_item_id",
        "customer_id",
        "product_id",
        "seller_id",
        "date_key",
        "price",
        "freight_value",
        "item_total",
        "price_outlier",
        "order_status",
        "is_delivered",
    }.issubset(facts["fact_order_items"].columns)
