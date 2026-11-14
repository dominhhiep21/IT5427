"""Bộ mart tí hon dựng tay cho test phần phân tích (không phải test, chỉ là dữ liệu mẫu).

Sáu đơn hàng, đủ để mỗi cái bẫy xuất hiện đúng một lần và mọi KPI tính nhẩm được:

| Đơn | Khách (người) | Trạng thái | Dòng hàng                         | Giao           | Đánh giá |
|-----|---------------|------------|-----------------------------------|----------------|----------|
| o1  | c1 (u1, SP)   | delivered  | p1/s1 100+10, p2/s2 50+5 = 165    | đúng hạn, 5 ng | 5 rồi 4  |
| o2  | c2 (u1, SP)   | delivered  | p1/s1 200+20 = 220                | trễ, 15 ngày   | 1        |
| o3  | c3 (u2, RJ)   | delivered  | p2/s2 30+3 = 33                   | trễ trong ngày | 5        |
| o4  | c4 (u3, BA)   | delivered  | p2/s1 80+20 = 100                 | trễ, 25 ngày   | 2        |
| o5  | c5 (u4, BA)   | canceled   | p1/s1 500+50 = 550                | –              | 1        |
| o6  | c6 (u5, SP)   | delivered  | p3/s1 10+1 = 11                   | thiếu ngày giao| không có |

Doanh thu delivered = 165 + 220 + 33 + 100 + 11 = 529; 5 đơn delivered; AOV = 105,80.
o1 có 2 dòng hàng, 2 thanh toán, 2 đánh giá, 2 danh mục, 2 người bán: nguồn của mọi bẫy JOIN.
"""

from __future__ import annotations

import pandas as pd

from src.integrate.aggregates import Aggregator
from src.integrate.dimensions import DimensionBuilder

DELIVERED_REVENUE = 529.0
DELIVERED_ORDERS = 5


def _ts(value: str | None):
    return pd.Timestamp(value) if value else pd.NaT


