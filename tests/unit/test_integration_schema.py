"""Unit test cho bộ nạp lược đồ trung gian, các kiểu hợp đồng và các phép kiểm của nó."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.common.exceptions import ConfigurationError, SchemaError
from src.integration import schema as schema_module
from src.integration.models import (
    MediatedFieldCatalogue,
    MediatedSchemaView,
    PartialInfo,
)
from src.integration.schema import build_field_catalogue, load_schema

ORDERS_HEADER = (
    "order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,"
    "order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date"
)
CUSTOMERS_HEADER = "customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state"
ITEMS_HEADER = "order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value"
PRODUCTS_HEADER = (
    "product_id,product_category_name,product_name_lenght,product_description_lenght,"
    "product_photos_qty,product_weight_g,product_length_cm,product_height_cm,product_width_cm"
)
# Dòng dữ liệu cố ý sai kiểu: nạp được nghĩa là bộ nạp chưa từng đọc tới nó.
BAD_ROW = '"khong-phai-so","31/31/2017","delivered","khong-phai-ngay",,,,'

SOURCES = {
    "olist_orders_dataset.csv": ORDERS_HEADER,
    "olist_customers_dataset.csv": CUSTOMERS_HEADER,
    "olist_order_items_dataset.csv": ITEMS_HEADER,
    "olist_products_dataset.csv": PRODUCTS_HEADER,
}

REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASED_SCHEMA = REPO_ROOT / "config" / "mediated-schema.yaml"
RELEASED_CSV_DIR = REPO_ROOT / "dataset"

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
  - name: mat_hang
    description: Một dòng cho mỗi dòng hàng của đơn
    source_tables:
      - olist_order_items_dataset
    fields:
      - field_name: ma_don
        source_table: olist_order_items_dataset
        source_column: order_id
        data_type: string
        loaded: true
      - field_name: ma_san_pham
        source_table: olist_order_items_dataset
        source_column: product_id
        data_type: string
        loaded: true
      - field_name: so_thu_tu
        source_table: olist_order_items_dataset
        source_column: order_item_id
        data_type: integer
        loaded: true
      - field_name: gia
        source_table: olist_order_items_dataset
        source_column: price
        data_type: decimal
        loaded: true
  - name: san_pham
    description: Một dòng cho mỗi sản phẩm
    source_tables:
      - olist_products_dataset
    fields:
      - field_name: ma_san_pham
        source_table: olist_products_dataset
        source_column: product_id
        data_type: string
        loaded: true
      - field_name: ten_danh_muc
        source_table: olist_products_dataset
        source_column: product_category_name
        data_type: string
        loaded: false
"""


def _write_schema(root: Path, text: str = SCHEMA_YAML) -> Path:
    path = root / "mediated-schema.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _write_dataset(root: Path) -> Path:
    dataset = root / "dataset"
    dataset.mkdir(exist_ok=True)
    for name, header in SOURCES.items():
        (dataset / name).write_text(f"{header}\n{BAD_ROW}\n", encoding="utf-8")
    return dataset


def _load(root: Path, text: str = SCHEMA_YAML, logger: object | None = None) -> MediatedSchemaView:
    return load_schema(_write_schema(root, text), csv_dir=_write_dataset(root), logger=logger)


