"""Unit tests for loading the mediated `don_hang` entity from source CSVs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src.common.exceptions import SchemaError
from src.common.logging import ERROR_CODES, JsonLogger, new_run_context
from src.config import load_config
from src.integration import load as load_module

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

ORDERS_HEADER = (
    "order_id,customer_id,order_status,order_purchase_timestamp,"
    "order_approved_at,order_delivered_carrier_date,"
    "order_delivered_customer_date,order_estimated_delivery_date"
)

ORDERS_ROWS = (
    "o1,c1,delivered,2017-01-01 10:00:00,,,,",
    "o2,c2,shipped,2017-02-01 10:00:00,,,,",
    "o3,c3,canceled,2017-03-01 10:00:00,,,,",
    "o1,c4,delivered,2017-04-01 10:00:00,,,,",
    "o4,c1,delivered,,,,,",
    "o5,c2,returned,2017-06-01 10:00:00,,,,",
    "o6,c3,delivered,2017-07-01 10:00:00,,,,",
)

CUSTOMERS_HEADER = "customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state"


def _write_schema(tmp_path: Path, text: str = SCHEMA_YAML) -> Path:
    path = tmp_path / "mediated-schema.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _write_dataset(tmp_path: Path, orders_header: str = ORDERS_HEADER) -> Path:
    dataset = tmp_path / "dataset"
    dataset.mkdir(exist_ok=True)
    (dataset / "olist_orders_dataset.csv").write_text(
        orders_header + "\n" + "\n".join(ORDERS_ROWS) + "\n",
        encoding="utf-8",
    )
    (dataset / "olist_customers_dataset.csv").write_text(CUSTOMERS_HEADER + "\n", encoding="utf-8")
    return dataset


def _make_config(tmp_path: Path, schema_text: str = SCHEMA_YAML):
    dataset = _write_dataset(tmp_path)
    schema = _write_schema(tmp_path, schema_text)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
paths:
  raw_csv_dir: "{dataset.as_posix()}"
  data_dir: data
  logs_dir: logs
  temp_dir: data/.tmp
  mediated_schema_path: "{schema.as_posix()}"
""",
        encoding="utf-8",
    )
    load_module.clear_cache()
    return load_config(config_path)


def _logger(config) -> JsonLogger:
    run = new_run_context("integration", config.logs_dir, config.temp_dir)
    return JsonLogger(run, console=False)


def _events(config, logger) -> list[dict]:
    if not logger.run.log_path.exists():
        return []
    lines = logger.run.log_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def test_load_reads_only_the_loaded_columns(tmp_path: Path, monkeypatch):
    config = _make_config(tmp_path)
    calls: list[tuple[str, dict]] = []
    real = load_module._read_csv

    def fake(path, **kwargs):
        calls.append((Path(path).name, kwargs))
        return real(path, **kwargs)

    monkeypatch.setattr(load_module, "_read_csv", fake)
    result = load_module.load_don_hang(config, _logger(config))

    data_calls = [call for call in calls if call[1].get("usecols")]
    assert len(data_calls) == 1
    assert list(data_calls[0][1]["usecols"]) == [
        "order_id",
        "order_purchase_timestamp",
        "order_status",
        "customer_id",
    ]
    assert all(order.bang_giao is None for order in result.orders)


def test_load_checks_bang_giao_by_header_only(tmp_path: Path, monkeypatch):
    config = _make_config(tmp_path)
    calls: list[tuple[str, dict]] = []
    real = load_module._read_csv

    def fake(path, **kwargs):
        calls.append((Path(path).name, kwargs))
        return real(path, **kwargs)

    monkeypatch.setattr(load_module, "_read_csv", fake)
    load_module.load_don_hang(config, _logger(config))

    customer_calls = [call for call in calls if call[0] == "olist_customers_dataset.csv"]
    assert customer_calls
    assert all(call[1].get("nrows") == 0 for call in customer_calls)


