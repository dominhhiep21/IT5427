"""Dash components for the "Tích hợp" tab card and its state contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml
from dash import html

from src.common.exceptions import ConfigurationError, QueryExecutionError, SchemaError
from src.common.logging import NullLogger
from src.dashboard.formatting import format_number
from src.integration.load import load_don_hang
from src.integration.query import rewrite_plan, run_monthly_orders
from src.integration.schema import load_schema

STATE_EMPTY = "rong"
STATE_PENDING = "chua-chay"
STATE_LOADING = "dang-tai"
STATE_FULL = "day-du"
STATE_PARTIAL = "mot-phan"
STATE_ERROR = "loi"

STATE_ICONS = {
    STATE_EMPTY: "ℹ",
    STATE_PENDING: "○",
    STATE_LOADING: "⏳",
    STATE_FULL: "✓",
    STATE_PARTIAL: "⚠",
    STATE_ERROR: "✕",
}

TEXTS = {
    "status_rong": "Rỗng",
    "status_chua-chay": "Chưa chạy",
    "status_dang-tai": "Đang tải",
    "status_day-du": "Đầy đủ",
    "status_mot-phan": "Một phần",
    "status_loi": "Lỗi",
    "title": "Số đơn theo tháng",
    "pending_hint": ("Chưa chạy truy vấn lần nào. Bấm nút bên dưới để chạy truy vấn mẫu trên dữ liệu nguồn."),
    "empty_hint": "Truy vấn chạy xong nhưng không có đơn nào.",
    "empty_hint_passive": (
        "Chạy truy vấn mẫu này để xem số đơn theo tháng, kế hoạch viết lại và kết quả đối chiếu KPI."
    ),
    "run": "Chạy truy vấn",
    "retry": "Thử lại",
    "previous": "Đang hiện kết quả lần trước",
    "error_default": "Không dựng được thẻ.",
    "error_schema": "Không đọc được dữ liệu nguồn.",
    "error_query": "Không chạy được truy vấn.",
    "total_suffix": " đơn",
    "total_prefix": "Tổng toàn kỳ",
    "column_month": "Tháng",
    "column_status": "Trạng thái",
    "column_orders": "Số đơn",
    "caption": "12 tháng gần nhất",
}

DEFAULT_ACTION_ID = "tich-hop-cap-nhat"

_LAST_RESULT = None
_LAST_RESULT_AT: datetime | None = None


@dataclass(frozen=True)
class TabConfig:
    """The "Tích hợp" tab contract (C9)."""

    tab_id: str
    tab_label: str
    card_ids: tuple[str, ...]
    callback_ids: tuple[str, ...]
    result_region_ids: tuple[str, ...] = ()


RESULT_REGION_ID = "don-theo-thang"


def _id_list(raw: dict, key: str) -> tuple[str, ...]:
    value = raw.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ConfigurationError(f"Cấu hình tab thiếu danh sách id {key!r}.")
    return tuple(value)


def _region_ids(raw: dict) -> tuple[str, ...]:
    """C9 buộc tab khai vùng kết quả; thiếu `don-theo-thang` là cấu hình hỏng."""

    value = raw.get("result_region_ids")
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ConfigurationError("Cấu hình tab thiếu danh sách id 'result_region_ids'.")
    regions = tuple(value)
    if RESULT_REGION_ID not in regions:
        raise ConfigurationError(
            f"Cấu hình tab phải khai vùng kết quả {RESULT_REGION_ID!r} trong 'result_region_ids'."
        )
    return regions


def load_tab_config(path: Path) -> TabConfig:
    """Read the tab contract from config/integration-tab.yaml."""

    path = Path(path)
    if not path.exists():
        raise ConfigurationError(f"Không tìm thấy tệp cấu hình tab: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Không đọc được tệp cấu hình tab: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError("Tệp cấu hình tab phải là một ánh xạ YAML.")
    tab_id = raw.get("tab_id")
    tab_label = raw.get("tab_label")
    if not isinstance(tab_id, str) or not tab_id:
        raise ConfigurationError("Cấu hình tab thiếu 'tab_id'.")
    if not isinstance(tab_label, str) or not tab_label:
        raise ConfigurationError("Cấu hình tab thiếu 'tab_label'.")
    return TabConfig(
        tab_id=tab_id,
        tab_label=tab_label,
        card_ids=_id_list(raw, "card_ids"),
        callback_ids=_id_list(raw, "callback_ids"),
        result_region_ids=_region_ids(raw),
    )


def reset_last_result() -> None:
    """Drop the remembered successful result."""

    global _LAST_RESULT, _LAST_RESULT_AT
    _LAST_RESULT = None
    _LAST_RESULT_AT = None


def _status(state: str) -> html.P:
    return html.P(
        [
            html.Span(
                STATE_ICONS[state],
                className="integration-status-icon",
                **{"aria-hidden": "true"},
            ),
            html.Span(TEXTS[f"status_{state}"], className="integration-status-text"),
        ],
        className="integration-status",
        **{"data-state": state},
    )


def _title(text: str = TEXTS["title"]) -> html.H3:
    return html.H3(text, className="integration-card-title")


def _action_button(label: str, action_id: str) -> html.Button:
    return html.Button(
        label,
        id=action_id,
        className="integration-action",
        n_clicks=0,
        **{"data-testid": "integration-action"},
    )


def _numbers(result) -> html.Div:
    """Headline figures, labelled by scope: whole-period total, whole-period row count."""

    return html.Div(
        [
            html.P(
                f"{TEXTS['total_prefix']}: {format_number(result.total_orders)}{TEXTS['total_suffix']}",
                className="integration-total",
                **{"data-testid": "integration-total"},
            ),
            html.P(
                f"{format_number(result.row_count)} dòng của cả kỳ · {result.elapsed_ms} ms",
                className="integration-detail",
                **{"data-testid": "integration-detail"},
            ),
        ],
        className="integration-numbers",
    )


def _months_table(result) -> html.Table:
    window = set(result.months or ())
    rows = [
        html.Tr(
            [
                html.Td(str(row.get("thang", row.get("group_key", "")))),
                html.Td(str(row.get("trang_thai", row.get("group_key", "")))),
                html.Td(
                    format_number(row.get("so_don", row.get("gia_tri", row.get("ty_le", 0)))),
                    className="num",
                ),
            ]
        )
        for row in result.rows
        if not window or str(row.get("thang", row.get("group_key", ""))) in window
    ]
    return html.Table(
        [
            html.Caption(f"{TEXTS['caption']} · {format_number(len(rows))} dòng hiển thị"),
            html.Thead(
                html.Tr(
                    [
                        html.Th(TEXTS["column_month"]),
                        html.Th(TEXTS["column_status"]),
                        html.Th(TEXTS["column_orders"], className="num"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        className="integration-table",
    )


def _previous_block(previous, previous_at: datetime | None) -> html.Div:
    label = TEXTS["previous"]
    if previous_at is not None:
        label = f"{label} · {previous_at.strftime('%H:%M:%S')}"
    return html.Div(
        [
            html.P(label, className="integration-previous-label"),
            _numbers(previous),
            _months_table(previous),
        ],
        className="integration-previous",
        **{"data-testid": "integration-previous"},
    )


def build_integration_card(
    result=None,
    state: str = STATE_EMPTY,
    *,
    title: str | None = None,
    show_action: bool = True,
    error: str | None = None,
    previous=None,
    previous_at: datetime | None = None,
    action_id: str = DEFAULT_ACTION_ID,
) -> html.Section:
    """Build the card for one of its six states."""

    if state not in STATE_ICONS:
        raise ValueError(f"Trạng thái thẻ không hợp lệ: {state!r}")

    children = [_title(title or TEXTS["title"]), _status(state)]
    if state == STATE_LOADING:
        children.append(
            html.Div(
                [html.Div(className="skeleton-line") for _ in range(3)],
                className="integration-skeleton",
            )
        )
    elif state == STATE_ERROR:
        children.append(
            html.P(
                error or TEXTS["error_default"],
                className="integration-error",
                **{"data-testid": "integration-error"},
            )
        )
        if previous is not None:
            children.append(_previous_block(previous, previous_at))
        if show_action:
            children.append(_action_button(TEXTS["retry"], action_id))
    elif state in (STATE_EMPTY, STATE_PENDING):
        hint = TEXTS["pending_hint"] if state == STATE_PENDING else TEXTS["empty_hint"]
        children.append(
            html.P(
                hint if show_action else TEXTS["empty_hint_passive"],
                className="integration-hint",
                **{"data-testid": "integration-hint"},
            )
        )
        if show_action:
            children.append(_action_button(TEXTS["run"], action_id))
    else:
        children.append(_numbers(result))
        children.append(_months_table(result))
        if state == STATE_PARTIAL:
            children.append(
                html.Ul(
                    [html.Li(item) for item in result.partial],
                    className="integration-partial",
                    **{"data-testid": "integration-partial"},
                )
            )
    return html.Section(
        children,
        className="integration-card",
        **{"data-state": state},
    )


def _state_for(result) -> str:
    if result.row_count == 0:
        return STATE_EMPTY
    if result.partial:
        return STATE_PARTIAL
    return STATE_FULL


def _error_text(exc: BaseException) -> str:
    if isinstance(exc, SchemaError):
        return TEXTS["error_schema"]
    if isinstance(exc, QueryExecutionError):
        return TEXTS["error_query"]
    return TEXTS["error_default"]


def render_integration_card(config, logger=None) -> list:
    """Load, query and render; never raise out of the card."""

    global _LAST_RESULT, _LAST_RESULT_AT
    logger = logger or NullLogger()
    action_id = DEFAULT_ACTION_ID
    try:
        action_id = load_tab_config(config.integration_tab_path).callback_ids[0]
        schema = load_schema(Path(config.mediated_schema_path))
        plan = rewrite_plan(schema.entity("don_hang"))
        loaded = load_don_hang(config, logger)
        result = run_monthly_orders(loaded.orders, plan, logger)
        card = build_integration_card(result, state=_state_for(result), action_id=action_id)
        _LAST_RESULT = result
        _LAST_RESULT_AT = datetime.now()
        return [card]
    except Exception as exc:  # noqa: BLE001 - the card must never crash the tab
        logger.error(
            "integration.card.render_failed",
            "result_unreadable",
            reason=str(exc)[:200],
        )
        return [
            build_integration_card(
                _LAST_RESULT,
                state=STATE_ERROR,
                error=_error_text(exc),
                previous=_LAST_RESULT,
                previous_at=_LAST_RESULT_AT,
                action_id=action_id,
            )
        ]