class RecordingLogger:
    """Logger ghi lại sự kiện thay cho `NullLogger` khi test cần khẳng định."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, object]]] = []

    def info(self, event: str, **fields: object) -> None:
        self.events.append(("info", event, fields))

    def warning(self, event: str, **fields: object) -> None:
        self.events.append(("warning", event, fields))

    def error(self, event: str, error_code: str, **fields: object) -> None:
        self.events.append(("error", event, {"error_code": error_code, **fields}))


class LineCountingHandle:
    """Bọc một tệp văn bản để đếm số dòng bộ nạp thực sự đọc."""

    def __init__(self, handle) -> None:
        self._handle = handle
        self.lines = 0

    def __iter__(self):
        for line in self._handle:
            self.lines += 1
            yield line

    def __enter__(self):
        self._handle.__enter__()
        return self

    def __exit__(self, *exc_info: object):
        return self._handle.__exit__(*exc_info)


def test_partial_info_keeps_missing_and_reason():
    info = PartialInfo(missing=("mat_hang", "san_pham"), reason="Thực thể chưa được khai.")

    assert info.missing == ("mat_hang", "san_pham")
    assert info.reason == "Thực thể chưa được khai."


def test_partial_info_is_frozen():
    info = PartialInfo(missing=("san_pham",), reason="Thực thể chưa được khai.")

    with pytest.raises(FrozenInstanceError):
        info.missing = ()  # type: ignore[misc]


def test_mediated_schema_view_defaults_partial_to_none():
    view = MediatedSchemaView(schema_kind="GAV", entities=(), mappings={}, elapsed_ms=1)

    assert view.partial is None
    assert view.elapsed_ms == 1


def test_mediated_schema_view_keeps_elapsed_ms_and_partial():
    info = PartialInfo(missing=("mat_hang",), reason="Thực thể chưa được khai.")
    view = MediatedSchemaView(
        schema_kind="GAV",
        entities=(),
        mappings={},
        elapsed_ms=7,
        partial=info,
    )

    assert view.partial == info
    assert view.elapsed_ms == 7


def test_mediated_schema_view_is_frozen():
    view = MediatedSchemaView(schema_kind="GAV", entities=(), mappings={}, elapsed_ms=1)

    with pytest.raises(FrozenInstanceError):
        view.elapsed_ms = 2  # type: ignore[misc]


def test_mediated_field_catalogue_keeps_field_order():
    catalogue = MediatedFieldCatalogue(fields_by_entity={"don_hang": ("don_hang.ma_don",)})

    assert catalogue.fields_by_entity["don_hang"] == ("don_hang.ma_don",)


def test_mediated_field_catalogue_is_frozen():
    catalogue = MediatedFieldCatalogue(fields_by_entity={})

    with pytest.raises(FrozenInstanceError):
        catalogue.fields_by_entity = {}  # type: ignore[misc]


def test_load_schema_accepts_columns_present_in_the_header(tmp_path: Path):
    view = _load(tmp_path)

    assert view.schema_kind == "GAV"


def test_load_schema_never_reads_the_data_row(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Mỗi tệp mẫu có một dòng dữ liệu sai kiểu; chỉ đúng một dòng tiêu đề được đọc (ADR-U2-S3)."""

    dataset = _write_dataset(tmp_path)
    opened: list[LineCountingHandle] = []
    real_open = Path.open

    def counting_open(self: Path, *args: object, **kwargs: object):
        handle = real_open(self, *args, **kwargs)
        if self.suffix != ".csv":
            return handle
        recorder = LineCountingHandle(handle)
        opened.append(recorder)
        return recorder

    monkeypatch.setattr(Path, "open", counting_open)

    view = load_schema(_write_schema(tmp_path), csv_dir=dataset)

    assert view.schema_kind == "GAV"
    assert len(opened) == len(SOURCES)
    assert [handle.lines for handle in opened] == [1] * len(SOURCES)


def test_load_schema_rejects_a_column_missing_from_the_header(tmp_path: Path):
    text = SCHEMA_YAML.replace("source_column: customer_state", "source_column: customer_region")

    with pytest.raises(SchemaError) as caught:
        _load(tmp_path, text)

    message = str(caught.value)
    assert "bang_giao" in message
    assert "customer_region" in message


def test_load_schema_rejects_a_missing_source_csv(tmp_path: Path):
    dataset = _write_dataset(tmp_path)
    (dataset / "olist_products_dataset.csv").unlink()

    with pytest.raises(ConfigurationError):
        load_schema(_write_schema(tmp_path), csv_dir=dataset)


def test_load_schema_rejects_an_undecodable_source_csv(tmp_path: Path):
    dataset = _write_dataset(tmp_path)
    (dataset / "olist_products_dataset.csv").write_bytes(b"product_id,\xff\xfe\n")

    with pytest.raises(SchemaError):
        load_schema(_write_schema(tmp_path), csv_dir=dataset)


def test_load_schema_returns_a_view_with_three_entities(tmp_path: Path):
    view = _load(tmp_path)

    assert isinstance(view, MediatedSchemaView)
    assert tuple(item.name for item in view.entities) == ("don_hang", "mat_hang", "san_pham")
    assert tuple(view.mappings) == ("don_hang", "mat_hang", "san_pham")
    assert view.schema_kind == "GAV"


def test_load_schema_has_no_partial_when_all_three_are_declared(tmp_path: Path):
    view = _load(tmp_path)

    assert view.partial is None


def test_load_schema_reports_missing_entities_as_partial(tmp_path: Path):
    text = SCHEMA_YAML.split("  - name: mat_hang")[0]

    view = _load(tmp_path, text)

    assert view.partial is not None
    assert view.partial.missing == ("mat_hang", "san_pham")
    assert view.partial.reason
    assert tuple(item.name for item in view.entities) == ("don_hang",)


