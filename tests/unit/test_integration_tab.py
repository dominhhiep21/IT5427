"""Unit tests for the "Tích hợp" tab: bốn thẻ, bốn màn hình chi tiết, năm trạng thái, năm callback."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

import pytest
from dash import Dash, html

from src.common.exceptions import (
    ConfigurationError,
    LinkageResultInvalidError,
    LinkageResultMissingError,
    NoSourceAvailableError,
    QueryExecutionError,
)
from src.config import load_config
from src.integration import tab as tab_module
from src.integration.card import (
    STATE_EMPTY,
    STATE_ERROR,
    STATE_FULL,
    STATE_LOADING,
    STATE_PARTIAL,
    load_tab_config,
)
from src.integration.models import (
    KpiComparison,
    KpiDefinition,
    MediatedSchemaView,
    PartialInfo,
    QueryRunResult,
    RewriteStep,
    SourceCatalogue,
    SourceChoice,
    SourceProfile,
)
from src.integration.schema import EntityMapping, FieldMapping

ROOT = Path(__file__).resolve().parents[2]

ORDERS_CSV = (
    "order_id,customer_id,order_status,order_purchase_timestamp,"
    "order_approved_at,order_delivered_carrier_date,order_delivered_customer_date,"
    "order_estimated_delivery_date\n"
    "o1,c1,delivered,2018-08-01 10:00:00,,,,2018-08-20 00:00:00\n"
)

PRODUCTS_CSV = "product_id,product_category_name\np1,beleza_saude\n"

SCHEMA_YAML = """
schema_kind: GAV
entities:
  - name: don_hang
    description: Một dòng cho mỗi đơn hàng
    source_tables:
      - olist_orders_dataset
    fields:
      - field_name: ma_don
        source_table: olist_orders_dataset
        source_column: order_id
        data_type: string
      - field_name: ngay_dat
        source_table: olist_orders_dataset
        source_column: order_purchase_timestamp
        data_type: timestamp
  - name: san_pham
    description: Một dòng cho mỗi sản phẩm
    source_tables:
      - olist_products_dataset
    fields:
      - field_name: ma_san_pham
        source_table: olist_products_dataset
        source_column: product_id
        data_type: string
      - field_name: ten_danh_muc
        source_table: olist_products_dataset
        source_column: product_category_name
        data_type: string
