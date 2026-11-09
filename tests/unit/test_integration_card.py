"""Unit tests for the "Tích hợp" tab card, its five states and the C9 config."""

from __future__ import annotations

from dataclasses import fields, replace
from datetime import datetime
from pathlib import Path

import pytest
from dash import html

from src.common.exceptions import ConfigurationError, QueryExecutionError, SchemaError
from src.config import load_config
from src.integration import card as card_module
from src.integration.models import QueryRunResult, RewriteStep

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

ORDERS_HEADER = (
    "order_id,customer_id,order_status,order_purchase_timestamp,"
    "order_approved_at,order_delivered_carrier_date,"
    "order_delivered_customer_date,order_estimated_delivery_date"
)

CUSTOMERS_HEADER = "customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state"


def _walk(node):
    yield node
    children = getattr(node, "children", None)
    if children is None or isinstance(children, str):
        return
    if isinstance(children, (list, tuple)):
        for child in children:
            if child is None or isinstance(child, str):
                continue
            yield from _walk(child)
    elif not isinstance(children, (int, float)):
        yield from _walk(children)


def _text(node) -> str:
    parts: list[str] = []
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, str):
            parts.append(current)
            continue
        children = getattr(current, "children", None)
        if children is None:
            continue
        if isinstance(children, (list, tuple)):
            stack.extend(child for child in children if child is not None)
        elif isinstance(children, str):
            parts.append(children)
        elif not isinstance(children, (int, float)):
            stack.append(children)
    return " ".join(parts)


def _props(node) -> dict:
    return node.to_plotly_json().get("props", {})


def _result(
    *,
    rows: list[dict] | None = None,
    months: list[str] | None = None,
    partial: list[str] | None = None,
    total_orders: int = 1234,
) -> QueryRunResult:
    return QueryRunResult(
        plan_id="plan-1",
        template_id="don-theo-thang",
        template_title="Số đơn theo tháng",
        mediated_query_text="SELECT ...",
        rewrite_plan=[RewriteStep(1, "don_hang", "olist_orders_dataset")],
        source_sql="SELECT ...",
        rows=rows if rows is not None else [{"thang": "2018-08", "trang_thai": "delivered", "so_don": 1234}],
        row_count=len(rows) if rows is not None else 1,
        elapsed_ms=42,
        total_orders=total_orders,
        months=months if months is not None else ["2018-08"],
        partial=partial if partial is not None else [],
    )


def _full_result() -> QueryRunResult:
    months = [f"2017-{index:02d}" for index in range(1, 13)]
    rows = [{"thang": month, "trang_thai": "delivered", "so_don": 10} for month in months]
    return _result(rows=rows, months=months, total_orders=120)


def test_pending_state_means_no_run_yet_without_showing_zero():
    card = card_module.build_integration_card(state=card_module.STATE_PENDING)
    text = _text(card)

    assert "Chưa chạy" in text
    assert "Chưa chạy truy vấn lần nào" in text
    # TS-U1-2: vùng đọc kết quả truy vấn in-memory, nên "chạy pipeline" không phải đường tới số liệu.
    assert "src.pipeline" not in text
    assert "0" not in text


def test_empty_state_is_a_finished_run_with_no_rows():
    card = card_module.build_integration_card(state=card_module.STATE_EMPTY)
    text = _text(card)

    assert "Rỗng" in text
    assert "Truy vấn chạy xong nhưng không có đơn nào" in text
    assert "0" not in text


def test_loading_state_names_the_state_and_shows_a_skeleton():
    card = card_module.build_integration_card(state=card_module.STATE_LOADING)
    text = _text(card)

    assert "Đang tải" in text
    assert len(card.children) >= 2


def test_full_state_shows_total_and_months():
    card = card_module.build_integration_card(_full_result(), state=card_module.STATE_FULL)
    text = _text(card)

    assert "Đầy đủ" in text
    assert "120" in text
    assert "2017-01" in text
    assert "2017-12" in text
    assert "42 ms" in text


def test_partial_state_names_what_is_missing():
    result = _result(partial=["thiếu tháng 2018-07", "thiếu trạng thái shipped"])
    card = card_module.build_integration_card(result, state=card_module.STATE_PARTIAL)
    text = _text(card)

    assert "Một phần" in text
    assert "thiếu tháng 2018-07" in text
    assert "thiếu trạng thái shipped" in text


def test_error_state_explains_the_failure_and_offers_retry():
    card = card_module.build_integration_card(
        state=card_module.STATE_ERROR, error="Không đọc được dữ liệu nguồn."
    )
    text = _text(card)

    assert "Lỗi" in text
    assert "Không đọc được dữ liệu nguồn." in text
    assert "Thử lại" in text


def test_error_state_keeps_the_previous_result_with_a_time_label():
    card = card_module.build_integration_card(
        _full_result(),
        state=card_module.STATE_ERROR,
        error="Truy vấn nguồn lỗi.",
        previous=_full_result(),
        previous_at=datetime(2018, 8, 31, 14, 5, 9),
    )
    text = _text(card)

    assert "kết quả lần trước" in text
    assert "14:05:09" in text
    assert "120" in text