def test_load_raises_when_source_column_is_missing(tmp_path: Path):
    config = _make_config(tmp_path)
    header = ORDERS_HEADER.replace("customer_id", "buyer_id")
    _write_dataset(tmp_path, header)
    load_module.clear_cache()
    config = load_config(config.config_path)

    with pytest.raises(SchemaError) as caught:
        load_module.load_don_hang(config, _logger(config))

    message = str(caught.value)
    assert "ma_khach" in message
    assert "customer_id" in message


def test_load_rejects_invalid_identifier_before_reading(tmp_path: Path, monkeypatch):
    schema_text = SCHEMA_YAML.replace(
        "source_table: olist_orders_dataset\n        source_column: order_id",
        "source_table: orders_unknown\n        source_column: order_id",
    )
    config = _make_config(tmp_path, schema_text)

    def explode(*args, **kwargs):
        raise AssertionError("không được đọc tệp khi lược đồ sai")

    monkeypatch.setattr(load_module, "_read_csv", explode)
    with pytest.raises(SchemaError):
        load_module.load_don_hang(config, _logger(config))


def test_load_retries_once_then_succeeds(tmp_path: Path, monkeypatch):
    config = _make_config(tmp_path)
    logger = _logger(config)
    real = load_module._read_csv
    failures = {"count": 0}

    def flaky(path, **kwargs):
        if kwargs.get("usecols") and failures["count"] == 0:
            failures["count"] += 1
            raise PermissionError("tệp đang bị khoá")
        return real(path, **kwargs)

    monkeypatch.setattr(load_module, "_read_csv", flaky)
    monkeypatch.setattr("time.sleep", lambda _: None)
    result = load_module.load_don_hang(config, logger)

    assert result.rows_in == len(ORDERS_ROWS)
    events = [event["event"] for event in _events(config, logger)]
    assert "integration.load.retried" in events


def test_load_fails_after_exactly_two_attempts(tmp_path: Path, monkeypatch):
    config = _make_config(tmp_path)
    logger = _logger(config)
    attempts = {"data": 0}
    real = load_module._read_csv

    def broken(path, **kwargs):
        if kwargs.get("usecols"):
            attempts["data"] += 1
            raise PermissionError("tệp đang bị khoá")
        return real(path, **kwargs)

    monkeypatch.setattr(load_module, "_read_csv", broken)
    monkeypatch.setattr("time.sleep", lambda _: None)
    with pytest.raises(SchemaError) as caught:
        load_module.load_don_hang(config, logger)

    assert attempts["data"] == 2
    assert "olist_orders_dataset.csv" in str(caught.value)


def test_load_drops_duplicate_order_ids(tmp_path: Path):
    config = _make_config(tmp_path)
    result = load_module.load_don_hang(config, _logger(config))

    assert len([order for order in result.orders if order.ma_don == "o1"]) == 1
    assert result.drop_reasons["trung_ma_don"] == 1


def test_load_drops_empty_date_and_unknown_status(tmp_path: Path):
    config = _make_config(tmp_path)
    result = load_module.load_don_hang(config, _logger(config))

    assert result.drop_reasons["ngay_dat_rong"] == 1
    assert result.drop_reasons["trang_thai_ngoai_mien"] == 1
    assert {order.ma_don for order in result.orders} == {"o1", "o2", "o3", "o6"}


def test_load_counts_rows_in_and_dropped(tmp_path: Path):
    config = _make_config(tmp_path)
    result = load_module.load_don_hang(config, _logger(config))

    assert result.rows_in == len(ORDERS_ROWS)
    assert result.rows_dropped == 3
    assert len(result.orders) == 4
    assert result.elapsed_ms >= 0


def test_load_does_not_retry_schema_errors(tmp_path: Path):
    config = _make_config(tmp_path)
    logger = _logger(config)
    header = ORDERS_HEADER.replace("order_purchase_timestamp", "purchase_at")
    _write_dataset(tmp_path, header)
    load_module.clear_cache()
    config = load_config(config.config_path)

    with pytest.raises(SchemaError):
        load_module.load_don_hang(config, logger)

    events = [event["event"] for event in _events(config, logger)]
    assert "integration.load.retried" not in events