"""


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


def _by_testid(node, testid: str) -> list:
    return [item for item in _walk(node) if _props(item).get("data-testid") == testid]


def _by_state(node, state: str) -> list:
    return [item for item in _walk(node) if _props(item).get("data-state") == state]


def _linkage_payload(
    target: str = "customer",
    *,
    correct_rate: float | None = 0.5,
    pairs_matched: int = 16,
    skipped: list | None = None,
) -> dict:
    return {
        "target_entity": target,
        "run_id": "20261108T000000-1",
        "computed_at": "2026-11-08T00:00:00+00:00",
        "threshold": 0.85,
        "summary": {
            "pairs_scored": 900,
            "pairs_matched": pairs_matched,
            "pairs_review": 3,
            "pairs_skipped": 4,
            "duplicate_groups": 2 if target == "customer" else None,
            "correct_rate": correct_rate,
            "correct_rate_sample": 8 if correct_rate is not None else None,
            "correct_rate_reason": (
                None if correct_rate is not None else "người bán không có khoá mốc trong nguồn"
            ),
        },
        "pairs": [
            {
                "pair_id": "abc",
                "record_a": "c1",
                "record_b": "c2",
                "score": 0.9123,
                "decision": "Ghép",
                "is_correct": True,
            },
            {
                "pair_id": "def",
                "record_a": "c3",
                "record_b": "c4",
                "score": 0.85,
                "decision": "Xem lại",
                "is_correct": False,
            },
        ],
        "skipped": (
            skipped
            if skipped is not None
            else [
                {
                    "skip_id": "skip-1",
                    "record_a": "c5",
                    "record_b": "c6",
                    "missing_fields": ["city"],
                    "reason": "thiếu thành phố",
                }
            ]
        ),
    }


def _schema_view(partial: PartialInfo | None = None) -> MediatedSchemaView:
    orders = EntityMapping(
        name="don_hang",
        description="Một dòng cho mỗi đơn hàng",
        source_tables=("olist_orders_dataset",),
        fields=(
            FieldMapping("ma_don", "olist_orders_dataset", "order_id", "string", True),
            FieldMapping("ngay_dat", "olist_orders_dataset", "order_purchase_timestamp", "timestamp", True),
        ),
    )
    products = EntityMapping(
        name="san_pham",
        description="Một dòng cho mỗi sản phẩm",
        source_tables=("olist_products_dataset",),
        fields=(
            FieldMapping("ten_danh_muc", "olist_products_dataset", "product_category_name", "string", True),
        ),
    )
    entities = (orders, products)
    return MediatedSchemaView(
        schema_kind="GAV",
        entities=entities,
        mappings={entity.name: entity.fields for entity in entities},
        elapsed_ms=3,
        partial=partial,
    )


def _catalogue(choices: tuple[SourceChoice, ...] = ()) -> SourceCatalogue:
    profiles = (
        SourceProfile(
            source_name="olist_csv",
            label="CSV Olist",
            tables=("olist_orders_dataset",),
            covered_fields=("don_hang.ma_don", "don_hang.ngay_dat"),
            coverage="Đủ hai bảng: đơn hàng, sản phẩm",
            has_data=True,
            cost_level=1,
            latency_ms=120,
            is_simulated=False,
        ),
        SourceProfile(
            source_name="ibge_cache",
            label="Cache IBGE",
            tables=("olist_customers_dataset",),
            covered_fields=("don_hang.bang_giao",),
            coverage="Chỉ có trường đơn hàng",
            has_data=True,
            cost_level=3,
            latency_ms=40,
            is_simulated=False,
        ),
        SourceProfile(
            source_name="partner_simulated",
            label="Đối tác mô phỏng",
            tables=("olist_orders_dataset",),
            covered_fields=("don_hang.ma_don",),
            coverage="Chỉ có trường đơn hàng",
            has_data=False,
            cost_level=2,
            latency_ms=10,
            is_simulated=True,
        ),
    )
    return SourceCatalogue(
        sources=profiles,
        choices=choices,
        query_fields={"doanh_thu_theo_thang": ("don_hang.ma_don", "don_hang.ngay_dat")},
        partial_reason="chưa có kết quả đề xuất cho truy vấn đang chọn",
        pending_query_id="doanh_thu_theo_thang",
    )


def _result(
    *,
    template_id: str = "doanh_thu_theo_thang",
    rows: list[dict] | None = None,
    partial: list[str] | None = None,
) -> QueryRunResult:
    return QueryRunResult(
        plan_id="plan-1",
        template_id=template_id,
        template_title="Doanh thu theo tháng",
        mediated_query_text="SELECT thang(ngay_dat) FROM don_hang",
        rewrite_plan=[
            RewriteStep(1, "don_hang", "olist_orders_dataset"),
            RewriteStep(2, "mat_hang", "olist_order_items_dataset", "don_hang.ma_don = mat_hang.ma_don"),
        ],
        source_sql="SELECT strftime(order_purchase_timestamp, '%Y-%m') FROM olist_orders_dataset",
        rows=rows if rows is not None else [{"thang": "2018-08", "gia_tri": 1234.5, "so_dong": 7}],
        row_count=1,
        elapsed_ms=42,
        total_orders=7,
        months=["2018-08"],
        partial=partial if partial is not None else [],
        kpi_definitions=[
            KpiDefinition(
                kpi_id="doanh_thu_theo_thang",
                title="Doanh thu theo tháng",
                formula="tổng price + freight_value của đơn delivered, nhóm theo tháng",
                revenue_definition="price + freight_value của đơn delivered",
                unit="BRL",
            )
        ],
        kpi_comparison=[
            KpiComparison(
                kpi_id="doanh_thu_theo_thang",
                group_key="__all__",
                expected_value=1234.5,
                actual_value=1234.5,
                delta=0.0,
                tolerance=0.01,
                matches=True,
            )
        ],
    )


def _write_dataset(tmp_path: Path) -> Path:
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    (dataset / "olist_orders_dataset.csv").write_text(ORDERS_CSV, encoding="utf-8")
    (dataset / "olist_products_dataset.csv").write_text(PRODUCTS_CSV, encoding="utf-8")
    return dataset


SOURCES_YAML = """
sources:
  - source_name: olist_csv
    label: CSV Olist
    tables:
      - olist_orders_dataset
    covered_fields:
      - don_hang.ma_don
      - don_hang.ngay_dat
    has_data: true
    cost_level: 1
    latency_ms: 120
    is_simulated: false
  - source_name: ibge_cache
    label: Cache IBGE
    tables:
      - olist_products_dataset
    covered_fields:
      - san_pham.ten_danh_muc
    has_data: true
    cost_level: 3
    latency_ms: 40
    is_simulated: false
  - source_name: partner_simulated
    label: Đối tác mô phỏng
    tables:
      - olist_orders_dataset
    covered_fields:
      - don_hang.ma_don
    has_data: false
    cost_level: 2
    latency_ms: 10
    is_simulated: true
