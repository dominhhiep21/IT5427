"""Dash components and callbacks for the "Tích hợp" tab (U6 — C3, C4, C5, C6, C7, C9)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import dash_mantine_components as dmc
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html, no_update

from src.common.exceptions import (
    ConfigurationError,
    KpiMismatchError,
    LinkageResultInvalidError,
    LinkageResultMissingError,
    NoSourceAvailableError,
    PipelineError,
    QueryExecutionError,
    SchemaError,
)
from src.common.kpis import TEMPLATE_IDS, kpi
from src.common.logging import NullLogger
from src.dashboard.formatting import format_number, format_percent
from src.integration.card import (
    STATE_EMPTY,
    STATE_ERROR,
    STATE_FULL,
    STATE_LOADING,
    STATE_PARTIAL,
    STATE_PENDING,
    STATE_ICONS,
    TEXTS as CARD_TEXTS,
    TabConfig,
    build_integration_card,
    render_integration_card,
)
from src.integration.models import (
    KpiDefinition,
    MediatedSchemaView,
    QueryRunResult,
    SourceCatalogue,
)
from src.integration.rewrite import run_template
from src.integration.schema import build_field_catalogue, load_schema
from src.integration.selector import load_source_catalogue, select_source

# Năm trạng thái dùng lại đúng bộ token của src/integration/card.py (ADR-U6-S3).
STATE_TOKENS = (STATE_EMPTY, STATE_LOADING, STATE_FULL, STATE_PARTIAL, STATE_ERROR)

DEFAULT_TARGET = "customer"
CUSTOMER = "customer"
SELLER = "seller"
TARGETS = (CUSTOMER, SELLER)
TARGET_TITLES = {CUSTOMER: "Khách hàng", SELLER: "Người bán"}

CARD_SCREENS: dict[str, str] = {
    "luoc-do-trung-gian": "schema",
    "viet-lai-truy-van": "queries",
    "ghep-ban-ghi": "linkage",
    "chon-nguon": "sources",
}

CARD_TITLES: dict[str, str] = {
    "luoc-do-trung-gian": "Lược đồ trung gian",
    "viet-lai-truy-van": "Truy vấn viết lại",
    "ghep-ban-ghi": "Ghép bản ghi",
    "chon-nguon": "Chọn nguồn",
}

SCREENS = ("schema", "queries", "linkage", "sources")

# Bảng "cặp bị bỏ qua" của C5 có thể hơn 12.000 dòng (bộ dữ liệu Olist: 12.613). Dựng hết
# thành DOM làm trình duyệt treo hàng phút, nên chỉ hiển thị phần đầu; tệp JSON vẫn giữ đủ.
SKIPPED_ROWS_SHOWN = 200

SCREEN_TITLES: dict[str, str] = {
    "schema": "Lược đồ trung gian",
    "queries": "Truy vấn viết lại",
    "linkage": "Ghép bản ghi",
    "sources": "Chọn nguồn",
}

RELOAD_TOKEN_ID = "reload-token"
OVERVIEW_PANEL_ID = "overview-panel"
OVERVIEW_CARDS_ID = "overview-cards"
SCREEN_BODY_ID = "screen-body"
QUERY_RESULT_ID = "query-result"
SOURCE_TABLE_ID = "source-table"
# Vùng kết quả của lát cắt, khai ở C9 `result_region_ids`; KHÔNG phải một card_id.
RESULT_REGION_ID = "don-theo-thang"

PLACEHOLDER = "—"
PIPELINE_HINT = (
    "Chưa có tệp kết quả ghép. Chạy python -X utf8 -m src.pipeline run --stage all để sinh "
    "data/integration/linkage-customer.json và linkage-seller.json; đóng dashboard trước khi chạy "
    "lại tầng integrate vì cùng một tệp warehouse/olist.duckdb bị khoá."
)

TEXTS: dict[str, str] = {
    "back": "Quay lại tổng quan",
    "reload": "Tải lại",
    "run": "Chạy",
    "retry": "Thử lại",
    "suggest": "Đề xuất nguồn",
    "template_label": "Truy vấn mẫu",
    "sources_query_label": "Truy vấn cần đề xuất",
    "entities": "Số thực thể",
    "fields": "Số trường",
    "ran": "Mẫu đã chạy",
    "mismatched": "Mẫu lệch KPI",
    "matched_pairs": "Cặp vượt ngưỡng",
    "correct_rate": "Tỉ lệ ghép đúng",
    "sources_with_data": "Nguồn có dữ liệu",
    "sources_selected": "Nguồn được chọn",
    "cannot_measure": "Không đo được",
    "no_skip": "Không có cặp bị bỏ qua",
    "threshold": "Ngưỡng",
    "duplicate_groups": "Số nhóm trùng",
    "pairs": "Cặp tiêu biểu",
    "skipped": "Bỏ qua",
    "skipped_truncated": (
        "Hiển thị {shown} trong {total} cặp bị bỏ qua đầu tiên; tệp kết quả vẫn giữ đủ mọi dòng."
    ),
    "median_sql": "Truy vấn trung gian",
    "source_sql": "SQL nguồn (lần chạy gần nhất)",
    "plan": "Kế hoạch viết lại",
    "rows": "Kết quả",
    "kpi_comparison": "Đối chiếu KPI",
    "kpi_definitions": "Định nghĩa KPI dùng chung",
    "old_result": "Kết quả cũ của lần chạy trước",
    "simulated": "nguồn mô phỏng",
    "empty_query": (
        "Chưa chạy truy vấn mẫu nào. Chọn một mẫu rồi bấm Chạy để xem hai bản SQL, "
        "kế hoạch viết lại và kết quả đối chiếu KPI."
    ),
    "empty_schema": "Chưa đọc được lược đồ trung gian. Kiểm tệp khai báo rồi bấm Tải lại.",
    "empty_linkage": "Chưa có tệp kết quả ghép cho đối tượng này.",
    "empty_sources": "Chưa có kết quả đề xuất nguồn. Chọn truy vấn rồi bấm Đề xuất nguồn.",
    "missing_sources": "Không nguồn nào đủ trường cho truy vấn này.",
    "error_schema": "Không đọc được lược đồ trung gian: tệp khai báo thiếu hoặc sai nội dung.",
    "error_sources": "Không đọc được bảng nguồn: tệp cấu hình nguồn thiếu hoặc sai nội dung.",
    "error_linkage": "Tệp kết quả ghép không đọc được hoặc thiếu trường bắt buộc.",
    "error_query": "Không chạy được truy vấn trên dữ liệu nguồn.",
    "error_query_schema": "Dữ liệu nguồn hoặc cấu hình của truy vấn chưa hợp lệ.",
    "error_query_source": "Không nguồn nào đủ trường cho truy vấn này.",
    "error_mismatch": "Kết quả lệch KPI so với nguồn tham chiếu.",
}

COLUMNS = {
    "field": "Trường trung gian",
    "source": "Nguồn",
    "data_type": "Kiểu dữ liệu",
    "step": "Bước",
    "mediated_entity": "Thực thể trung gian",
    "source_table": "Bảng nguồn",
    "join": "Điều kiện join",
    "record_a": "Bản ghi A",
    "record_b": "Bản ghi B",
    "score": "Điểm",
    "decision": "Quyết định",
    "reason": "Lý do",
    "source_name": "Nguồn",
    "has_data": "Có dữ liệu",
    "cost": "Chi phí",
    "latency": "Độ trễ (ms)",
    "selected": "Được chọn",
    "kpi": "KPI",
    "formula": "Công thức",
    "revenue": "Định nghĩa doanh thu",
}

LINKAGE_REQUIRED_KEYS = ("target_entity", "run_id", "computed_at", "threshold", "summary", "pairs", "skipped")
LINKAGE_SUMMARY_KEYS = (
    "pairs_scored",
    "pairs_matched",
    "pairs_review",
    "pairs_skipped",
    "duplicate_groups",
    "correct_rate",
)
CONTRACT_ERRORS = (
    SchemaError,
    ConfigurationError,
    NoSourceAvailableError,
    QueryExecutionError,
    KpiMismatchError,
    LinkageResultMissingError,
    LinkageResultInvalidError,
)

_LAST_RUNS: dict[str, QueryRunResult] = {}
_RUN_ERRORS: dict[str, str] = {}
_CATALOGUE: SourceCatalogue | None = None


@dataclass(frozen=True)
class CardSpec:
    """Một thẻ của màn hình tổng quan: trạng thái, đúng hai dòng số liệu, câu giải thích."""

    card_id: str
    title: str
    state: str
    metrics: tuple[str, str]
    message: str | None = None


def reset_tab_state() -> None:
    """Xoá kết quả và danh mục đã nhớ trong tiến trình (dùng cho test và lần chạy lại)."""

    global _CATALOGUE
    _LAST_RUNS.clear()
    _RUN_ERRORS.clear()
    _CATALOGUE = None


# --- L1: đọc hợp đồng ---------------------------------------------------------


def load_schema_view(config, logger=None) -> MediatedSchemaView:
    """Đọc C6 cho màn hình lược đồ, chỉ đọc tiêu đề CSV nguồn của chính cấu hình này."""

    return load_schema(Path(config.mediated_schema_path), Path(config.raw_csv_dir), logger)


def catalogue(config, logger=None, pending_query_id: str | None = None) -> SourceCatalogue:
    """Đọc C7, dùng lại bản đã nạp khi có, và nhớ nó cho lần đề xuất kế tiếp."""

    global _CATALOGUE
    if _CATALOGUE is None:
        view = load_schema_view(config, logger)
        _CATALOGUE = load_source_catalogue(
            Path(config.integration_sources_path),
            build_field_catalogue(view),
            pending_query_id,
            logger,
        )
    return _CATALOGUE


def linkage_path(config, target_entity: str = DEFAULT_TARGET) -> Path:
    """`data/integration/linkage-<customer|seller>.json` của C5."""

    return Path(config.integration_dir) / f"linkage-{target_entity}.json"


def load_linkage_result(config, target_entity: str = DEFAULT_TARGET) -> dict[str, Any]:
    """Đọc tệp C5; thiếu tệp là trạng thái rỗng, tệp hỏng là lỗi (BR6.11)."""

    path = linkage_path(config, target_entity)
    if not path.exists():
        raise LinkageResultMissingError(f"Chưa có tệp kết quả ghép: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LinkageResultInvalidError(f"Không đọc được tệp kết quả ghép {path.name}.") from exc
    if not isinstance(payload, dict):
        raise LinkageResultInvalidError(f"Tệp kết quả ghép {path.name} không phải một ánh xạ JSON.")
    missing = [key for key in LINKAGE_REQUIRED_KEYS if key not in payload]
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        missing.append("summary")
    else:
        missing += [key for key in LINKAGE_SUMMARY_KEYS if key not in summary]
    if not isinstance(payload.get("pairs"), list) or not isinstance(payload.get("skipped"), list):
        missing.append("pairs/skipped")
    if missing:
        raise LinkageResultInvalidError(
            f"Tệp kết quả ghép {path.name} thiếu trường bắt buộc: {', '.join(sorted(set(missing)))}."
        )
    return payload


# --- L3: trạng thái -----------------------------------------------------------


def StateBlock(
    state: str,
    message: str | None = None,
    items: Any = (),
    *,
    testid: str = "state-block",
) -> html.Div:
    """Năm trạng thái của một màn hình, mỗi trạng thái nêu bằng chữ (BR6.4, BR6.5)."""

    if state not in STATE_TOKENS:
        raise ValueError(f"Trạng thái màn hình không hợp lệ: {state!r}")
    children: list[Any] = [
        html.P(
            [
                html.Span(STATE_ICONS[state], **{"aria-hidden": "true"}),
                html.Span(CARD_TEXTS[f"status_{state}"]),
            ],
            className="integration-status",
        )
    ]
    if message:
        children.append(html.P(message, className="integration-state-message"))
    listed = [str(item) for item in items or ()]
    if listed:
        children.append(html.Ul([html.Li(item) for item in listed], className="integration-state-items"))
    if state == STATE_LOADING:
        children.append(html.Div([html.Div(className="skeleton-line") for _ in range(3)]))
    return html.Div(
        children,
        className="integration-state",
        **{"data-state": state, "data-testid": testid, "role": "status"},
    )


def _panel(
    state: str,
    children: list[Any],
    *,
    testid: str,
    message: str | None = None,
    items: Any = (),
) -> html.Div:
    """Bọc thân một màn hình trong một khối trạng thái, giữ `data-state` ở gốc."""

    return html.Div(
        [StateBlock(state, message, items), *children],
        className="integration-panel",
        **{"data-state": state, "data-testid": testid},
    )


def _table(columns: list[str], rows: list[list[Any]], *, testid: str, caption: str = "") -> Any:
    """Bảng một dòng tiêu đề; mọi ô là chữ, không có HTML từ hợp đồng (ADR-U6-S4)."""

    return dmc.Table(
        [
            dmc.TableThead(dmc.TableTr([dmc.TableTh(column) for column in columns])),
            dmc.TableTbody([dmc.TableTr([dmc.TableTd(str(cell)) for cell in row]) for row in rows]),
        ],
        **{"data-testid": testid, "aria-label": caption or testid},
    )


# --- L2: thành phần -----------------------------------------------------------


def _metric_line(card_id: str, value: str, index: int) -> html.P:
    return html.P(
        value,
        className="integration-metric",
        **{"data-testid": f"card-{card_id}-metric", "data-metric": str(index)},
    )


def IntegrationCard(spec: CardSpec) -> html.Div:
    """Một thẻ tổng quan: tiêu đề, trạng thái, hai dòng số liệu, một điểm vào chi tiết (BR6.2)."""

    metrics = tuple(spec.metrics)
    if len(metrics) != 2:
        raise ValueError(f"Thẻ {spec.card_id!r} phải có đúng hai dòng số liệu, nhận {len(metrics)}.")
    return html.Div(
        [
            html.H3(spec.title, className="integration-card-title"),
            StateBlock(spec.state, spec.message, testid=f"card-{spec.card_id}-state"),
            _metric_line(spec.card_id, metrics[0], 1),
            _metric_line(spec.card_id, metrics[1], 2),
            dmc.Button(
                "Xem chi tiết",
                id=f"card-{spec.card_id}-open",
                n_clicks=0,
                variant="light",
                size="xs",
                **{"data-testid": f"card-{spec.card_id}-open", "aria-label": f"Xem chi tiết {spec.title}"},
            ),
        ],
        className="integration-card",
        **{"data-state": spec.state, "data-testid": "integration-card", "data-card": spec.card_id},
    )


def OverviewScreen(specs: list[CardSpec]) -> html.Div:
    """Lưới bốn thẻ của màn hình tổng quan, mỗi thẻ một điểm vào chi tiết."""

    return html.Div(
        dmc.SimpleGrid([IntegrationCard(spec) for spec in specs], cols=4, className="integration-grid"),
        id=OVERVIEW_CARDS_ID,
        className="integration-overview-cards",
        **{"data-testid": OVERVIEW_CARDS_ID},
    )


def DetailScreen(screen: str, body: Any) -> html.Div:
    """Khung một màn hình chi tiết: tiêu đề, quay lại tổng quan, tải lại, rồi thân màn hình."""

    return html.Div(
        [
            html.Header(
                [
                    html.H2(SCREEN_TITLES[screen]),
                    html.Div(
                        [
                            dmc.Button(
                                TEXTS["back"],
                                id={"type": "back", "screen": screen},
                                n_clicks=0,
                                variant="subtle",
                                size="xs",
                                **{"data-testid": "back-to-overview"},
                            ),
                            dmc.Button(
                                TEXTS["reload"],
                                id={"type": "reload", "screen": screen},
                                n_clicks=0,
                                variant="subtle",
                                size="xs",
                                **{"data-testid": "reload-screen"},
                            ),
                        ],
                        className="integration-screen-actions",
                    ),
                ],
                className="integration-screen-header",
            ),
            html.Div(body, className="integration-screen-panel"),
        ],
        id=f"screen-{screen}",
        className="integration-screen-body",
        **{"data-screen": screen, "data-testid": "detail-screen"},
    )


def SchemaPanel(view: MediatedSchemaView) -> html.Div:
    """Danh sách thực thể, bảng ánh xạ ba cột của từng thực thể, nhãn GAV (BR6.10)."""

    state, message, items = STATE_FULL, None, []
    if not view.entities:
        state, message = STATE_EMPTY, TEXTS["empty_schema"]
    elif view.partial is not None:
        state, message = STATE_PARTIAL, view.partial.reason
        items = list(view.partial.missing)
    tabs = [
        dcc.Tab(
            label=entity.name,
            value=entity.name,
            children=[
                html.P(entity.description, className="integration-entity-description"),
                _table(
                    [COLUMNS["field"], COLUMNS["source"], COLUMNS["data_type"]],
                    [
                        [
                            mapping.field_name,
                            f"{mapping.source_table}.{mapping.source_column}",
                            mapping.data_type,
                        ]
                        for mapping in view.mappings.get(entity.name, ())
                    ],
                    testid=f"schema-mapping-{entity.name}",
                    caption=f"Ánh xạ {entity.name}",
                ),
            ],
        )
        for entity in view.entities
    ]
    return _panel(
        state,
        [
            html.P(
                view.schema_kind,
                className="integration-schema-kind",
                **{"data-testid": "schema-kind", "aria-label": "Kiểu lược đồ"},
            ),
            dcc.Tabs(
                id="schema-entity",
                value=view.entities[0].name if view.entities else "",
                children=tabs,
                className="integration-tabs",
            ),
        ],
        testid="schema-panel",
        message=message,
        items=items,
    )


def _sql_block(title: str, text: str, testid: str) -> html.Section:
    return html.Section(
        [
            html.H4(title),
            dmc.Code(text, block=True, className="integration-sql", **{"data-testid": testid}),
        ],
        className="integration-sql-block",
    )


def _kpi_definitions(definitions: list[KpiDefinition]) -> html.Section:
    return html.Section(
        [
            html.H4(TEXTS["kpi_definitions"]),
            _table(
                [COLUMNS["kpi"], COLUMNS["formula"], COLUMNS["revenue"]],
                [[item.title, item.formula, item.revenue_definition] for item in definitions],
                testid="kpi-definitions",
                caption=TEXTS["kpi_definitions"],
            ),
        ],
        className="integration-kpi-definitions",
    )


def _result_block(result: QueryRunResult, *, stale: bool) -> list[Any]:
    """Bốn phần của một kết quả C4: hai bản SQL, kế hoạch, bảng kết quả, định nghĩa KPI."""

    state = STATE_PARTIAL if result.partial else STATE_FULL
    head: list[Any] = [
        StateBlock(state, items=result.partial, testid="query-state"),
        html.H4(f"{TEXTS['rows']}: {format_number(result.row_count)} dòng · {result.elapsed_ms} ms"),
    ]
    if stale:
        head.append(
            html.P(TEXTS["old_result"], className="integration-stale", **{"data-testid": "stale-result"})
        )
    compared = len(result.kpi_comparison)
    return [
        *head,
        _sql_block(TEXTS["median_sql"], result.mediated_query_text, "mediated-sql"),
        _sql_block(TEXTS["source_sql"], result.source_sql, "source-sql"),
        html.Section(
            [
                html.H4(TEXTS["plan"]),
                _table(
                    [COLUMNS["step"], COLUMNS["mediated_entity"], COLUMNS["source_table"], COLUMNS["join"]],
                    [
                        [step.step, step.mediated_entity, step.source_table, step.join_condition]
                        for step in result.rewrite_plan
                    ],
                    testid="rewrite-plan",
                    caption=TEXTS["plan"],
                ),
            ],
            className="integration-plan",
        ),
        html.Section(
            [
                _table(
                    list(result.rows[0]) if result.rows else [COLUMNS["rows"]],
                    [list(row.values()) for row in result.rows],
                    testid="query-rows",
                    caption=TEXTS["rows"],
                ),
            ],
            className="integration-rows",
        ),
        html.P(
            f"{TEXTS['kpi_comparison']}: khớp {format_number(compared)} nhóm",
            **{"data-testid": "kpi-comparison"},
        ),
        _kpi_definitions(result.kpi_definitions),
    ]


def _result_area_state(result: QueryRunResult | None, message: str | None) -> str:
    if message is not None:
        return STATE_ERROR
    if result is None:
        return STATE_EMPTY
    return STATE_PARTIAL if result.partial else STATE_FULL


def result_area(template_id: str, result: QueryRunResult | None, message: str | None = None) -> html.Div:
    """Vùng kết quả của màn hình truy vấn; callback `run_query` thay đúng các con của nó."""

    state = _result_area_state(result, message)
    if message is not None:
        children: list[Any] = [StateBlock(STATE_ERROR, message, testid="query-state")]
        if result is not None:
            children.extend(_result_block(result, stale=True))
    elif result is None:
        children = [StateBlock(STATE_EMPTY, TEXTS["empty_query"], testid="query-state")]
    else:
        children = _result_block(result, stale=False)
    return html.Div(
        children,
        id=QUERY_RESULT_ID,
        className="integration-result",
        **{"data-state": state, "data-testid": QUERY_RESULT_ID, "data-template": template_id},
    )


def QueryPanel(
    template_id: str,
    result: QueryRunResult | None,
    message: str | None = None,
) -> html.Div:
    """Màn hình truy vấn: chọn mẫu, nút Chạy/Thử lại, vùng kết quả (BR6.6, BR6.7, BR6.12)."""

    options = [{"label": kpi(item).title, "value": item} for item in TEMPLATE_IDS]
    area = result_area(template_id, result, message)
    return html.Div(
        [
            dmc.Group(
                [
                    dmc.Select(
                        id="query-template",
                        data=options,
                        value=template_id,
                        allowDeselect=False,
                        label=TEXTS["template_label"],
                        w=260,
                        **{"data-testid": "query-template"},
                    ),
                    dmc.Button(
                        TEXTS["run"],
                        id="run-query",
                        n_clicks=0,
                        **{"data-testid": "run-query"},
                    ),
                    dmc.Button(
                        TEXTS["retry"],
                        id="retry-query",
                        n_clicks=0,
                        variant="light",
                        **{"data-testid": "retry-query"},
                    ),
                ],
                className="integration-controls",
            ),
            dcc.Loading(area, type="default", color="#2F7D6A"),
        ],
        className="integration-query-panel",
        **{"data-state": _result_area_state(result, message), "data-testid": "query-panel"},
    )


def _linkage_summary(payload: dict[str, Any]) -> tuple[str, str]:
    """Hai dòng số liệu của thẻ ghép bản ghi: số cặp vượt ngưỡng, tỉ lệ ghép đúng."""

    summary = payload["summary"]
    matched = int(summary.get("pairs_matched") or 0)
    rate = summary.get("correct_rate")
    first = f"{TEXTS['matched_pairs']}: {format_number(matched)}"
    if rate is None:
        return first, f"{TEXTS['correct_rate']}: {TEXTS['cannot_measure']}"
    sample = summary.get("correct_rate_sample")
    share = format_percent(float(rate) * 100)
    detail = f"{share} ({format_number(sample)}/{format_number(matched)})" if sample is not None else share
    return first, f"{TEXTS['correct_rate']}: {detail}"


def _duplicate_groups(payload: dict[str, Any]) -> str:
    value = payload["summary"].get("duplicate_groups")
    return TEXTS["cannot_measure"] if value is None else format_number(int(value))


def _linkage_body(payload: dict[str, Any] | None) -> Any:
    """Thân một đối tượng của màn hình ghép bản ghi; thiếu tệp là trạng thái rỗng."""

    if payload is None:
        return StateBlock(STATE_EMPTY, f"{TEXTS['empty_linkage']} {PIPELINE_HINT}", testid="linkage-state")
    matched, rate = _linkage_summary(payload)
    items = [
        f"{TEXTS['threshold']}: {format_number(float(payload['threshold']), 2)}",
        matched,
        rate,
        f"{TEXTS['duplicate_groups']}: {_duplicate_groups(payload)}",
    ]
    if payload["summary"].get("correct_rate") is None:
        reason = payload["summary"].get("correct_rate_reason") or TEXTS["cannot_measure"]
        items.append(f"{TEXTS['correct_rate']}: {TEXTS['cannot_measure']} — {reason}")
    pairs = [
        [pair["record_a"], pair["record_b"], format_number(float(pair["score"]), 2), pair["decision"]]
        for pair in payload["pairs"]
    ]
    skipped = [[item["record_a"], item["record_b"], item["reason"]] for item in payload["skipped"]]
    skipped_block: Any
    if skipped:
        shown = skipped[:SKIPPED_ROWS_SHOWN]
        body: list[Any] = [html.H4(TEXTS["skipped"])]
        if len(skipped) > len(shown):
            body.append(
                html.P(
                    TEXTS["skipped_truncated"].format(
                        shown=format_number(len(shown)), total=format_number(len(skipped))
                    ),
                    **{"data-testid": "linkage-skipped-note"},
                )
            )
        body.append(
            _table(
                [COLUMNS["record_a"], COLUMNS["record_b"], COLUMNS["reason"]],
                shown,
                testid="linkage-skipped",
                caption=TEXTS["skipped"],
            )
        )
        skipped_block = html.Section(body, className="integration-skipped")
    else:
        skipped_block = html.Section(
            [html.H4(TEXTS["skipped"]), html.P(TEXTS["no_skip"], **{"data-testid": "linkage-skipped"})],
            className="integration-skipped",
        )
    return html.Div(
        [
            html.Ul([html.Li(item) for item in items], className="integration-figures"),
            html.H4(TEXTS["pairs"]),
            _table(
                [COLUMNS["record_a"], COLUMNS["record_b"], COLUMNS["score"], COLUMNS["decision"]],
                pairs,
                testid="linkage-pairs",
                caption=TEXTS["pairs"],
            ),
            skipped_block,
        ],
        className="integration-linkage-body",
    )


def LinkagePanel(payload: dict[str, Any], other: dict[str, Any] | None = None) -> html.Div:
    """Màn hình ghép bản ghi: hai tab khách hàng/người bán, đổi bằng bàn phím (BR6.11)."""

    by_target: dict[str, dict[str, Any]] = {}
    for item in (payload, other):
        if item is not None:
            by_target[str(item["target_entity"])] = item
    present = [target for target in TARGETS if target in by_target]
    state = STATE_EMPTY if not present else STATE_PARTIAL if len(present) == 1 else STATE_FULL
    tabs = [
        dcc.Tab(label=TARGET_TITLES[target], value=target, children=_linkage_body(by_target.get(target)))
        for target in TARGETS
    ]
    return _panel(
        state,
        [
            dcc.Tabs(
                id="linkage-target",
                value=present[0] if present else DEFAULT_TARGET,
                children=tabs,
                className="integration-tabs",
            )
        ],
        testid="linkage-panel",
        message=None if present else PIPELINE_HINT,
    )


def _source_rows(catalogue: SourceCatalogue, query_id: str | None) -> tuple[list[list[str]], list[str]]:
    """Sáu dữ kiện của mỗi nguồn, kèm ghi chú nguồn mô phỏng (BR6.8)."""

    chosen = {
        choice.source_name: choice.is_selected for choice in catalogue.choices if choice.query_id == query_id
    }
    reasons = {
        choice.source_name: choice.reason
        for choice in catalogue.choices
        if choice.query_id == query_id and not choice.is_selected
    }
    rows: list[list[str]] = []
    for profile in catalogue.sources:
        label = profile.label
        if profile.is_simulated and TEXTS["simulated"].lower() not in label.lower():
            label = f"{label} ({TEXTS['simulated']})"
        selected = "Có" if chosen.get(profile.source_name) else "Không"
        rows.append(
            [
                label,
                "Có" if profile.has_data else "Không",
                format_number(profile.cost_level),
                format_number(profile.latency_ms),
                selected if chosen else PLACEHOLDER,
                reasons.get(profile.source_name, ""),
            ]
        )
    notes: list[str] = []
    if query_id is None or not chosen:
        notes.append(TEXTS["empty_sources"])
    elif not any(chosen.values()):
        notes.append(TEXTS["missing_sources"])
    return rows, notes


SOURCE_COLUMNS = [
    COLUMNS["source_name"],
    COLUMNS["has_data"],
    COLUMNS["cost"],
    COLUMNS["latency"],
    COLUMNS["selected"],
    COLUMNS["reason"],
]


def _source_table(
    catalogue: SourceCatalogue,
    query_id: str | None,
    note: str | None = None,
    items: Any = (),
) -> html.Div:
    """Phần bảng nguồn của một truy vấn, để callback `suggest_source` thay đúng vùng đó."""

    rows, notes = _source_rows(catalogue, query_id)
    listed = [str(item) for item in items or ()]
    children: list[Any] = [
        _table(SOURCE_COLUMNS, rows, testid="source-rows", caption="Bảng nguồn"),
        html.Ul([html.Li(text) for text in notes], className="integration-notes"),
    ]
    if note:
        children.append(html.P(note, **{"data-testid": "source-note"}))
    if listed:
        children.append(html.Ul([html.Li(item) for item in listed], **{"data-testid": "source-missing-fields"}))
    return html.Div(children, className="integration-source-table")


def source_state(catalogue: SourceCatalogue, message: str | None = None) -> tuple[str, str | None, list[str]]:
    """Trạng thái, lý do và dòng bối cảnh của màn hình chọn nguồn (BR6.4)."""

    query_id = catalogue.pending_query_id
    label = [f"{TEXTS['sources_query_label']}: {query_id}"] if query_id else []
    if message is not None:
        return STATE_PARTIAL, message, label
    if catalogue.partial_reason:
        return STATE_PARTIAL, catalogue.partial_reason, label
    return STATE_FULL, None, []


def source_region(
    catalogue: SourceCatalogue,
    query_id: str | None,
    message: str | None = None,
    items: Any = (),
) -> html.Div:
    """Vùng thay được của màn hình chọn nguồn: khối trạng thái + bảng nguồn.

    Cả hai nằm trong một `Output` để bấm "Đề xuất nguồn" xong thì huy hiệu trạng thái
    không còn nói "chưa có kết quả đề xuất" (lỗi thấy trên trình duyệt 2026-11-09).
    """

    state, note, listed = source_state(catalogue, message)
    return html.Div(
        [StateBlock(state, note, listed), _source_table(catalogue, query_id, message, items)],
        id=SOURCE_TABLE_ID,
        **{"data-state": state, "data-testid": SOURCE_TABLE_ID},
    )


def SourcePanel(catalogue: SourceCatalogue, message: str | None = None, items: Any = ()) -> html.Div:
    """Màn hình chọn nguồn: chọn truy vấn, đề xuất nguồn, bảng nguồn (BR6.8, W4)."""

    query_id = catalogue.pending_query_id
    state, _, _ = source_state(catalogue, message)
    options = [{"label": item, "value": item} for item in catalogue.query_fields]
    return html.Div(
        [
            dmc.Group(
                [
                    dmc.Select(
                        id="source-query",
                        data=options,
                        value=query_id or (options[0]["value"] if options else None),
                        allowDeselect=False,
                        label=TEXTS["sources_query_label"],
                        w=280,
                        **{"data-testid": "source-query"},
                    ),
                    dmc.Button(
                        TEXTS["suggest"],
                        id="suggest-source",
                        n_clicks=0,
                        **{"data-testid": "suggest-source"},
                    ),
                ],
                className="integration-controls",
            ),
            source_region(catalogue, query_id, message, items),
        ],
        className="integration-panel",
        **{"data-state": state, "data-testid": "source-panel"},
    )


# --- Thẻ tổng quan ------------------------------------------------------------


def _empty_spec(card_id: str) -> CardSpec:
    return CardSpec(card_id, CARD_TITLES[card_id], STATE_EMPTY, (PLACEHOLDER, PLACEHOLDER))


def schema_card(config, card_id: str = "luoc-do-trung-gian", logger=None) -> CardSpec:
    """Thẻ 1: số thực thể và số trường của lược đồ trung gian (C6)."""

    try:
        view = load_schema_view(config, logger)
    except CONTRACT_ERRORS:
        return CardSpec(
            card_id, CARD_TITLES[card_id], STATE_ERROR, (PLACEHOLDER, PLACEHOLDER), TEXTS["error_schema"]
        )
    if not view.entities:
        return CardSpec(
            card_id, CARD_TITLES[card_id], STATE_EMPTY, (PLACEHOLDER, PLACEHOLDER), TEXTS["empty_schema"]
        )
    fields = sum(len(entity.fields) for entity in view.entities)
    state = STATE_PARTIAL if view.partial is not None else STATE_FULL
    return CardSpec(
        card_id,
        CARD_TITLES[card_id],
        state,
        (
            f"{TEXTS['entities']}: {format_number(len(view.entities))}",
            f"{TEXTS['fields']}: {format_number(fields)}",
        ),
        view.partial.reason if view.partial is not None else None,
    )


def queries_card(card_id: str = "viet-lai-truy-van") -> CardSpec:
    """Thẻ 2: số mẫu đã chạy và số mẫu lệch KPI (những lần chạy trong tiến trình này)."""

    ran = len(_LAST_RUNS) + len(_RUN_ERRORS)
    if ran == 0:
        return CardSpec(
            card_id, CARD_TITLES[card_id], STATE_EMPTY, (PLACEHOLDER, PLACEHOLDER), TEXTS["empty_query"]
        )
    mismatched = len(_RUN_ERRORS)
    return CardSpec(
        card_id,
        CARD_TITLES[card_id],
        STATE_ERROR if mismatched else STATE_FULL,
        (f"{TEXTS['ran']}: {format_number(ran)}", f"{TEXTS['mismatched']}: {format_number(mismatched)}"),
        "; ".join(sorted(_RUN_ERRORS.values())) or None,
    )


def linkage_card(config, card_id: str = "ghep-ban-ghi", logger=None) -> CardSpec:
    """Thẻ 3: số cặp vượt ngưỡng và tỉ lệ ghép đúng của đối tượng khách hàng (C5)."""

    try:
        payload = load_linkage_result(config, DEFAULT_TARGET)
    except LinkageResultMissingError:
        return CardSpec(card_id, CARD_TITLES[card_id], STATE_EMPTY, (PLACEHOLDER, PLACEHOLDER), PIPELINE_HINT)
    except LinkageResultInvalidError:
        return CardSpec(
            card_id, CARD_TITLES[card_id], STATE_ERROR, (PLACEHOLDER, PLACEHOLDER), TEXTS["error_linkage"]
        )
    matched, rate = _linkage_summary(payload)
    return CardSpec(card_id, CARD_TITLES[card_id], STATE_FULL, (matched, rate))


def sources_card(config, card_id: str = "chon-nguon", logger=None) -> CardSpec:
    """Thẻ 4: số nguồn có dữ liệu và số nguồn được chọn của truy vấn đang chờ (C7)."""

    try:
        loaded = catalogue(config, logger)
    except CONTRACT_ERRORS:
        return CardSpec(
            card_id, CARD_TITLES[card_id], STATE_ERROR, (PLACEHOLDER, PLACEHOLDER), TEXTS["error_sources"]
        )
    with_data = sum(1 for profile in loaded.sources if profile.has_data)
    selected = sum(1 for choice in loaded.choices if choice.is_selected)
    metrics = (
        f"{TEXTS['sources_with_data']}: {format_number(with_data)}",
        f"{TEXTS['sources_selected']}: {format_number(selected) if loaded.choices else PLACEHOLDER}",
    )
    if loaded.partial_reason:
        pending = f" ({loaded.pending_query_id})" if loaded.pending_query_id else ""
        return CardSpec(
            card_id,
            CARD_TITLES[card_id],
            STATE_PARTIAL,
            metrics,
            f"{loaded.partial_reason}{pending}",
        )
    return CardSpec(card_id, CARD_TITLES[card_id], STATE_FULL, metrics)


def card_specs(config, tab_config: TabConfig, logger=None) -> list[CardSpec]:
    """Bốn thẻ theo `card_ids` của C9; lỗi của một hợp đồng chỉ hỏng thẻ của nó."""

    specs: list[CardSpec] = []
    for card_id in _checked_cards(tab_config):
        screen = CARD_SCREENS[card_id]
        try:
            if screen == "schema":
                specs.append(schema_card(config, card_id, logger))
            elif screen == "queries":
                specs.append(queries_card(card_id))
            elif screen == "linkage":
                specs.append(linkage_card(config, card_id, logger))
            else:
                specs.append(sources_card(config, card_id, logger))
        except PipelineError:
            specs.append(CardSpec(card_id, CARD_TITLES[card_id], STATE_ERROR, (PLACEHOLDER, PLACEHOLDER)))
    return specs


# --- Khung tab ----------------------------------------------------------------


def _region_component(region_id: str, action_id: str):
    """Dựng một vùng kết quả theo id C9; id lạ là lỗi cấu hình, không im lặng bỏ qua."""

    builders = {RESULT_REGION_ID: _thin_slice_region}
    builder = builders.get(region_id)
    if builder is None:
        raise ConfigurationError(
            f"Vùng kết quả {region_id!r} có trong 'result_region_ids' nhưng chưa có hàm dựng. "
            "Thêm hàm dựng cùng thay đổi khai vùng, hoặc gỡ id khỏi cấu hình."
        )
    return builder(action_id)


def _thin_slice_region(action_id: str):
    return build_integration_card(state=STATE_PENDING, action_id=action_id, show_action=True)


def _checked_cards(tab_config: TabConfig) -> tuple[str, ...]:
    """Đúng bốn thẻ đã chốt trong C9; thiếu hay thừa là lỗi cấu hình."""

    cards = tuple(tab_config.card_ids)
    missing = tuple(card_id for card_id in CARD_SCREENS if card_id not in cards)
    extra = tuple(card_id for card_id in cards if card_id not in CARD_SCREENS)
    if missing or extra:
        parts = []
        if missing:
            parts.append("thiếu: " + ", ".join(missing))
        if extra:
            parts.append("thừa: " + ", ".join(extra))
        raise ConfigurationError("Tab 'Tích hợp' phải có đúng bốn thẻ (" + "; ".join(parts) + ").")
    return cards


def IntegrationTab(tab_config: TabConfig) -> list:
    """Khung tab: bốn thẻ rỗng, một vùng thân màn hình, một ô nhớ yêu cầu tải lại.

    Không đọc hợp đồng nào ở đây: C5/C6/C7 chỉ được đọc trong callback (ADR-U6-S1).
    """

    cards = [_empty_spec(card_id) for card_id in _checked_cards(tab_config)]
    regions = [
        html.Div(
            _region_component(region_id, tab_config.callback_ids[0]),
            id=region_id,
            className="integration-region",
            **{"data-testid": region_id},
        )
        for region_id in tab_config.result_region_ids
    ]
    return [
        # DMC cần provider bao ngoài thì các thành phần mới có theme và style (ADR-U6-S4).
        dmc.MantineProvider(
            [
                dcc.Store(id=RELOAD_TOKEN_ID, data={"screen": "", "seq": 0}),
                *regions,
                html.Div(
                    OverviewScreen(cards),
                    id=OVERVIEW_PANEL_ID,
                    className="integration-overview",
                    **{"data-testid": OVERVIEW_PANEL_ID},
                ),
                html.Div(
                    id=SCREEN_BODY_ID,
                    className="integration-screen",
                    **{"data-testid": SCREEN_BODY_ID},
                ),
            ]
        )
    ]


def build_integration_tab(tab_config: TabConfig) -> list:
    """Tên cũ của `IntegrationTab`, giữ cho chỗ nối trong `src/dashboard/app.py`."""

    return IntegrationTab(tab_config)


# --- L1/L2 theo màn hình ------------------------------------------------------


def screen_body(config, screen: str, logger=None) -> Any:
    """Thân một màn hình chi tiết, đọc đúng hợp đồng của màn hình đó trong callback."""

    try:
        if screen == "schema":
            return SchemaPanel(load_schema_view(config, logger))
        if screen == "queries":
            template_id = next(iter(_LAST_RUNS), TEMPLATE_IDS[0])
            return QueryPanel(template_id, _LAST_RUNS.get(template_id), _RUN_ERRORS.get(template_id))
        if screen == "linkage":
            return _linkage_panel(config)
        return SourcePanel(catalogue(config, logger))
    except CONTRACT_ERRORS:
        return _screen_error(screen)


def _screen_error(screen: str) -> html.Div:
    """Câu tiếng Việt theo màn hình; không chép thông điệp nội bộ của ngoại lệ (BR6.5)."""

    text = {
        "schema": TEXTS["error_schema"],
        "queries": TEXTS["error_query_schema"],
        "linkage": TEXTS["error_linkage"],
        "sources": TEXTS["error_sources"],
    }[screen]
    return StateBlock(STATE_ERROR, text, testid=f"{screen}-state")


def _linkage_panel(config) -> html.Div:
    """Đọc cả hai tệp C5; thiếu tệp là trạng thái rỗng, không phải lỗi."""

    loaded: list[dict[str, Any]] = []
    first_error: BaseException | None = None
    for target in TARGETS:
        try:
            loaded.append(load_linkage_result(config, target))
        except LinkageResultMissingError:
            continue
        except LinkageResultInvalidError as exc:
            first_error = first_error or exc
    if first_error is not None and not loaded:
        raise first_error
    if not loaded:
        return _panel(
            STATE_EMPTY,
            [
                dcc.Tabs(
                    id="linkage-target",
                    value=DEFAULT_TARGET,
                    children=[
                        dcc.Tab(label=TARGET_TITLES[target], value=target, children=_linkage_body(None))
                        for target in TARGETS
                    ],
                )
            ],
            testid="linkage-panel",
            message=PIPELINE_HINT,
        )
    return LinkagePanel(loaded[0], loaded[1] if len(loaded) > 1 else None)


# --- L4/L5: chạy truy vấn và đề xuất nguồn ------------------------------------


def _query_error_text(exc: BaseException) -> str:
    if isinstance(exc, KpiMismatchError):
        return TEXTS["error_mismatch"]
    if isinstance(exc, NoSourceAvailableError):
        return TEXTS["error_query_source"]
    if isinstance(exc, QueryExecutionError):
        return TEXTS["error_query"]
    if isinstance(exc, (SchemaError, ConfigurationError)):
        return TEXTS["error_query_schema"]
    return TEXTS["error_query"]


def run_query_body(config, template_id: str, logger=None) -> html.Div:
    """Chạy một mẫu qua U5 (C3) rồi U3 (C4), giữ kết quả cho thẻ tổng quan (W3)."""

    logger = logger or NullLogger()
    title = kpi(template_id).title
    try:
        loaded = catalogue(config, logger, pending_query_id=template_id)
        selection = select_source(loaded, template_id, logger)
        result = run_template(template_id, params=None, selection=selection, logger=logger)
    except CONTRACT_ERRORS as exc:
        _RUN_ERRORS[template_id] = f"{title}: {_query_error_text(exc)}"
        previous = _LAST_RUNS.get(template_id)
        return result_area(template_id, previous, f"Truy vấn '{title}' lỗi khi chạy. {_query_error_text(exc)}")
    _RUN_ERRORS.pop(template_id, None)
    _LAST_RUNS[template_id] = result
    return result_area(template_id, result)


def suggest_source_body(config, query_id: str, logger=None) -> html.Div:
    """Đề xuất nguồn cho một truy vấn qua U5, rồi vẽ lại vùng nguồn (W4)."""

    global _CATALOGUE
    logger = logger or NullLogger()
    try:
        loaded = catalogue(config, logger, pending_query_id=query_id)
        selection = select_source(loaded, query_id, logger)
    except NoSourceAvailableError as exc:
        _CATALOGUE = exc.catalogue
        return source_region(exc.catalogue, query_id, TEXTS["missing_sources"], items=exc.missing_fields)
    except CONTRACT_ERRORS as exc:
        return html.Div(StateBlock(STATE_ERROR, _query_error_text(exc), testid=SOURCE_TABLE_ID))
    _CATALOGUE = selection.catalogue
    return source_region(selection.catalogue, query_id)


def source_table_body(config, query_id: str, logger=None) -> html.Div:
    """Vẽ lại vùng nguồn của một truy vấn đã có quyết định, không gọi lại U5 (W4)."""

    loaded = catalogue(config, logger, pending_query_id=query_id)
    return source_region(loaded, query_id)


# --- Năm callback -------------------------------------------------------------


def query_triggered(triggered_id: str | None) -> bool:
    """Chỉ nút Chạy/Thử lại mới chạy truy vấn; đổi mẫu trong ô chọn thì không (W3 bước 1)."""

    return triggered_id in {"run-query", "retry-query"}


def suggest_triggered(triggered_id: str | None) -> bool:
    """Chỉ nút "Đề xuất nguồn" mới gọi U5; đổi truy vấn chỉ vẽ lại bảng đã có (W4 bước 1)."""

    return triggered_id == "suggest-source"


def clicked_value(triggered: Any) -> Any:
    """Giá trị của input vừa đổi; Dash phát `0` khi một thành phần khớp mẫu vừa được tạo."""

    return triggered[0]["value"] if triggered else None


def region_state(node: Any) -> Any:
    """`data-state` của một vùng, để callback cập nhật cả thuộc tính chứ không chỉ phần thân."""

    props = getattr(node, "to_plotly_json", lambda: {})().get("props", {})
    return props.get("data-state")


def fill_overview(config, tab_value: str | None, tab_config: TabConfig, logger=None) -> Any:
    """`load_overview`: điền bốn thẻ khi tab vừa được chọn; không chạy truy vấn nào (W1)."""

    if tab_value != tab_config.tab_id:
        return no_update
    return [IntegrationCard(spec) for spec in card_specs(config, tab_config, logger)]


def route_screen(
    config,
    triggered_id: Any,
    reload_token: Any = None,
    logger=None,
    clicked: Any = None,
) -> Any:
    """`route`: trả về (ẩn tổng quan, thân màn hình) cho màn hình vừa được chọn (W2).

    Nút "Quay lại" nằm trong màn hình chi tiết nên chỉ tồn tại sau khi màn hình được dựng;
    vì vậy callback nhận chúng bằng pattern-matching id (`{"type": "back", ...}`) chứ không
    bằng id cố định — id cố định khiến Dash báo "nonexistent object" và callback không chạy.

    `clicked` là giá trị `n_clicks` của input vừa đổi. Dash gọi lại callback ngay khi một
    thành phần khớp mẫu được tạo (với `n_clicks = 0`), nên phải bỏ qua những lần gọi đó —
    nếu không, mở tab "Tích hợp" là thẻ đầu tiên tự bật màn hình chi tiết.
    """

    if triggered_id is None:
        return no_update
    if triggered_id == RELOAD_TOKEN_ID:
        token = reload_token if isinstance(reload_token, dict) else {}
        screen = token.get("screen")
        if screen not in SCREENS:
            return (False, None)
        return (True, DetailScreen(screen, screen_body(config, screen, logger)))
    if not clicked:
        return no_update
    if isinstance(triggered_id, str) and triggered_id.startswith("back-"):
        return (False, None)
    if isinstance(triggered_id, dict):
        if triggered_id.get("type") == "back":
            return (False, None)
        return no_update
    if isinstance(triggered_id, str) and triggered_id.startswith("card-") and triggered_id.endswith("-open"):
        card_id = triggered_id[len("card-") : -len("-open")]
        screen = CARD_SCREENS.get(card_id)
        if screen is None:
            return no_update
        return (True, DetailScreen(screen, screen_body(config, screen, logger)))
    return no_update


def reload_token(triggered_id: Any, current: Any = None, clicked: Any = None) -> Any:
    """`reload`: ghi màn hình cần đọc lại kèm số thứ tự, để lần bấm sau vẫn đổi giá trị.

    `clicked` lọc lần gọi mà Dash phát ra lúc thành phần vừa được tạo với `n_clicks = 0`.
    """

    if not clicked:
        return no_update
    if isinstance(triggered_id, dict):
        screen = triggered_id.get("screen") if triggered_id.get("type") == "reload" else None
    elif isinstance(triggered_id, str) and triggered_id.startswith("reload-"):
        screen = triggered_id[len("reload-") :]
    else:
        return no_update
    if screen not in SCREENS:
        return no_update
    # "Tải lại" phải đọc lại hợp đồng: xoá danh mục đã nhớ để C7 được nạp mới (W2 bước 2).
    global _CATALOGUE
    _CATALOGUE = None
    previous = current.get("seq") if isinstance(current, dict) else None
    return {"screen": screen, "seq": int(previous or 0) + 1}


def _region_callback(renderer, config, logger_factory):
    """Trả một hàm callback Dash cho một vùng kết quả (mỗi vùng một Output riêng)."""

    def callback(_clicks):  # noqa: ANN001 - chữ ký do Dash quyết định
        return renderer(config, logger_factory())

    return callback


def register_callbacks(app: Dash, config, tab_config: TabConfig, logger_factory=None) -> None:
    """Đăng ký sáu callback của tab, mỗi callback một Output riêng (ADR-U6-S5).

    Sáu gồm năm của U6 và một của vùng kết quả `don-theo-thang` (C9 `result_region_ids`);
    cộng hai callback của ba tab báo cáo thì dashboard có tám callback.
    """

    def logger():
        return NullLogger() if logger_factory is None else logger_factory(config)

    renderers = {RESULT_REGION_ID: render_integration_card}
    for region_id in tab_config.result_region_ids:
        renderer = renderers.get(region_id)
        if renderer is None:
            raise ConfigurationError(
                f"Vùng kết quả {region_id!r} chưa có callback dựng nội dung; khai vùng phải đi cùng hàm dựng."
            )
        app.callback(
            Output(region_id, "children"),
            Input(tab_config.callback_ids[0], "n_clicks"),
            prevent_initial_call=True,
        )(_region_callback(renderer, config, logger))

    @app.callback(Output(OVERVIEW_CARDS_ID, "children"), Input("tabs", "value"))
    def load_overview(tab_value):  # noqa: ANN001 - chữ ký do Dash quyết định
        return fill_overview(config, tab_value, tab_config, logger())

    @app.callback(
        Output(OVERVIEW_PANEL_ID, "hidden"),
        Output(SCREEN_BODY_ID, "children"),
        Input(RELOAD_TOKEN_ID, "data"),
        *[Input(f"card-{card_id}-open", "n_clicks") for card_id in tab_config.card_ids],
        Input({"type": "back", "screen": ALL}, "n_clicks"),
    )
    def route(reload_value, *_clicks):  # noqa: ANN001 - chữ ký do Dash quyết định
        return route_screen(
            config,
            ctx.triggered_id,
            reload_value,
            logger(),
            clicked_value(ctx.triggered),
        )

    @app.callback(
        Output(QUERY_RESULT_ID, "children"),
        Input("run-query", "n_clicks"),
        Input("retry-query", "n_clicks"),
        Input("query-template", "value"),
    )
    def run_query(_run_clicks, _retry_clicks, template_id):  # noqa: ANN001 - chữ ký do Dash quyết định
        if not query_triggered(ctx.triggered_id) or not template_id:
            return no_update
        return run_query_body(config, template_id, logger()).children

    @app.callback(
        Output(SOURCE_TABLE_ID, "children"),
        Output(SOURCE_TABLE_ID, "data-state"),
        Input("suggest-source", "n_clicks"),
        Input("source-query", "value"),
    )
    def suggest_source(_clicks, query_id):  # noqa: ANN001 - chữ ký do Dash quyết định
        if ctx.triggered_id is None or not query_id:
            return no_update, no_update
        if not suggest_triggered(ctx.triggered_id):
            node = source_table_body(config, query_id, logger())
        else:
            node = suggest_source_body(config, query_id, logger())
        return node, region_state(node)

    @app.callback(
        Output(RELOAD_TOKEN_ID, "data"),
        Input({"type": "reload", "screen": ALL}, "n_clicks"),
        State(RELOAD_TOKEN_ID, "data"),
    )
    def reload(*values):  # noqa: ANN001 - chữ ký do Dash quyết định
        return reload_token(
            ctx.triggered_id,
            values[-1] if values else None,
            clicked_value(ctx.triggered),
        )