def test_every_state_label_has_a_word_and_an_icon():
    for state in (
        card_module.STATE_EMPTY,
        card_module.STATE_LOADING,
        card_module.STATE_FULL,
        card_module.STATE_PARTIAL,
        card_module.STATE_ERROR,
    ):
        card = card_module.build_integration_card(_result(partial=["thiếu tháng 2018-07"]), state=state)
        status = [node for node in _walk(card) if _props(node).get("className") == "integration-status"]
        assert status, state
        assert _props(status[0]).get("data-state") == state
        assert card_module.STATE_ICONS[state] in _text(status[0])


def test_interactive_elements_are_focusable_buttons_with_test_ids():
    cards = [
        card_module.build_integration_card(state=card_module.STATE_EMPTY),
        card_module.build_integration_card(state=card_module.STATE_ERROR, error="hỏng"),
    ]
    for card in cards:
        buttons = [node for node in _walk(card) if isinstance(node, html.Button)]
        assert buttons
        for button in buttons:
            assert _props(button).get("data-testid")
            assert not _props(button).get("style")


def test_load_tab_config_reads_the_shipped_contract():
    tab = card_module.load_tab_config(ROOT / "config" / "integration-tab.yaml")

    assert tab.tab_id == "tich-hop"
    assert tab.tab_label == "Tích hợp"
    assert tab.card_ids == (
        "luoc-do-trung-gian",
        "viet-lai-truy-van",
        "ghep-ban-ghi",
        "chon-nguon",
    )
    assert tab.callback_ids == ("tich-hop-cap-nhat",)


def test_tab_config_carries_card_ids_and_result_regions():
    """ADR-U6-S2 + C9: `card_ids` cho thẻ, `result_region_ids` cho vùng kết quả."""

    names = {field.name for field in fields(card_module.TabConfig)}

    assert names == {"tab_id", "tab_label", "card_ids", "callback_ids", "result_region_ids"}
    assert not hasattr(card_module, "build_integration_tab")