query_fields:
  doanh_thu_theo_thang:
    - don_hang.ma_don
    - don_hang.ngay_dat
  doanh_thu_theo_danh_muc:
    - san_pham.ten_danh_muc
  ty_le_giao_tre_theo_bang:
    - don_hang.ma_don
"""


def _config(
    tmp_path: Path,
    *,
    schema_text: str = SCHEMA_YAML,
    linkage: dict | None = None,
    seller: dict | None = None,
) -> object:
    dataset = _write_dataset(tmp_path)
    schema = tmp_path / "mediated-schema.yaml"
    schema.write_text(schema_text, encoding="utf-8")
    tab_path = tmp_path / "integration-tab.yaml"
    tab_path.write_text(
        (ROOT / "config" / "integration-tab.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "integration-sources.yaml").write_text(SOURCES_YAML, encoding="utf-8")
    integration = tmp_path / "integration"
    integration.mkdir()
    if linkage is not None:
        (integration / "linkage-customer.json").write_text(
            json.dumps(linkage, ensure_ascii=False), encoding="utf-8"
        )
    if seller is not None:
        (integration / "linkage-seller.json").write_text(
            json.dumps(seller, ensure_ascii=False), encoding="utf-8"
        )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
paths:
  raw_csv_dir: "{dataset.as_posix()}"
  data_dir: data
  logs_dir: logs
  temp_dir: data/.tmp
  integration_dir: "{integration.as_posix()}"
  integration_sources_path: "{(tmp_path / "integration-sources.yaml").as_posix()}"
  mediated_schema_path: "{schema.as_posix()}"
  integration_tab_path: "{tab_path.as_posix()}"
""",
        encoding="utf-8",
    )
    return load_config(config_path)


@pytest.fixture(autouse=True)
def _clean_tab_state():
    tab_module.reset_tab_state()
    yield
    tab_module.reset_tab_state()


# --- Khung tab: bốn thẻ, bốn màn hình chi tiết ---------------------------------


def test_integration_tab_draws_four_empty_cards_and_no_detail_screen():
    tab_config = load_tab_config(ROOT / "config" / "integration-tab.yaml")

    children = tab_module.IntegrationTab(tab_config)
    text = _text(html.Div(children))

    cards = _by_testid(html.Div(children), "integration-card")
    assert len(cards) == 4
    for card in cards:
        assert _props(card).get("data-state") == STATE_EMPTY
    assert "Lược đồ trung gian" in text
    assert "Chọn nguồn" in text
    assert not _by_testid(html.Div(children), "back-to-overview")


def test_each_card_has_two_metric_lines_and_one_open_button():
    tab_config = load_tab_config(ROOT / "config" / "integration-tab.yaml")

    children = tab_module.IntegrationTab(tab_config)
    tree = html.Div(children)

    for card_id in tab_config.card_ids:
        metrics = _by_testid(tree, f"card-{card_id}-metric")
        assert len(metrics) == 2, card_id
        assert all(str(_text(item)).strip() for item in metrics)
        assert _by_testid(tree, f"card-{card_id}-open"), card_id