def test_load_schema_keeps_field_order_from_the_file(tmp_path: Path):
    view = _load(tmp_path)

    assert tuple(item.field_name for item in view.mappings["don_hang"]) == (
        "ma_don",
        "ngay_dat",
        "trang_thai",
        "ma_khach",
        "bang_giao",
    )


def test_load_schema_rejects_a_source_table_outside_the_table_specs(tmp_path: Path):
    text = SCHEMA_YAML.replace("source_table: olist_products_dataset", "source_table: olist_catalog_dataset")

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


def test_load_schema_rejects_a_field_using_a_table_outside_its_entity(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "      - field_name: ma_san_pham\n        source_table: olist_order_items_dataset",
        "      - field_name: ma_san_pham\n        source_table: olist_products_dataset",
    )

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


@pytest.mark.parametrize("bad_name", ['"Orders";DROP', "don hang", "A_B", "a" * 65])
def test_load_schema_rejects_malformed_identifiers(tmp_path: Path, bad_name: str):
    text = SCHEMA_YAML.replace("field_name: ma_don", f"field_name: '{bad_name}'", 1)

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


def test_load_schema_checks_identifiers_before_opening_source_files(tmp_path: Path):
    """ADR-U2-S1: định danh hỏng phải hỏng trước khi bộ nạp mở bất kỳ tệp CSV nào."""

    text = SCHEMA_YAML.replace("field_name: ma_don", "field_name: 'don hang'", 1)

    with pytest.raises(SchemaError) as caught:
        load_schema(_write_schema(tmp_path, text), csv_dir=tmp_path / "khong-ton-tai")

    assert not isinstance(caught.value, ConfigurationError)
    assert "don hang" in str(caught.value)


def test_load_schema_rejects_a_non_gav_schema_kind(tmp_path: Path):
    text = SCHEMA_YAML.replace("schema_kind: GAV", "schema_kind: GLAV")

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


def test_load_schema_rejects_an_unknown_data_type(tmp_path: Path):
    text = SCHEMA_YAML.replace("data_type: decimal", "data_type: money")

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


def test_load_schema_rejects_a_duplicate_field_name(tmp_path: Path):
    text = SCHEMA_YAML.replace("field_name: ma_khach", "field_name: ma_don")

    with pytest.raises(SchemaError) as caught:
        _load(tmp_path, text)

    assert "ma_don" in str(caught.value)


def test_load_schema_rejects_a_duplicate_entity_name(tmp_path: Path):
    text = SCHEMA_YAML.replace("  - name: mat_hang", "  - name: don_hang")

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


def test_load_schema_defaults_loaded_to_true(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "        data_type: decimal\n        loaded: true\n", "        data_type: decimal\n"
    )

    view = _load(tmp_path, text)

    assert view.entity("mat_hang").field("gia").loaded is True


def test_load_schema_rejects_a_non_boolean_loaded_flag(tmp_path: Path):
    text = SCHEMA_YAML.replace("loaded: false", 'loaded: "khong"')

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


def test_load_schema_measures_elapsed_ms(tmp_path: Path):
    view = _load(tmp_path)

    assert isinstance(view.elapsed_ms, int)
    assert 0 < view.elapsed_ms <= 2000


def test_field_catalogue_lists_entity_dot_field_in_order(tmp_path: Path):
    catalogue = build_field_catalogue(_load(tmp_path))

    assert isinstance(catalogue, MediatedFieldCatalogue)
    assert catalogue.fields_by_entity["mat_hang"] == (
        "mat_hang.ma_don",
        "mat_hang.ma_san_pham",
        "mat_hang.so_thu_tu",
        "mat_hang.gia",
    )


def test_field_catalogue_skips_entities_that_are_missing(tmp_path: Path):
    text = SCHEMA_YAML.split("  - name: mat_hang")[0]

    catalogue = build_field_catalogue(_load(tmp_path, text))

    assert tuple(catalogue.fields_by_entity) == ("don_hang",)


def test_load_schema_logs_the_loaded_event(tmp_path: Path):
    logger = RecordingLogger()

    _load(tmp_path, logger=logger)

    levels = [level for level, _, _ in logger.events]
    events = [event for _, event, _ in logger.events]
    assert levels == ["info"]
    assert events == ["integration.schema.loaded"]
    fields = logger.events[0][2]
    assert fields["entity_count"] == 3
    assert fields["partial_entities"] == []


