"""Build daily pre-aggregates for dashboard filters."""

from __future__ import annotations

import pandas as pd


class Aggregator:
    def build_sales(
        self,
        fact_items: pd.DataFrame,
        fact_orders: pd.DataFrame,
        dims: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        frame = fact_items.merge(
            dims["dim_customer"][["customer_id", "state", "region"]],
            on="customer_id",
            how="left",
        ).merge(
            dims["dim_product"][["product_id", "category"]],
            on="product_id",
            how="left",
        )
        frame = frame[frame["is_delivered"].fillna(False)].copy()
        frame["is_sparse_period"] = pd.to_datetime(frame["date_key"]).dt.year == 2016
        out = (
            frame.groupby(
                ["date_key", "state", "region", "category", "is_sparse_period"],
                dropna=False,
            )
            .agg(
                revenue=("item_total", "sum"),
                orders=("order_id", "nunique"),
                items=("order_id", "size"),
                freight=("freight_value", "sum"),
            )
            .reset_index()
        )
        out["revenue"] = out["revenue"].round(2)
        out["freight"] = out["freight"].round(2)
        return out.sort_values(
            ["date_key", "state", "region", "category"]
        ).reset_index(drop=True)

    def build_delivery(
        self,
        fact_orders: pd.DataFrame,
        dims: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:
        frame = fact_orders.merge(
            dims["dim_customer"][["customer_id", "state", "region"]],
            on="customer_id",
            how="left",
        )
        frame = frame[frame["is_delivered"].fillna(False)].copy()
        frame["is_sparse_period"] = pd.to_datetime(frame["date_key"]).dt.year == 2016
        out = (
            frame.groupby(
                ["date_key", "state", "region", "category", "is_sparse_period"],
                dropna=False,
            )
            .agg(
                delivered_orders=("order_id", "size"),
                late_orders=("is_late", "sum"),
                delivery_days_sum=("delivery_days", "sum"),
            )
            .reset_index()
        )
        out["late_orders"] = out["late_orders"].astype(int)
        out["delivery_days_sum"] = out["delivery_days_sum"].round(2)
        return out.sort_values(
            ["date_key", "state", "region", "category"]
        ).reset_index(drop=True)

    def build_all(
        self,
        facts: dict[str, pd.DataFrame],
        dims: dict[str, pd.DataFrame],
    ) -> dict[str, pd.DataFrame]:
        return {
            "agg_sales_daily": self.build_sales(
                facts["fact_order_items"], facts["fact_orders"], dims
            ),
            "agg_delivery_daily": self.build_delivery(
                facts["fact_orders"], dims
            ),
        }