def test_integration_tab_rejects_an_unknown_result_region():
    """C9: mọi id trong `result_region_ids` phải có hàm dựng; id lạ không được bỏ qua im lặng."""

    tab_config = load_tab_config(ROOT / "config" / "integration-tab.yaml")
    broken = tab_module.TabConfig(
        tab_id=tab_config.tab_id,
        tab_label=tab_config.tab_label,
        card_ids=tab_config.card_ids,
        callback_ids=tab_config.callback_ids,
        result_region_ids=("vung-khong-ton-tai",),
    )

    with pytest.raises(ConfigurationError) as caught:
        tab_module.IntegrationTab(broken)

    assert "vung-khong-ton-tai" in str(caught.value)


def test_integration_tab_rejects_a_contract_missing_one_card():
    tab_config = load_tab_config(ROOT / "config" / "integration-tab.yaml")
    broken = tab_module.TabConfig(
        tab_id=tab_config.tab_id,
        tab_label=tab_config.tab_label,
        card_ids=tab_config.card_ids[:3],
        callback_ids=tab_config.callback_ids,
    )

    with pytest.raises(ConfigurationError) as caught:
        tab_module.IntegrationTab(broken)

    assert "chon-nguon" in str(caught.value)


@pytest.mark.parametrize(
    "state",
    [STATE_EMPTY, STATE_LOADING, STATE_FULL, STATE_PARTIAL, STATE_ERROR],
)
def test_state_block_uses_the_five_existing_tokens(state):
    block = tab_module.StateBlock(state, "câu giải thích")

    assert _props(block).get("data-state") == state
    assert "câu giải thích" in _text(block)
    assert _text(block).strip()


def test_state_block_lists_what_is_missing_without_a_fake_zero():
    block = tab_module.StateBlock(STATE_PARTIAL, "còn thiếu", ["thiếu thực thể mat_hang"])

    text = _text(block)
    assert "thiếu thực thể mat_hang" in text
    assert "0" not in text


# --- Tổng quan: hai dòng số liệu mỗi thẻ ---------------------------------------


def test_load_overview_fills_two_metric_lines_per_card(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())
    tab_config = load_tab_config(config.integration_tab_path)

    children = tab_module.fill_overview(config, tab_config.tab_id, tab_config)
    tree = html.Div(children)
    text = _text(tree)

    assert len(_by_testid(tree, "integration-card")) == 4
    assert "Số thực thể" in text
    assert "Số trường" in text
    assert "Nguồn có dữ liệu" in text
    assert "Cặp vượt ngưỡng" in text


def test_load_overview_does_nothing_when_another_tab_is_selected(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())
    tab_config = load_tab_config(config.integration_tab_path)

    assert tab_module.fill_overview(config, "overview", tab_config) is tab_module.no_update


def test_load_overview_keeps_a_broken_contract_to_its_own_card(tmp_path: Path):
    config = _config(tmp_path, schema_text="schema_kind: GAV\nentities: []\n", linkage=_linkage_payload())
    tab_config = load_tab_config(config.integration_tab_path)

    specs = tab_module.card_specs(config, tab_config)
    states = {spec.card_id: spec.state for spec in specs}

    assert states["luoc-do-trung-gian"] == STATE_ERROR
    assert states["ghep-ban-ghi"] == STATE_FULL
    assert states["viet-lai-truy-van"] == STATE_EMPTY


def test_linkage_card_is_empty_with_the_pipeline_hint_when_the_file_is_missing(tmp_path: Path):
    config = _config(tmp_path)
    tab_config = load_tab_config(config.integration_tab_path)

    spec = tab_module.linkage_card(config, tab_config.card_ids[2])

    assert spec.state == STATE_EMPTY
    assert "src.pipeline run --stage all" in spec.message
    assert "0" not in " ".join(spec.metrics)


def test_linkage_card_is_an_error_when_the_file_is_broken(tmp_path: Path):
    config = _config(tmp_path, linkage={"target_entity": "customer"})
    tab_config = load_tab_config(config.integration_tab_path)

    spec = tab_module.linkage_card(config, tab_config.card_ids[2])

    assert spec.state == STATE_ERROR
    assert "kết quả ghép" in spec.message


