"""Shared pytest fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.clean.customers import clean_customers
from src.clean.geolocation import clean_geolocation
from src.clean.items import clean_order_items
from src.clean.orders import clean_orders
from src.clean.payments import clean_payments
from src.clean.products import clean_products, clean_translation
from src.clean.reviews import clean_reviews
from src.clean.sellers import clean_sellers
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.config import load_config


@pytest.fixture
def config(tmp_path: Path):
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
paths:
  raw_csv_dir: dataset
  data_dir: data
  reports_dir: data/reports
  logs_dir: logs
  temp_dir: data/.tmp
parquet:
  compression: snappy
geolocation:
  lat_min: -34.0
  lat_max: 6.0
  lng_min: -74.0
  lng_max: -34.0
quality:
  iqr_multiplier: 1.5
  memory_warn_mb: 1536
  memory_fail_mb: 2048
""",
        encoding="utf-8",
    )
    return load_config(config_path)


@pytest.fixture
def real_config(tmp_path: Path):
    dataset = ROOT / "dataset"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
paths:
  raw_csv_dir: "{dataset.as_posix()}"
  data_dir: data
  marts_dir: data/marts
  reports_dir: data/reports
  logs_dir: logs
  temp_dir: data/.tmp
  duckdb_path: warehouse/olist.duckdb
  ibge_dir: "{(ROOT / 'dataset' / 'external' / 'ibge').as_posix()}"
parquet:
  compression: snappy
geolocation:
  lat_min: -34.0
  lat_max: 6.0
  lng_min: -74.0
  lng_max: -34.0
quality:
  iqr_multiplier: 1.5
  memory_warn_mb: 1536
  memory_fail_mb: 2048