def test_load_schema_logs_the_partial_event(tmp_path: Path):
    logger = RecordingLogger()
    text = SCHEMA_YAML.split("  - name: mat_hang")[0]

    _load(tmp_path, text, logger=logger)

    assert [level for level, _, _ in logger.events] == ["warning", "info"]
    assert logger.events[0][1] == "integration.schema.partial"
    assert logger.events[0][2]["missing_entities"] == ["mat_hang", "san_pham"]


def test_load_schema_logs_a_failure_with_an_error_code(tmp_path: Path):
    logger = RecordingLogger()
    text = SCHEMA_YAML.replace("source_column: customer_state", "source_column: customer_region")

    with pytest.raises(SchemaError):
        _load(tmp_path, text, logger=logger)

    assert len(logger.events) == 1
    level, event, fields = logger.events[0]
    assert (level, event) == ("error", "integration.schema.failed")
    assert fields["error_code"] == "column_missing"
    assert "customer_region" in str(fields["message"])


def test_load_schema_uses_a_null_logger_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    logger = RecordingLogger()
    monkeypatch.setattr(schema_module, "NullLogger", lambda: logger)

    _load(tmp_path)

    assert [event for _, event, _ in logger.events] == ["integration.schema.loaded"]


def test_load_schema_without_a_logger_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture
):
    """SR-U2-7: mặc định thật là `NullLogger`, nên không có dòng log nào và không có tệp log."""

    view = _load(tmp_path)

    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "")
    assert caplog.records == []
    assert sorted(item.name for item in tmp_path.iterdir()) == ["dataset", "mediated-schema.yaml"]
    assert view.partial is None


def test_load_schema_resolves_the_csv_dir_from_the_app_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    dataset = _write_dataset(tmp_path)
    monkeypatch.setattr(schema_module, "load_config", lambda: SimpleNamespace(raw_csv_dir=dataset))
    monkeypatch.setattr(schema_module, "_CSV_DIR", None)

    view = load_schema(_write_schema(tmp_path))

    assert view.schema_kind == "GAV"


def test_load_schema_rejects_an_entity_without_source_tables(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "    source_tables:\n      - olist_products_dataset\n", "    source_tables: []\n"
    )

    with pytest.raises(SchemaError):
        _load(tmp_path, text)


def test_load_schema_rejects_an_unknown_entity_key(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "    description: Một dòng cho mỗi sản phẩm",
        "    descriptions: Một dòng cho mỗi sản phẩm",
        1,
    )

    with pytest.raises(SchemaError) as caught:
        _load(tmp_path, text)

    assert "descriptions" in str(caught.value)


def test_load_schema_rejects_an_unknown_field_key(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "      - field_name: ma_don\n"
        "        source_table: olist_orders_dataset\n"
        "        source_column: order_id\n"
        "        data_type: string\n"
        "        loaded: true",
        "      - field_name: ma_don\n"
        "        source_table: olist_orders_dataset\n"
        "        source_column: order_id\n"
        "        data_type: string\n"
        "        loadded: true",
        1,
    )

    with pytest.raises(SchemaError) as caught:
        _load(tmp_path, text)

    assert "loadded" in str(caught.value)


def test_load_schema_rejects_duplicate_source_tables(tmp_path: Path):
    text = SCHEMA_YAML.replace(
        "      - olist_order_items_dataset\n    fields:",
        "      - olist_order_items_dataset\n      - olist_order_items_dataset\n    fields:",
        1,
    )

    with pytest.raises(SchemaError) as caught:
        _load(tmp_path, text)

    assert "olist_order_items_dataset" in str(caught.value)


def test_load_schema_logs_decode_error_for_an_unreadable_schema_file(tmp_path: Path):
    path = tmp_path / "mediated-schema.yaml"
    path.write_text("schema_kind: [thieu ngoac\n", encoding="utf-8")
    logger = RecordingLogger()

    with pytest.raises(SchemaError):
        load_schema(path, csv_dir=_write_dataset(tmp_path), logger=logger)

    assert logger.events[0][1] == "integration.schema.failed"
    assert logger.events[0][2]["error_code"] == "decode_error"


@pytest.mark.slow
def test_released_schema_declares_the_three_entities():
    """BR2.1/BR2.9: tệp cấu hình đang phát hành khai đủ ba thực thể và không có kênh partial."""

    view = load_schema(RELEASED_SCHEMA, csv_dir=RELEASED_CSV_DIR)

    assert view.schema_kind == "GAV"
    assert tuple(item.name for item in view.entities) == ("don_hang", "mat_hang", "san_pham")
    assert tuple(view.mappings) == ("don_hang", "mat_hang", "san_pham")
    assert view.partial is None