def test_sources_card_is_partial_before_any_suggestion(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())
    tab_config = load_tab_config(config.integration_tab_path)

    spec = tab_module.sources_card(config, tab_config.card_ids[3])

    assert spec.state == STATE_PARTIAL
    assert "chưa có kết quả đề xuất" in spec.message
    assert "doanh_thu_theo_thang" in spec.message


# --- Điều hướng: route và reload ----------------------------------------------


@pytest.mark.parametrize(
    ("card_id", "title"),
    [
        ("luoc-do-trung-gian", "Lược đồ trung gian"),
        ("viet-lai-truy-van", "Truy vấn viết lại"),
        ("ghep-ban-ghi", "Ghép bản ghi"),
        ("chon-nguon", "Chọn nguồn"),
    ],
)
def test_route_opens_the_screen_named_by_the_card(tmp_path: Path, card_id: str, title: str):
    config = _config(tmp_path, linkage=_linkage_payload())

    hidden, screen = tab_module.route_screen(config, f"card-{card_id}-open", clicked=1)

    assert hidden is True
    assert title in _text(screen)


def test_route_back_shows_the_overview_again_without_re_reading_the_cards(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())

    assert tab_module.route_screen(config, {"type": "back", "screen": "schema"}, clicked=1) == (
        False,
        None,
    )


def test_route_ignores_the_zero_click_dash_sends_when_the_buttons_are_created(tmp_path: Path):
    """Dash gọi lại callback ngay khi thành phần khớp mẫu được tạo, với `n_clicks = 0`.

    Bỏ qua lần gọi đó là điều kiện để mở tab "Tích hợp" không tự bật màn hình chi tiết đầu tiên
    (lỗi thật gặp 2026-11-09 trên trình duyệt, ngay sau khi sửa lỗi `back-schema`).
    """

    config = _config(tmp_path, linkage=_linkage_payload())

    assert tab_module.route_screen(config, "card-luoc-do-trung-gian-open", clicked=0) is tab_module.no_update
    assert (
        tab_module.route_screen(config, {"type": "back", "screen": "schema"}, clicked=0) is tab_module.no_update
    )


def test_route_ignores_the_first_paint(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())

    assert tab_module.route_screen(config, None) is tab_module.no_update


def test_route_reads_a_reload_request_from_the_token(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())

    hidden, screen = tab_module.route_screen(config, "reload-token", {"screen": "linkage", "seq": 2})

    assert hidden is True
    assert "Ghép bản ghi" in _text(screen)


def test_reload_token_names_the_screen_and_bumps_the_sequence():
    assert tab_module.reload_token(
        {"type": "reload", "screen": "linkage"}, {"screen": "linkage", "seq": 4}, clicked=1
    ) == {
        "screen": "linkage",
        "seq": 5,
    }


def test_reload_does_not_read_anything_without_a_click():
    assert tab_module.reload_token(None, {"screen": "linkage", "seq": 4}) is tab_module.no_update
    assert (
        tab_module.reload_token({"type": "reload", "screen": "linkage"}, {"seq": 4}, clicked=0)
        is tab_module.no_update
    )


# --- Bốn màn hình chi tiết -----------------------------------------------------


def test_every_detail_screen_offers_back_and_reload_buttons():
    for screen in tab_module.SCREENS:
        node = tab_module.DetailScreen(screen, html.Div("thân"))

        assert _by_testid(node, "back-to-overview"), screen
        assert _by_testid(node, "reload-screen"), screen
        assert tab_module.SCREEN_TITLES[screen] in _text(node)


def test_schema_panel_has_three_mapping_columns_and_the_gav_label():
    panel = tab_module.SchemaPanel(_schema_view())
    text = _text(panel)
    headers = [
        _text(item) for item in _walk(panel) if item.__class__.__name__ in {"TableTh", "TableHeaderCell", "Th"}
    ]

    assert "GAV" in text
    assert "Trường trung gian" in headers
    assert "Nguồn" in headers
    assert "Kiểu dữ liệu" in headers
    assert "olist_orders_dataset.order_id" in text
    assert "timestamp" in text