def test_load_tab_config_requires_card_ids(tmp_path: Path):
    path = tmp_path / "integration-tab.yaml"
    path.write_text(
        "tab_id: tich-hop\ntab_label: Tích hợp\ncallback_ids:\n  - tich-hop-cap-nhat\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError) as caught:
        card_module.load_tab_config(path)

    assert "card_ids" in str(caught.value)


def test_full_state_requires_twelve_months_and_all_eight_statuses():
    """Definition of "Đầy đủ": a full 12-month window AND no missing status (BR1.8)."""

    twelve_months = [f"2017-{month:02d}" for month in range(1, 13)]

    complete = _result(months=twelve_months, partial=[])
    assert card_module._state_for(complete) == card_module.STATE_FULL

    missing_status = _result(months=twelve_months, partial=["thiếu trạng thái approved"])
    assert card_module._state_for(missing_status) == card_module.STATE_PARTIAL


def test_headline_figures_name_their_scope():
    result = _result()
    text = _text(card_module.build_integration_card(result, state=card_module.STATE_FULL))

    assert "Tổng toàn kỳ" in text
    assert "dòng của cả kỳ" in text
    assert "dòng hiển thị" in text


def _make_config(tmp_path: Path, orders_rows: tuple[str, ...]):
    dataset = tmp_path / "dataset"
    dataset.mkdir(exist_ok=True)
    (dataset / "olist_orders_dataset.csv").write_text(
        ORDERS_HEADER + "\n" + "\n".join(orders_rows) + "\n", encoding="utf-8"
    )
    (dataset / "olist_customers_dataset.csv").write_text(CUSTOMERS_HEADER + "\n", encoding="utf-8")
    schema = tmp_path / "mediated-schema.yaml"
    schema.write_text(SCHEMA_YAML, encoding="utf-8")
    tab_path = tmp_path / "integration-tab.yaml"
    tab_path.write_text(
        (ROOT / "config" / "integration-tab.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
paths:
  raw_csv_dir: "{dataset.as_posix()}"
  data_dir: data
  logs_dir: logs
  temp_dir: data/.tmp
  mediated_schema_path: "{schema.as_posix()}"
  integration_tab_path: "{tab_path.as_posix()}"
""",
        encoding="utf-8",
    )
    return load_config(config_path)


def _reset_card_state():
    card_module.reset_last_result()


def test_render_integration_card_shows_numbers_on_success(tmp_path: Path):
    _reset_card_state()
    config = _make_config(tmp_path, ("o1,c1,delivered,2018-08-01 10:00:00,,,,",))

    children = card_module.render_integration_card(config)

    text = _text(html.Div(children))
    assert "1" in text
    assert "Lỗi" not in text


def test_render_integration_card_never_reads_the_warehouse(tmp_path: Path):
    """TS-U1-2: một đường dữ liệu duy nhất — số đến từ truy vấn in-memory, không từ `warehouse/`/mart."""

    _reset_card_state()
    config = _make_config(tmp_path, ("o1,c1,delivered,2018-08-01 10:00:00,,,,",))
    missing = tmp_path / "khong-ton-tai"
    config = replace(
        config,
        duckdb_path=missing / "olist.duckdb",
        marts_dir=missing / "marts",
        data_dir=missing / "data",
    )

    children = card_module.render_integration_card(config)

    text = _text(html.Div(children))
    assert "1" in text
    assert "Lỗi" not in text


def test_render_integration_card_returns_error_tree_instead_of_raising(tmp_path: Path, monkeypatch):
    _reset_card_state()
    config = _make_config(tmp_path, ("o1,c1,delivered,2018-08-01 10:00:00,,,,",))

    def explode(*args, **kwargs):
        raise SchemaError("thiếu cột nguồn")

    monkeypatch.setattr(card_module, "load_don_hang", explode)
    children = card_module.render_integration_card(config)

    text = _text(html.Div(children))
    assert "Lỗi" in text
    assert "Thử lại" in text


def test_render_integration_card_keeps_previous_result_after_a_failure(tmp_path: Path, monkeypatch):
    _reset_card_state()
    config = _make_config(tmp_path, ("o1,c1,delivered,2018-08-01 10:00:00,,,,",))
    card_module.render_integration_card(config)

    def explode(*args, **kwargs):
        raise QueryExecutionError("SQL nguồn lỗi")

    monkeypatch.setattr(card_module, "run_monthly_orders", explode)
    monkeypatch.setattr(card_module, "load_don_hang", lambda *a, **k: _fake_load())

    children = card_module.render_integration_card(config)
    text = _text(html.Div(children))

    assert "kết quả lần trước" in text


def _fake_load():
    from src.integration.models import DonHang, LoadResult

    order = DonHang(
        ma_don="o1",
        ngay_dat=datetime(2018, 8, 1, 10, 0),
        trang_thai="delivered",
        ma_khach="c1",
    )
    return LoadResult(orders=[order], rows_in=1, rows_dropped=0, drop_reasons={}, elapsed_ms=1)


def test_render_integration_card_shows_the_empty_state_without_rows(tmp_path: Path, monkeypatch):
    _reset_card_state()
    config = _make_config(tmp_path, ("o1,c1,delivered,2018-08-01 10:00:00,,,,",))
    empty = _result(rows=[], months=[], total_orders=0)
    monkeypatch.setattr(card_module, "load_don_hang", lambda *a, **k: _fake_load())
    monkeypatch.setattr(card_module, "run_monthly_orders", lambda *a, **k: empty)

    children = card_module.render_integration_card(config)
    text = _text(html.Div(children))

    assert "Rỗng" in text
    assert "0" not in text


def test_render_integration_card_never_raises_on_a_broken_result(tmp_path: Path, monkeypatch):
    _reset_card_state()
    config = _make_config(tmp_path, ("o1,c1,delivered,2018-08-01 10:00:00,,,,",))
    broken = _result()
    broken.rows = None  # type: ignore[assignment]
    monkeypatch.setattr(card_module, "load_don_hang", lambda *a, **k: _fake_load())
    monkeypatch.setattr(card_module, "run_monthly_orders", lambda *a, **k: broken)

    children = card_module.render_integration_card(config)

    assert "Lỗi" in _text(html.Div(children))


def test_build_integration_card_rejects_an_unknown_state():
    with pytest.raises(ValueError):
        card_module.build_integration_card(state="khong-co")


def test_load_tab_config_rejects_a_missing_file(tmp_path: Path):
    with pytest.raises(ConfigurationError):
        card_module.load_tab_config(tmp_path / "khong-co.yaml")


def test_load_tab_config_rejects_invalid_yaml(tmp_path: Path):
    path = tmp_path / "integration-tab.yaml"
    path.write_text("tab_id: [khong dong ngoac\n", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        card_module.load_tab_config(path)


def test_load_tab_config_rejects_a_non_mapping(tmp_path: Path):
    path = tmp_path / "integration-tab.yaml"
    path.write_text("- chi-la-mot-danh-sach\n", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        card_module.load_tab_config(path)


def test_load_tab_config_requires_tab_id_and_label(tmp_path: Path):
    path = tmp_path / "integration-tab.yaml"
    path.write_text("tab_id: tich-hop\n", encoding="utf-8")

    with pytest.raises(ConfigurationError):
        card_module.load_tab_config(path)

    path.write_text("tab_label: Tích hợp\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        card_module.load_tab_config(path)


def test_load_tab_config_requires_id_lists(tmp_path: Path):
    path = tmp_path / "integration-tab.yaml"
    path.write_text(
        "tab_id: tich-hop\ntab_label: Tích hợp\ncard_ids: []\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError):
        card_module.load_tab_config(path)