""",
        encoding="utf-8",
    )
    return load_config(config_path)


@pytest.fixture
def run(config):
    return new_run_context("test", config.logs_dir, config.temp_dir)


@pytest.fixture
def writer(run, config):
    return AtomicWriter(run, config.parquet_compression)


@pytest.fixture
def logger(run):
    return JsonLogger(run, console=False)


@pytest.fixture
def small_orders() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "order_id": "o1",
                "customer_id": "c1",
                "order_status": "delivered",
                "order_purchase_timestamp": "2017-01-01 10:00:00",
                "order_approved_at": "2017-01-01 11:00:00",
                "order_delivered_carrier_date": "2017-01-02 10:00:00",
                "order_delivered_customer_date": "2017-01-07 10:00:00",
                "order_estimated_delivery_date": "2017-01-06 10:00:00",
            },
            {
                "order_id": "o2",
                "customer_id": "c2",
                "order_status": "canceled",
                "order_purchase_timestamp": "2017-02-01 10:00:00",
                "order_approved_at": None,
                "order_delivered_carrier_date": None,
                "order_delivered_customer_date": None,
                "order_estimated_delivery_date": "2017-02-10 10:00:00",
            },
            {
                "order_id": "o3",
                "customer_id": "c1",
                "order_status": "shipped",
                "order_purchase_timestamp": "2017-03-01 10:00:00",
                "order_approved_at": "not-a-date",
                "order_delivered_carrier_date": None,
                "order_delivered_customer_date": None,
                "order_estimated_delivery_date": "2017-03-10 10:00:00",
            },
        ]
    )


@pytest.fixture
def small_customers() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "customer_id": "c1",
                "customer_unique_id": "u1",
                "customer_zip_code_prefix": "100",
                "customer_city": " Sao  Paulo ",
                "customer_state": "sp",
            },
            {
                "customer_id": "c2",
                "customer_unique_id": "u2",
                "customer_zip_code_prefix": "200",
                "customer_city": "Rio",
                "customer_state": "rj",
            },
        ]
    )


@pytest.fixture
def small_sellers() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "seller_id": "s1",
                "seller_zip_code_prefix": "100",
                "seller_city": "Sao Paulo",
                "seller_state": "sp",
            }
        ]
    )


@pytest.fixture
def small_products() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "product_id": "p1",
                "product_category_name": "cama_mesa_banho",
                "product_name_lenght": "10",
                "product_description_lenght": "20",
                "product_photos_qty": "1",
                "product_weight_g": "100",
                "product_length_cm": "10",
                "product_height_cm": "5",
                "product_width_cm": "4",
            },
            {
                "product_id": "p2",
                "product_category_name": None,
                "product_name_lenght": None,
                "product_description_lenght": None,
                "product_photos_qty": None,
                "product_weight_g": None,
                "product_length_cm": None,
                "product_height_cm": None,
                "product_width_cm": None,
            },
            {
                "product_id": "p3",
                "product_category_name": "pc_gamer",
                "product_name_lenght": "10",
                "product_description_lenght": "20",
                "product_photos_qty": "1",
                "product_weight_g": "100",
                "product_length_cm": "10",
                "product_height_cm": "5",
                "product_width_cm": "4",
            },
        ]
    )


@pytest.fixture
def small_translation() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "product_category_name": "cama_mesa_banho",
                "product_category_name_english": "bed_bath_table",
            }
        ]
    )


@pytest.fixture
def small_items() -> pd.DataFrame:
    rows = [
        ("o1", 1, "p1", "s1", "2017-01-02 10:00:00", "10", "1"),
        ("o1", 2, "p2", "s1", "2017-01-02 10:00:00", "12", "1"),
        ("o2", 1, "p1", "s1", "2017-02-02 10:00:00", "11", "1"),
        ("o2", 2, "p3", "s1", "2017-02-02 10:00:00", "13", "1"),
        ("o3", 1, "p1", "s1", "2017-03-02 10:00:00", "1000", "1"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ],
    )


@pytest.fixture
def small_payments() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("o1", 1, "credit_card", 1, "11"),
            ("o2", 1, "boleto", 1, "24"),
            ("o3", 1, "voucher", 1, "1001"),
        ],
        columns=[
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ],
    )


@pytest.fixture
def small_reviews() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("r1", "o1", 5, None, None, "2017-01-06", "2017-01-07"),
            ("r2", "o1", 4, "ok", "good", "2017-01-06", "2017-01-07"),
            ("r3", "o2", 1, None, "bad", "2017-02-11", "2017-02-12"),
        ],
        columns=[
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ],
    )


@pytest.fixture
def small_geo() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("100", "-23.5", "-46.6", "Sao Paulo", "SP"),
            ("100", "-23.5", "-46.6", "Sao Paulo", "SP"),
            ("100", "-23.6", "-46.5", "sao paulo", "sp"),
            ("100", "-23.7", "-46.4", "Campinas", "SP"),
            ("200", "45.0", "-46.0", "Rio de Janeiro", "RJ"),
            ("300", "-22.0", "-43.0", "Rio de Janeiro", "RJ"),
        ],
        columns=[
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ],
    )


@pytest.fixture
def region_map() -> pd.DataFrame:
    raw = json.loads(
        (ROOT / "dataset" / "external" / "ibge" / "estados.json").read_text(
            encoding="utf-8"
        )
    )
    return pd.DataFrame(
        [
            {
                "state": item["sigla"].upper(),
                "region": item["regiao"]["nome"],
            }
            for item in raw
        ]
    ).sort_values("state").reset_index(drop=True)


@pytest.fixture
def small_cleaned(
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
    translation = clean_translation(small_translation)
    geo, _ = clean_geolocation(small_geo)
    return {
        "translation": translation,
        "customers": clean_customers(small_customers),
        "sellers": clean_sellers(small_sellers),
        "products": clean_products(small_products, translation),
        "orders": clean_orders(small_orders),
        "order_items": clean_order_items(small_items),
        "payments": clean_payments(small_payments),
        "reviews": clean_reviews(small_reviews),
        "geolocation_zip": geo,
    }
