"""Build star-schema fact tables from cleaned U1 tables."""

from __future__ import annotations

import pandas as pd


class FactBuilder:
    def build_order_items(
        self, cleaned: dict[str, pd.DataFrame], dims: dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        items = cleaned["order_items"].copy()
        orders = cleaned["orders"][
            [
                "order_id",
                "customer_id",
                "order_purchase_timestamp",
                "order_status",
                "is_delivered",
            ]
        ]
        out = items.merge(orders, on="order_id", how="left")
        out["date_key"] = pd.to_datetime(
            out["order_purchase_timestamp"]
        ).dt.strftime("%Y-%m-%d")
        out["item_total"] = out["price"].fillna(0) + out["freight_value"].fillna(0)
        return out[
            [
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
            ]
        ]

    def _dominant_category(self, cleaned: dict[str, pd.DataFrame]) -> pd.DataFrame:
        items = cleaned["order_items"][["order_id", "product_id", "price", "freight_value"]].copy()
        products = cleaned["products"][
            ["product_id", "product_category_name", "category_missing"]
        ]
        items = items.merge(products, on="product_id", how="left")
        items["item_total"] = items["price"].fillna(0) + items["freight_value"].fillna(0)
        totals = (
            items.groupby(
                ["order_id", "product_category_name", "category_missing"],
                dropna=False,
            )["item_total"]
            .sum()
            .reset_index()
        )
        dominant = (
            totals.sort_values(
                ["order_id", "category_missing", "item_total", "product_category_name"],
                ascending=[True, True, False, True],
            )
            .drop_duplicates("order_id")[["order_id", "product_category_name"]]
            .rename(columns={"product_category_name": "category"})
        )
        return dominant

    def build_orders(
        self, cleaned: dict[str, pd.DataFrame], dims: dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        orders = cleaned["orders"].copy()
        orders["date_key"] = pd.to_datetime(
            orders["order_purchase_timestamp"]
        ).dt.strftime("%Y-%m-%d")
        delivered = pd.to_datetime(orders["order_delivered_customer_date"])
        estimated = pd.to_datetime(orders["order_estimated_delivery_date"])
        purchase = pd.to_datetime(orders["order_purchase_timestamp"])
        orders["delivery_days"] = (
            (delivered - purchase).dt.total_seconds() / 86400
        ).round(2)
        orders["is_late"] = (
            orders["is_delivered"].fillna(False)
            & delivered.notna()
            & (delivered > estimated)
        )
        orders["has_items"] = orders["order_id"].isin(
            cleaned["order_items"]["order_id"]
        )
        orders["has_payment"] = orders["order_id"].isin(
            cleaned["payments"]["order_id"]
        )
        orders["has_review"] = orders["order_id"].isin(cleaned["reviews"]["order_id"])

        dominant = self._dominant_category(cleaned)
        orders = orders.merge(dominant, on="order_id", how="left")
        orders["category"] = orders["category"].fillna("unknown")

        return orders[
            [
                "order_id",
                "customer_id",
                "date_key",
                "category",
                "order_status",
                "is_delivered",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
                "delivery_days",
                "is_late",
                "has_items",
                "has_payment",
                "has_review",
            ]
        ]

    def build_payments(
        self, cleaned: dict[str, pd.DataFrame], dims: dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        payments = cleaned["payments"].copy()
        orders = cleaned["orders"][["order_id", "order_purchase_timestamp"]]
        out = payments.merge(orders, on="order_id", how="left")
        out["date_key"] = pd.to_datetime(
            out["order_purchase_timestamp"]
        ).dt.strftime("%Y-%m-%d")
        return out[
            [
                "order_id",
                "payment_sequential",
                "date_key",
                "payment_type",
                "payment_installments",
                "payment_value",
            ]
        ]

    def build_reviews(
        self, cleaned: dict[str, pd.DataFrame], dims: dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        reviews = cleaned["reviews"].copy()
        reviews["date_key"] = pd.to_datetime(
            reviews["review_creation_date"]
        ).dt.strftime("%Y-%m-%d")
        return reviews[
            [
                "review_id",
                "order_id",
                "date_key",
                "review_score",
                "multiple_reviews_per_order",
            ]
        ]

    def build_all(
        self, cleaned: dict[str, pd.DataFrame], dims: dict[str, pd.DataFrame]
    ) -> dict[str, pd.DataFrame]:
        return {
            "fact_order_items": self.build_order_items(cleaned, dims),
            "fact_orders": self.build_orders(cleaned, dims),
            "fact_payments": self.build_payments(cleaned, dims),
            "fact_reviews": self.build_reviews(cleaned, dims),
        }