def test_schema_panel_lists_every_entity_as_its_own_tab():
    panel = tab_module.SchemaPanel(_schema_view())
    tabs = [item for item in _walk(panel) if item.__class__.__name__ == "Tabs"]

    assert [child.value for child in tabs[0].children] == ["don_hang", "san_pham"]
    assert "Một dòng cho mỗi sản phẩm" in _text(panel)


def test_schema_panel_partial_names_the_missing_entity():
    view = _schema_view(partial=PartialInfo(missing=("mat_hang",), reason="thiếu tệp khai báo"))
    panel = tab_module.SchemaPanel(view)

    assert _props(panel).get("data-state") == STATE_PARTIAL
    assert "mat_hang" in _text(panel)


def test_query_panel_shows_two_sql_bodies_the_plan_and_the_kpi_definitions():
    panel = tab_module.QueryPanel("doanh_thu_theo_thang", _result())
    text = _text(panel)

    assert "SELECT thang(ngay_dat) FROM don_hang" in text
    assert "SELECT strftime(order_purchase_timestamp" in text
    assert "olist_order_items_dataset" in text
    assert "don_hang.ma_don = mat_hang.ma_don" in text
    assert "price + freight_value của đơn delivered" in text
    assert _by_testid(panel, "query-rows")
    assert _by_testid(panel, "kpi-definitions")


def test_query_panel_marks_the_previous_result_as_old_on_failure():
    panel = tab_module.QueryPanel(
        "doanh_thu_theo_thang",
        _result(),
        message="Truy vấn 'Doanh thu theo tháng' lỗi khi chạy.",
    )
    text = _text(panel)

    assert "kết quả cũ" in text.lower()
    assert "Doanh thu theo tháng" in text
    assert _by_testid(panel, "retry-query")


def test_query_panel_starts_empty_with_a_hint():
    panel = tab_module.QueryPanel("doanh_thu_theo_thang", None)

    assert _props(panel).get("data-state") == STATE_EMPTY
    assert "Chạy" in _text(panel)


def test_run_query_body_reports_a_failed_run_without_leaking_the_exception(tmp_path: Path, monkeypatch):
    config = _config(tmp_path, linkage=_linkage_payload())

    def explode(*args, **kwargs):
        raise QueryExecutionError("Không tìm thấy tệp nguồn: olist_orders_dataset.csv")

    monkeypatch.setattr(tab_module, "select_source", lambda catalogue, query_id, logger=None: _selection())
    monkeypatch.setattr(tab_module, "run_template", explode)

    node = tab_module.run_query_body(config, "doanh_thu_theo_thang")

    text = _text(node)
    assert _props(node).get("data-state") == STATE_ERROR
    assert "olist_orders_dataset.csv" not in text
    assert "Không chạy được truy vấn" in text


def test_run_query_body_keeps_the_result_for_the_overview_card(tmp_path: Path, monkeypatch):
    config = _config(tmp_path, linkage=_linkage_payload())
    monkeypatch.setattr(tab_module, "select_source", lambda catalogue, query_id, logger=None: _selection())
    monkeypatch.setattr(tab_module, "run_template", lambda *a, **k: _result())

    node = tab_module.run_query_body(config, "doanh_thu_theo_thang")
    tab_config = load_tab_config(config.integration_tab_path)
    spec = tab_module.card_specs(config, tab_config)[1]

    assert _props(node).get("data-state") == STATE_FULL
    assert spec.state == STATE_FULL
    assert "1" in spec.metrics[0]


def _selection():
    from src.integration.models import SourceSelection

    catalogue = _catalogue()
    choice = SourceChoice(
        query_id="doanh_thu_theo_thang",
        source_name="olist_csv",
        is_selected=True,
        reason="được chọn: đủ trường",
    )
    return SourceSelection(
        query_id="doanh_thu_theo_thang",
        selected_sources=(choice,),
        rejected_sources=(),
        catalogue=catalogue,
    )


def test_linkage_panel_shows_the_threshold_metrics_pairs_and_the_skipped_line():
    panel = tab_module.LinkagePanel(_linkage_payload())
    text = _text(panel)

    assert "0,85" in text
    assert "16" in text
    assert "50,00%" in text
    assert "8/16" in text
    assert "0,91" in text
    assert "Xem lại" in text
    assert _by_testid(panel, "linkage-skipped")
    assert "thiếu thành phố" in text


