"""Unit tests for the evidence index built from the source CSVs (BR4.1, BR4.4, BR4.9)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.common.exceptions import SchemaError
from src.linkage.index import build_index, evidence_for

CUSTOMERS_HEADER = "customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state"
SELLERS_HEADER = "seller_id,seller_zip_code_prefix,seller_city,seller_state"
ORDERS_HEADER = (
    "order_id,customer_id,order_status,order_purchase_timestamp,"
    "order_approved_at,order_delivered_carrier_date,"
    "order_delivered_customer_date,order_estimated_delivery_date"
)
ITEMS_HEADER = "order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value"
PAYMENTS_HEADER = "order_id,payment_sequential,payment_type,payment_installments,payment_value"


def _write(config, name: str, header: str, rows: list[str]) -> None:
    text = header + "\n" + "".join(f"{row}\n" for row in rows)
    (Path(config.raw_csv_dir) / name).write_text(text, encoding="utf-8")


def _write_base(config, customers: list[str], orders: list[str], items: list[str], payments: list[str]) -> None:
    _write(config, "olist_customers_dataset.csv", CUSTOMERS_HEADER, customers)
    _write(config, "olist_orders_dataset.csv", ORDERS_HEADER, orders)
    _write(config, "olist_order_items_dataset.csv", ITEMS_HEADER, items)
    _write(config, "olist_order_payments_dataset.csv", PAYMENTS_HEADER, payments)


def test_build_index_collects_products_and_payments_per_customer(config):
    _write_base(
        config,
        customers=[
            "c1,u1,01310,São Paulo,SP",
            "c2,u2,01310,Sao Paulo,SP",
        ],
        orders=[
            "o1,c1,delivered,2017-01-01 10:00:00,,,,",
            "o2,c1,delivered,2017-02-01 10:00:00,,,,",
            "o3,c2,delivered,2017-03-01 10:00:00,,,,",
        ],
        items=[
            "o1,1,p1,s1,2017-01-05,10.0,1.0",
            "o1,2,p2,s1,2017-01-05,20.0,1.0",
            "o2,1,p3,s2,2017-02-05,30.0,1.0",
            "o3,1,p4,s2,2017-03-05,40.0,1.0",
        ],
        payments=[
            "o1,1,credit_card,1,31.0",
            "o2,1,credit_card,1,31.0",
            "o3,1,boleto,1,41.0",
        ],
    )

    index = build_index(config, "customer")

    assert index.target_entity == "customer"
    assert sorted(index.records) == ["c1", "c2"]
    first = index.records["c1"]
    assert first.record_id == "c1"
    assert first.unique_id == "u1"
    assert first.city == "sao paulo"
    assert first.zip_prefix == "01310"
    assert first.products == frozenset({"p1", "p2", "p3"})
    assert first.payments == frozenset({31.0})
    assert first.order_count == 2
    assert index.records["c2"].products == frozenset({"p4"})


def test_build_index_raises_schema_error_naming_the_missing_column(config):
    _write_base(
        config,
        customers=["c1,u1,01310,São Paulo,SP"],
        orders=[],
        items=[],
        payments=[],
    )
    header = CUSTOMERS_HEADER.replace("customer_city", "city_name")
    _write(config, "olist_customers_dataset.csv", header, ["c1,u1,01310,São Paulo,SP"])

    with pytest.raises(SchemaError) as caught:
        build_index(config, "customer")

    message = str(caught.value)
    assert "customers" in message
    assert "customer_city" in message


def test_build_index_raises_when_a_source_file_is_absent(config):
    with pytest.raises(SchemaError) as caught:
        build_index(config, "customer")

    assert "customers" in str(caught.value)


def test_customer_without_orders_is_kept_with_empty_evidence(config):
    _write_base(
        config,
        customers=["c1,u1,01310,São Paulo,SP", "c2,u2,01310,São Paulo,SP"],
        orders=["o1,c1,delivered,2017-01-01 10:00:00,,,,"],
        items=[],
        payments=[],
    )

    index = build_index(config, "customer")

    assert sorted(index.records) == ["c1", "c2"]
    assert index.records["c2"].products == frozenset()
    assert index.records["c2"].order_count == 0
    assert index.records["c2"].zip_prefix == "01310"


def test_zip_prefix_keeps_leading_zeros_and_counts_missing(config):
    _write_base(
        config,
        customers=[
            "c1,u1,01310,São Paulo,SP",
            "c2,u2,1310,São Paulo,SP",
            "c3,u3,,São Paulo,SP",
        ],
        orders=[],
        items=[],
        payments=[],
    )

    index = build_index(config, "customer")

    assert index.records["c1"].zip_prefix == "01310"
    assert index.records["c2"].zip_prefix == "01310"
    assert index.records["c3"].zip_prefix == ""
    assert index.records_missing_match_fields == 1


def test_payments_are_summed_per_order(config):
    _write_base(
        config,
        customers=["c1,u1,01310,São Paulo,SP"],
        orders=["o1,c1,delivered,2017-01-01 10:00:00,,,,"],
        items=["o1,1,p1,s1,2017-01-05,10.0,1.0"],
        payments=[
            "o1,1,credit_card,1,100.00",
            "o1,2,voucher,1,50.50",
        ],
    )

    index = build_index(config, "customer")

    assert index.records["c1"].payments == frozenset({150.5})


def test_duplicate_groups_counts_unique_ids_seen_more_than_once(config):
    _write_base(
        config,
        customers=[
            "c1,u1,01310,São Paulo,SP",
            "c2,u1,01310,São Paulo,SP",
            "c3,u2,01311,São Paulo,SP",
            "c4,u3,01312,São Paulo,SP",
            "c5,u3,01312,São Paulo,SP",
        ],
        orders=[],
        items=[],
        payments=[],
    )

    index = build_index(config, "customer")

    assert index.duplicate_groups == 2


def test_seller_index_has_no_marker_key(config):
    _write(
        config,
        "olist_sellers_dataset.csv",
        SELLERS_HEADER,
        [
            "s1,01310,São Paulo,SP",
            "s2,20000,Rio de Janeiro,RJ",
        ],
    )
    _write(
        config,
        "olist_order_items_dataset.csv",
        ITEMS_HEADER,
        [
            "o1,1,p1,s1,2017-01-05,10.0,1.0",
            "o1,2,p2,s1,2017-01-05,20.0,1.0",
            "o2,1,p3,s2,2017-02-05,30.0,1.0",
        ],
    )
    _write(
        config,
        "olist_order_payments_dataset.csv",
        PAYMENTS_HEADER,
        [
            "o1,1,credit_card,1,31.0",
            "o2,1,boleto,1,31.0",
        ],
    )

    index = build_index(config, "seller")

    assert index.duplicate_groups == 0
    assert index.records["s1"].unique_id is None
    assert index.records["s1"].products == frozenset({"p1", "p2"})
    assert index.records["s1"].payments == frozenset({31.0})
    assert index.records["s2"].products == frozenset({"p3"})


def test_evidence_for_is_pure_over_frames():
    records = pd.DataFrame(
        {
            "customer_id": ["c1", "c2"],
            "customer_unique_id": ["u1", None],
            "customer_zip_code_prefix": ["01310", "01310"],
            "customer_city": ["São Paulo", None],
        }
    )
    orders = pd.DataFrame({"order_id": ["o1"], "customer_id": ["c1"]})
    items = pd.DataFrame({"order_id": ["o1"], "product_id": ["p1"]})
    payments = pd.DataFrame({"order_id": ["o1"], "payment_value": ["10.00"]})

    records_by_id, duplicates = evidence_for(records, orders, items, payments, "customer")

    assert sorted(records_by_id) == ["c1", "c2"]
    assert records_by_id["c1"].products == frozenset({"p1"})
    assert records_by_id["c1"].payments == frozenset({10.0})
    assert records_by_id["c2"].city == ""
    assert records_by_id["c2"].products == frozenset()
    assert duplicates == 0