def build_small_marts() -> dict[str, pd.DataFrame]:
    dim_customer = pd.DataFrame(
        [
            ("c1", "u1", 1000, "sao paulo", "sao paulo", "SP", "Sudeste"),
            ("c2", "u1", 1000, "sao paulo", "sao paulo", "SP", "Sudeste"),
            ("c3", "u2", 2000, "rio de janeiro", "rio de janeiro", "RJ", "Sudeste"),
            ("c4", "u3", 4000, "salvador", "salvador", "BA", "Nordeste"),
            ("c5", "u4", 4000, "salvador", "salvador", "BA", "Nordeste"),
            ("c6", "u5", 1000, "sao paulo", "sao paulo", "SP", "Sudeste"),
        ],
        columns=[
            "customer_id",
            "customer_unique_id",
            "zip_code_prefix",
            "city",
            "customer_city_normalized",
            "state",
            "region",
        ],
    )
    dim_product = pd.DataFrame(
        [
            ("p1", "cat_a", "category_a", False, False),
            ("p2", "cat_b", "category_b", False, False),
            ("p3", "unknown", "unknown", True, False),
        ],
        columns=["product_id", "category", "category_english", "category_missing", "translation_missing"],
    )
    dim_seller = pd.DataFrame(
        [
            ("s1", 1000, "sao paulo", "sao paulo", "SP", "Sudeste"),
            ("s2", 2000, "rio de janeiro", "rio de janeiro", "RJ", "Sudeste"),
        ],
        columns=["seller_id", "zip_code_prefix", "city", "seller_city_normalized", "state", "region"],
    )
    dim_geography = pd.DataFrame(
        [(1000, -23.5, -46.6, "sao paulo", "SP", "Sudeste")],
        columns=["zip_code_prefix", "lat_median", "lng_median", "city_mode", "state_mode", "region"],
    )
    dim_date = DimensionBuilder().build_date(pd.Timestamp("2017-01-01"), pd.Timestamp("2018-02-28"))

    orders = [
        # order, customer, ngày đặt, danh mục đại diện, trạng thái, ngày giao, ngày dự kiến, số ngày, trễ, có đánh giá
        ("o1", "c1", "2017-01-10", "cat_a", "delivered", "2017-01-15 10:00", "2017-01-20", 5.0, False, True),
        ("o2", "c2", "2017-02-10", "cat_a", "delivered", "2017-02-25 10:00", "2017-02-20", 15.0, True, True),
        ("o3", "c3", "2017-02-11", "cat_b", "delivered", "2017-02-19 10:00", "2017-02-19", 8.0, True, True),
        ("o4", "c4", "2018-01-05", "cat_b", "delivered", "2018-01-30 10:00", "2018-01-20", 25.0, True, True),
        ("o5", "c5", "2018-01-06", "cat_a", "canceled", None, "2018-01-25", None, False, True),
        ("o6", "c6", "2018-02-01", "unknown", "delivered", None, "2018-02-20", None, False, False),
    ]
    fact_orders = pd.DataFrame(
        [
            {
                "order_id": order_id,
                "customer_id": customer_id,
                "date_key": date_key,
                "category": category,
                "order_status": status,
                "is_delivered": status == "delivered",
                "order_delivered_customer_date": _ts(delivered),
                "order_estimated_delivery_date": _ts(estimated),
                "delivery_days": days,
                "is_late": late,
                "has_items": True,
                "has_payment": True,
                "has_review": has_review,
            }
            for order_id, customer_id, date_key, category, status, delivered, estimated, days, late, has_review in orders
        ]
    )
    fact_orders["delivery_days"] = fact_orders["delivery_days"].astype("float64")

    items = [
        ("o1", 1, "p1", "s1", 100.0, 10.0),
        ("o1", 2, "p2", "s2", 50.0, 5.0),
        ("o2", 1, "p1", "s1", 200.0, 20.0),
        ("o3", 1, "p2", "s2", 30.0, 3.0),
        ("o4", 1, "p2", "s1", 80.0, 20.0),
        ("o5", 1, "p1", "s1", 500.0, 50.0),
        ("o6", 1, "p3", "s1", 10.0, 1.0),
    ]
    order_lookup = fact_orders.set_index("order_id")
    fact_order_items = pd.DataFrame(
        [
            {
                "order_id": order_id,
                "order_item_id": item_id,
                "customer_id": order_lookup.loc[order_id, "customer_id"],
                "product_id": product_id,
                "seller_id": seller_id,
                "date_key": order_lookup.loc[order_id, "date_key"],
                "price": price,
                "freight_value": freight,
                "item_total": price + freight,
                "price_outlier": False,
                "order_status": order_lookup.loc[order_id, "order_status"],
                "is_delivered": bool(order_lookup.loc[order_id, "is_delivered"]),
            }
            for order_id, item_id, product_id, seller_id, price, freight in items
        ]
    )

    payments = [
        ("o1", 1, "credit_card", 3, 100.0),
        ("o1", 2, "voucher", 1, 65.0),
        ("o2", 1, "credit_card", 2, 225.0),
        ("o3", 1, "boleto", 1, 33.0),
        ("o4", 1, "credit_card", 1, 100.0),
        ("o5", 1, "boleto", 1, 550.0),
        ("o6", 1, "debit_card", 1, 11.0),
    ]
    fact_payments = pd.DataFrame(
        [
            {
                "order_id": order_id,
                "payment_sequential": sequential,
                "date_key": order_lookup.loc[order_id, "date_key"],
                "payment_type": payment_type,
                "payment_installments": installments,
                "payment_value": value,
            }
            for order_id, sequential, payment_type, installments, value in payments
        ]
    )

    reviews = [
        ("r1", "o1", "2017-01-16", 5, True),
        ("r2", "o1", "2017-01-17", 4, True),
        ("r3", "o2", "2017-02-26", 1, False),
        ("r4", "o3", "2017-02-20", 5, False),
        ("r5", "o4", "2018-01-31", 2, False),
        ("r6", "o5", "2018-01-26", 1, False),
    ]
    fact_reviews = pd.DataFrame(
        reviews, columns=["review_id", "order_id", "date_key", "review_score", "multiple_reviews_per_order"]
    )

    dims = {
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_seller": dim_seller,
        "dim_geography": dim_geography,
        "dim_date": dim_date,
    }
    facts = {
        "fact_order_items": fact_order_items,
        "fact_orders": fact_orders,
        "fact_payments": fact_payments,
        "fact_reviews": fact_reviews,
    }
    # Dùng chính Aggregator của pipeline để bảng aggregate nhất quán với fact như trong thực tế.
    return {**dims, **facts, **Aggregator().build_all(facts, dims)}


def build_small_sources(marts: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """CSV gốc tương ứng với bộ mart nhỏ: toàn chuỗi, ô trống cho giá trị thiếu."""

    orders = marts["fact_orders"]
    return {
        "olist_orders_dataset.csv": pd.DataFrame(
            {
                "order_id": orders["order_id"],
                "order_status": orders["order_status"],
                "order_delivered_customer_date": orders["order_delivered_customer_date"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "order_estimated_delivery_date": orders["order_estimated_delivery_date"].dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        ),
        "olist_order_items_dataset.csv": marts["fact_order_items"][
            ["order_id", "order_item_id", "price", "freight_value"]
        ],
        "olist_order_payments_dataset.csv": marts["fact_payments"][
            ["order_id", "payment_sequential", "payment_value"]
        ],
        "olist_order_reviews_dataset.csv": marts["fact_reviews"][["review_id", "order_id", "review_score"]],
    }


def write_small_warehouse(config, marts: dict[str, pd.DataFrame] | None = None, *, with_sources: bool = True):
    """Ghi bộ mart nhỏ ra Parquet (và CSV gốc) đúng chỗ `open_analysis_connection` sẽ đọc."""

    marts = marts if marts is not None else build_small_marts()
    config.marts_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in marts.items():
        frame.to_parquet(config.marts_dir / f"{name}.parquet", index=False)
    if with_sources:
        for file_name, frame in build_small_sources(marts).items():
            frame.to_csv(config.raw_csv_dir / file_name, index=False)
    return marts