def test_linkage_panel_says_when_no_pair_was_skipped():
    panel = tab_module.LinkagePanel(_linkage_payload(skipped=[]))

    assert "Không có cặp bị bỏ qua" in _text(panel)
    assert _by_testid(panel, "linkage-skipped")


def test_linkage_panel_caps_the_skipped_table_instead_of_building_every_row():
    """C5 thật có 12.613 cặp bị bỏ qua; dựng hết thành DOM làm trình duyệt treo hàng phút
    (gặp 2026-11-09 khi mở thẻ "Ghép bản ghi"). Chỉ hiển thị phần đầu và nói rõ đã cắt.
    """

    many = [{"record_a": f"a{i}", "record_b": f"b{i}", "reason": "thiếu thành phố"} for i in range(1000)]
    payload = _linkage_payload(skipped=many)
    panel = tab_module.LinkagePanel(payload)
    rows = [node for node in _walk(panel) if node.__class__.__name__ == "TableTr"]

    # hai dòng tiêu đề + bảng cặp đầy đủ + 200 dòng đầu của bảng bỏ qua
    assert len(rows) == 2 + len(payload["pairs"]) + tab_module.SKIPPED_ROWS_SHOWN
    assert _by_testid(panel, "linkage-skipped-note")
    assert "200 trong 1.000" in _text(panel)


def test_linkage_panel_says_the_correct_rate_cannot_be_measured_for_sellers():
    panel = tab_module.LinkagePanel(_linkage_payload("seller", correct_rate=None))

    text = _text(panel)
    assert "Không đo được" in text
    assert "khoá mốc" in text


def test_linkage_panel_switches_between_customer_and_seller_without_a_callback():
    panel = tab_module.LinkagePanel(_linkage_payload())
    tabs = [item for item in _walk(panel) if item.__class__.__name__ == "Tabs"]
    values = [child.value for child in tabs[0].children]

    assert values == ["customer", "seller"]


def test_source_panel_lists_the_contract_facts_and_the_simulated_note():
    panel = tab_module.SourcePanel(_catalogue())
    text = _text(panel)

    assert "CSV Olist" in text
    assert "Cache IBGE" in text
    assert "nguồn mô phỏng" in text
    assert "120" in text
    assert _by_testid(panel, "suggest-source")
    assert _by_testid(panel, "source-table")


def test_source_region_updates_the_status_badge_together_with_the_table(tmp_path: Path, monkeypatch):
    """Trước 2026-11-09 huy hiệu vẫn nói "chưa có kết quả đề xuất" sau khi bấm "Đề xuất nguồn",
    vì callback chỉ thay bảng. Trạng thái và bảng phải nằm trong cùng một `Output`.
    """

    config = _config(tmp_path, linkage=_linkage_payload())
    resolved = replace(_catalogue(), partial_reason=None, pending_query_id=None)
    monkeypatch.setattr(
        tab_module,
        "select_source",
        lambda catalogue, query_id, logger=None: SimpleNamespace(catalogue=resolved),
    )

    region = tab_module.suggest_source_body(config, "doanh_thu_theo_thang")

    assert _props(region).get("data-state") == tab_module.STATE_FULL
    assert "chưa có kết quả đề xuất" not in _text(region)
    assert _by_testid(region, "source-rows")


def test_source_region_keeps_the_partial_reason_before_a_source_is_chosen():
    region = tab_module.source_region(_catalogue(), "doanh_thu_theo_thang")

    assert _props(region).get("data-state") == tab_module.STATE_PARTIAL
    assert "chưa có kết quả đề xuất" in _text(region)


def test_suggest_source_body_names_the_missing_fields_when_no_source_fits(tmp_path: Path, monkeypatch):
    config = _config(tmp_path, linkage=_linkage_payload())

    def explode(catalogue, query_id, logger=None):
        raise NoSourceAvailableError(
            "Không nguồn nào đủ trường cho truy vấn 'doanh_thu_theo_thang'.",
            ("san_pham.ten_danh_muc",),
            _catalogue(),
        )

    monkeypatch.setattr(tab_module, "select_source", explode)

    node = tab_module.suggest_source_body(config, "doanh_thu_theo_thang")

    text = _text(node)
    assert "san_pham.ten_danh_muc" in text
    assert "Không nguồn nào đủ trường" in text


