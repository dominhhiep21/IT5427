"""Unit tests for the mediated entity model and the schema loader."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from src.common.exceptions import ConfigurationError, SchemaError
from src.integration.models import STATUS_VALUES, DonHang, InvalidRecord
from src.integration.schema import checked_identifier, load_schema, loaded_columns

ROOT = Path(__file__).resolve().parents[2]

SCHEMA_YAML = """
schema_kind: GAV
entities:
  - name: don_hang
    description: Một dòng cho mỗi đơn hàng
    source_tables:
      - olist_orders_dataset
      - olist_customers_dataset
    fields:
      - field_name: ma_don
        source_table: olist_orders_dataset
        source_column: order_id
        data_type: string
        loaded: true
      - field_name: ngay_dat
        source_table: olist_orders_dataset
        source_column: order_purchase_timestamp
        data_type: timestamp
        loaded: true
      - field_name: trang_thai
        source_table: olist_orders_dataset
        source_column: order_status
        data_type: string
        loaded: true
      - field_name: ma_khach
        source_table: olist_orders_dataset
        source_column: customer_id
        data_type: string
        loaded: true
      - field_name: bang_giao
        source_table: olist_customers_dataset
        source_column: customer_state
        data_type: string
        loaded: false
"""


def _write_schema(tmp_path: Path, text: str = SCHEMA_YAML) -> Path:
    path = tmp_path / "mediated-schema.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "ma_don": "o1",
        "ngay_dat": "2017-01-01 10:00:00",
        "trang_thai": "delivered",
        "ma_khach": "c1",
        "bang_giao": "",
    }
    row.update(overrides)
    return row


def test_from_row_builds_don_hang():
    order = DonHang.from_row(_row())

    assert order.ma_don == "o1"
    assert order.trang_thai == "delivered"
    assert order.ma_khach == "c1"


def test_from_row_parses_purchase_date():
    order = DonHang.from_row(_row(ngay_dat="2018-10-17 09:30:00"))

    assert order.ngay_dat == datetime(2018, 10, 17, 9, 30)


def test_from_row_leaves_missing_bang_giao_empty():
    order = DonHang.from_row(_row(bang_giao=""))

    assert order.bang_giao is None


def test_from_row_rejects_missing_date():
    with pytest.raises(InvalidRecord) as caught:
        DonHang.from_row(_row(ngay_dat=""))

    assert caught.value.reason == "ngay_dat_rong"


def test_from_row_rejects_unparseable_date():
    with pytest.raises(InvalidRecord) as caught:
        DonHang.from_row(_row(ngay_dat="31/31/2017"))

    assert caught.value.reason == "ngay_dat_rong"


def test_from_row_rejects_unknown_status():
    with pytest.raises(InvalidRecord) as caught:
        DonHang.from_row(_row(trang_thai="returned"))

    assert caught.value.reason == "trang_thai_ngoai_mien"


def test_from_row_rejects_empty_order_id():
    with pytest.raises(InvalidRecord) as caught:
        DonHang.from_row(_row(ma_don=""))

    assert caught.value.reason == "ma_don_rong"


def test_status_values_are_the_eight_olist_values():
    assert STATUS_VALUES == frozenset(
        {
            "created",
            "approved",
            "invoiced",
            "processing",
            "shipped",
            "delivered",
            "unavailable",
            "canceled",
        }
    )


def test_load_schema_reads_entity_and_loaded_flags(tmp_path: Path):
    schema = load_schema(_write_schema(tmp_path))
    entity = schema.entity("don_hang")

    assert schema.schema_kind == "GAV"
    assert len(entity.fields) == 5
    assert entity.loaded_fields == (
        "ma_don",
        "ngay_dat",
        "trang_thai",
        "ma_khach",
    )
    assert entity.field("bang_giao").loaded is False


def test_loaded_columns_are_the_four_order_columns(tmp_path: Path):
    entity = load_schema(_write_schema(tmp_path)).entity("don_hang")

    assert loaded_columns(entity) == (
        "order_id",
        "order_purchase_timestamp",
        "order_status",
        "customer_id",
    )


def test_shipped_schema_file_matches_the_contract():
    schema = load_schema(ROOT / "config" / "mediated-schema.yaml")
    entity = schema.entity("don_hang")

    assert entity.source_tables == (
        "olist_orders_dataset",
        "olist_customers_dataset",
    )
    assert len(entity.fields) == 7
    assert entity.field("bang_giao").source_column == "customer_state"
    assert entity.field("bang_giao").loaded is True
    assert entity.field("ngay_giao_thuc_te").source_column == "order_delivered_customer_date"
    assert entity.field("ngay_giao_du_kien").source_column == "order_estimated_delivery_date"


def test_load_schema_rejects_source_table_outside_allow_list(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "      - field_name: ma_don\n        source_table: olist_orders_dataset",
        "      - field_name: ma_don\n        source_table: orders_unknown",
    )

    with pytest.raises(SchemaError):
        load_schema(_write_schema(tmp_path, text))


def test_load_schema_rejects_a_missing_file(tmp_path: Path):
    with pytest.raises(ConfigurationError):
        load_schema(tmp_path / "khong-co.yaml")


def test_load_schema_rejects_invalid_yaml(tmp_path: Path):
    path = tmp_path / "mediated-schema.yaml"
    path.write_text("schema_kind: [thieu ngoac\n", encoding="utf-8")

    with pytest.raises(SchemaError):
        load_schema(path)


def test_load_schema_rejects_a_non_mapping(tmp_path: Path):
    path = tmp_path / "mediated-schema.yaml"
    path.write_text("- chi-la-danh-sach\n", encoding="utf-8")

    with pytest.raises(SchemaError):
        load_schema(path)


def test_load_schema_rejects_a_wrong_schema_kind(tmp_path: Path):
    text = SCHEMA_YAML.replace("schema_kind: GAV", "schema_kind: GLAV")

    with pytest.raises(SchemaError):
        load_schema(_write_schema(tmp_path, text))


def test_load_schema_rejects_an_unknown_data_type(tmp_path: Path):
    text = SCHEMA_YAML.replace("data_type: timestamp", "data_type: date")

    with pytest.raises(SchemaError):
        load_schema(_write_schema(tmp_path, text))


def test_load_schema_rejects_a_non_boolean_loaded_flag(tmp_path: Path):
    text = SCHEMA_YAML.replace("loaded: false", 'loaded: "khong"')

    with pytest.raises(SchemaError):
        load_schema(_write_schema(tmp_path, text))


def test_load_schema_rejects_a_field_table_outside_the_entity(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "  - name: don_hang\n    description: Một dòng cho mỗi đơn hàng\n    source_tables:\n      - olist_orders_dataset\n      - olist_customers_dataset",
        "  - name: don_hang\n    description: Một dòng cho mỗi đơn hàng\n    source_tables:\n      - olist_customers_dataset",
    )

    with pytest.raises(SchemaError):
        load_schema(_write_schema(tmp_path, text))


def test_load_schema_rejects_an_entity_without_fields(tmp_path: Path):
    text = SCHEMA_YAML.split("    fields:")[0]

    with pytest.raises(SchemaError):
        load_schema(_write_schema(tmp_path, text))


def test_checked_identifier_rejects_an_empty_name():
    with pytest.raises(SchemaError):
        checked_identifier("", frozenset({"order_id"}), "cột nguồn")


def test_checked_identifier_rejects_camel_case():
    with pytest.raises(SchemaError):
        checked_identifier("orderId", frozenset({"orderId"}), "cột nguồn")


def test_checked_identifier_rejects_column_with_semicolon():
    with pytest.raises(SchemaError):
        checked_identifier(
            "order_id; DROP TABLE x --",
            frozenset({"order_id"}),
            "cột nguồn",
        )


def test_checked_identifier_rejects_name_outside_allow_list():
    with pytest.raises(SchemaError):
        checked_identifier("order_total", frozenset({"order_id"}), "cột nguồn")


def test_from_row_rejects_a_future_purchase_date():
    """entities.md constraint: ngay_dat must not be in the future."""

    row = {
        "ma_don": "o-1",
        "ngay_dat": "2099-01-01 10:00:00",
        "trang_thai": "delivered",
        "ma_khach": "c-1",
        "bang_giao": None,
    }

    with pytest.raises(InvalidRecord) as excinfo:
        DonHang.from_row(row)

    assert excinfo.value.reason == "ngay_dat_tuong_lai"