def test_load_writes_closed_error_codes(tmp_path: Path):
    config = _make_config(tmp_path)
    logger = _logger(config)
    (config.raw_csv_dir / "olist_orders_dataset.csv").unlink()
    load_module.clear_cache()

    with pytest.raises(SchemaError):
        load_module.load_don_hang(config, logger)

    codes = {event["error_code"] for event in _events(config, logger) if "error_code" in event}
    assert codes
    assert codes <= ERROR_CODES


def test_clean_rows_is_a_pure_function_over_a_frame():
    frame = pd.DataFrame(
        [
            {"ma_don": "o1", "ngay_dat": "2017-01-01 10:00:00", "trang_thai": "delivered"},
            {"ma_don": "o1", "ngay_dat": "2017-02-01 10:00:00", "trang_thai": "delivered"},
            {"ma_don": "o2", "ngay_dat": "", "trang_thai": "delivered"},
        ]
    )

    orders, dropped, reasons = load_module.clean_rows(frame)

    assert [order.ma_don for order in orders] == ["o1"]
    assert dropped == 2
    assert reasons == {"trung_ma_don": 1, "ngay_dat_rong": 1}


def test_load_with_a_second_loaded_table_reads_the_key_table_only(tmp_path: Path):
    """BR3.11: `bang_giao` được bật `loaded` cho tầng truy vấn; lát cắt này vẫn nạp bảng khoá."""

    schema_text = SCHEMA_YAML.replace(
        "source_column: customer_state\n        data_type: string\n        loaded: false",
        "source_column: customer_state\n        data_type: string\n        loaded: true",
    )
    config = _make_config(tmp_path, schema_text)
    logger = _logger(config)

    result = load_module.load_don_hang(config, logger)

    assert result.orders
    assert all(order.bang_giao is None for order in result.orders)
    skipped = [event for event in _events(config, logger) if event["event"] == "integration.load.skipped"]
    assert skipped and skipped[0]["tables"] == ["olist_customers_dataset"]


def test_load_decodes_utf8_and_reports_a_decode_error(tmp_path: Path, monkeypatch):
    config = _make_config(tmp_path)
    logger = _logger(config)

    def broken(path, **kwargs):
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")

    monkeypatch.setattr(load_module, "_read_csv", broken)
    monkeypatch.setattr("time.sleep", lambda _: None)
    with pytest.raises(SchemaError):
        load_module.load_don_hang(config, logger)

    codes = {event["error_code"] for event in _events(config, logger) if "error_code" in event}
    assert "decode_error" in codes


def test_load_uses_cache_for_the_same_source_files(tmp_path: Path, monkeypatch):
    config = _make_config(tmp_path)
    calls = {"count": 0}
    real = load_module._read_csv

    def counting(path, **kwargs):
        calls["count"] += 1
        return real(path, **kwargs)

    monkeypatch.setattr(load_module, "_read_csv", counting)
    first = load_module.load_don_hang(config, _logger(config))
    after_first = calls["count"]
    second = load_module.load_don_hang(config, _logger(config))

    assert calls["count"] == after_first
    assert second is first


def test_load_reloads_when_source_file_changes(tmp_path: Path, monkeypatch):
    config = _make_config(tmp_path)
    first = load_module.load_don_hang(config, _logger(config))
    orders_path = config.raw_csv_dir / "olist_orders_dataset.csv"
    orders_path.write_text(ORDERS_HEADER + "\n" + ORDERS_ROWS[0] + "\n", encoding="utf-8")
    import os

    os.utime(orders_path, (orders_path.stat().st_atime, orders_path.stat().st_mtime + 5))
    second = load_module.load_don_hang(config, _logger(config))

    assert second is not first
    assert second.rows_in == 1