def test_changing_a_selector_does_not_run_anything():
    """W3 bước 1 và W4 bước 1: chỉ nút bấm mới chạy, đổi ô chọn thì không."""

    assert tab_module.query_triggered("query-template") is False
    assert tab_module.query_triggered("run-query") is True
    assert tab_module.query_triggered("retry-query") is True
    assert tab_module.suggest_triggered("source-query") is False
    assert tab_module.suggest_triggered("suggest-source") is True


def test_source_table_body_redraws_without_calling_u5(tmp_path: Path, monkeypatch):
    config = _config(tmp_path, linkage=_linkage_payload())

    def boom(*args, **kwargs):
        raise AssertionError("không được đề xuất nguồn khi chỉ đổi truy vấn")

    monkeypatch.setattr(tab_module, "select_source", boom)

    node = tab_module.source_table_body(config, "doanh_thu_theo_thang")

    assert _by_testid(node, "source-rows")


def test_load_linkage_result_reads_the_file_and_rejects_a_missing_one(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())

    payload = tab_module.load_linkage_result(config, "customer")
    assert payload["summary"]["pairs_matched"] == 16

    with pytest.raises(LinkageResultMissingError):
        tab_module.load_linkage_result(config, "seller")


def test_load_linkage_result_rejects_a_file_without_the_summary(tmp_path: Path):
    config = _config(tmp_path, linkage={"target_entity": "customer", "pairs": [], "skipped": []})

    with pytest.raises(LinkageResultInvalidError):
        tab_module.load_linkage_result(config, "customer")


# --- Năm callback, mỗi callback một Output ------------------------------------


def _output_components(app) -> list[str]:
    """Mọi thành phần là đích của một Output, giải cả callback một lẫn nhiều Output."""

    components: list[str] = []
    for entry in app.callback_map.values():
        output = entry["output"]
        for item in output if isinstance(output, list) else [output]:
            components.append(item.split(".")[0] if isinstance(item, str) else str(item.component_id))
    return components


def test_callbacks_register_six_outputs_with_one_shared_region(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())
    tab_config = load_tab_config(config.integration_tab_path)
    app = Dash(__name__, suppress_callback_exceptions=True)

    tab_module.register_callbacks(app, config, tab_config)

    assert len(app.callback_map) == 6
    components = _output_components(app)

    assert sorted(set(components)) == sorted(
        [
            "overview-cards",
            "overview-panel",
            "screen-body",
            "query-result",
            "source-table",
            "reload-token",
            "don-theo-thang",
        ]
    )
    # Riêng vùng nguồn có hai Output (`children` + `data-state`) để huy hiệu trạng thái
    # đổi cùng bảng sau khi bấm "Đề xuất nguồn"; không vùng nào khác bị hai callback ghi.
    assert components.count("source-table") == 2


def test_every_interactive_control_is_a_real_button_with_a_test_id(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())
    tab_config = load_tab_config(config.integration_tab_path)
    tree = html.Div(
        tab_module.IntegrationTab(tab_config)
        + [
            tab_module.DetailScreen("queries", tab_module.QueryPanel("doanh_thu_theo_thang", _result())),
            tab_module.DetailScreen("sources", tab_module.SourcePanel(_catalogue())),
        ]
    )

    buttons = [item for item in _walk(tree) if item.__class__.__name__ in {"Button", "button"}]
    assert buttons
    for button in buttons:
        assert _props(button).get("data-testid"), _text(button)


def test_overview_and_route_stay_under_the_two_second_budget(tmp_path: Path):
    config = _config(tmp_path, linkage=_linkage_payload())
    tab_config = load_tab_config(config.integration_tab_path)

    started = perf_counter()
    tab_module.fill_overview(config, tab_config.tab_id, tab_config)
    tab_module.route_screen(config, f"card-{tab_config.card_ids[2]}-open")
    elapsed_ms = (perf_counter() - started) * 1000

    assert elapsed_ms < 2000
