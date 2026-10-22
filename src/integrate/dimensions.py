"""Build star-schema dimensions from cleaned U1 tables."""

from __future__ import annotations

import pandas as pd

from src.external.region import RegionMapper


class DimensionBuilder:
    def build_customer(self, customers: pd.DataFrame, region_map: pd.DataFrame) -> pd.DataFrame:
        out = customers[
            [
                "customer_id",
                "customer_unique_id",
                "customer_zip_code_prefix",
                "customer_city",
                "customer_city_normalized",
                "customer_state",
            ]
        ].copy()
        out = out.rename(
            columns={
                "customer_zip_code_prefix": "zip_code_prefix",
                "customer_city": "city",
                "customer_state": "state",
            }
        )
        return RegionMapper.attach(out, "state", region_map)

    def build_product(self, products: pd.DataFrame) -> pd.DataFrame:
        return products[
            [
                "product_id",
                "product_category_name",
                "product_category_name_english",
                "category_missing",
                "translation_missing",
            ]
        ].rename(
            columns={
                "product_category_name": "category",
                "product_category_name_english": "category_english",
            }
        ).copy()

    def build_seller(self, sellers: pd.DataFrame, region_map: pd.DataFrame) -> pd.DataFrame:
        out = sellers[
            [
                "seller_id",
                "seller_zip_code_prefix",
                "seller_city",
                "seller_city_normalized",
                "seller_state",
            ]
        ].copy()
        out = out.rename(
            columns={
                "seller_zip_code_prefix": "zip_code_prefix",
                "seller_city": "city",
                "seller_state": "state",
            }
        )
        return RegionMapper.attach(out, "state", region_map)

    def build_geography(self, geo: pd.DataFrame, region_map: pd.DataFrame) -> pd.DataFrame:
        out = geo[
            [
                "zip_code_prefix",
                "lat_median",
                "lng_median",
                "city_mode",
                "state_mode",
            ]
        ].copy()
        out = RegionMapper.attach(out, "state_mode", region_map)
        return out

    def build_date(self, min_date: pd.Timestamp, max_date: pd.Timestamp) -> pd.DataFrame:
        dates = pd.date_range(min_date.normalize(), max_date.normalize(), freq="D")
        frame = pd.DataFrame({"date": dates})
        frame["date_key"] = frame["date"].dt.strftime("%Y-%m-%d")
        frame["year"] = frame["date"].dt.year
        frame["quarter"] = frame["date"].dt.quarter
        frame["month"] = frame["date"].dt.month
        frame["day"] = frame["date"].dt.day
        frame["weekday"] = frame["date"].dt.weekday
        frame["is_sparse_period"] = frame["year"] == 2016
        return frame[
            [
                "date_key",
                "date",
                "year",
                "quarter",
                "month",
                "day",
                "weekday",
                "is_sparse_period",
            ]
        ]

    def build_all(
        self,
        cleaned: dict[str, pd.DataFrame],
        region_map: pd.DataFrame,
    ) -> dict[str, pd.DataFrame]:
        orders = cleaned["orders"]
        min_date = pd.to_datetime(orders["order_purchase_timestamp"]).min()
        max_date = pd.to_datetime(orders["order_purchase_timestamp"]).max()
        return {
            "dim_customer": self.build_customer(cleaned["customers"], region_map),
            "dim_product": self.build_product(cleaned["products"]),
            "dim_seller": self.build_seller(cleaned["sellers"], region_map),
            "dim_geography": self.build_geography(
                cleaned["geolocation_zip"], region_map
            ),
            "dim_date": self.build_date(min_date, max_date),
        }
