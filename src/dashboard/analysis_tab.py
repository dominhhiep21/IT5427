"""Tab "Kết quả phân tích": đọc báo cáo C2 rồi dựng nội dung, không tính toán gì (BR3.1–BR3.10)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import dash_mantine_components as dmc
from dash import Dash, Input, Output, dcc, html, no_update

from src.analytics.report import (
    RUN_STATS_HINT,
    STATUS_EMPTY,
    STATUS_ERROR,
    STATUS_PARTIAL,
    AnalysisReport,
    ModelBlock,
    ReportView,
    SkipEntry,
    StatsBlock,
    read_report,
    report_path,
)
from src.analytics.model import AUC_TARGET
from src.analytics.statistics import MIN_STATE_ORDERS
from src.dashboard.formatting import format_number, format_percent
from src.dashboard.prediction_section import (
    TEXTS3 as PREDICTION_TEXTS,
    build_prediction_body,
    model_available,
)
from src.integration.card import STATE_ICONS, TEXTS as CARD_TEXTS

TABS_ID = "tabs"
TAB_VALUE = "phan-tich"
TAB_LABEL = "Kết quả phân tích"

# Vùng nội dung do callback thay; khối chờ của `dcc.Loading` dùng `custom_spinner`.
RESULT_BODY_ID = "analysis-result"

# Trạng thái duy nhất do giao diện tự sinh; bốn token còn lại lấy thẳng từ `ReportView.status`.
TOKEN_PENDING = "chua-chay"

# Cùng literal xanh mực mà `src/integration/tab.py` dùng cho spinner; không phải token mới trong CSS.
LOADING_COLOR = "#2F7D6A"

SECTION_SUMMARY = "tom-tat"
SECTION_STATS = "thong-ke"
SECTION_MODEL = "mo-hinh"
SECTION_PREDICTION = "du-doan"
SECTION_IDS = (SECTION_SUMMARY, SECTION_STATS, SECTION_MODEL, SECTION_PREDICTION)

CARD_IDS = ("ti-le-tre", "so-don", "so-bo-qua", "auc")

BLOCK_LABELS = {"stats": "khối thống kê", "model": "khối mô hình"}

TEXTS = {
    "heading": "Báo cáo phân tích và mô hình",
    "summary": "Tóm tắt",
    "stats": "Thống kê",
    "model": "Mô hình",
    "summary_caption": "Bốn chỉ số đọc từ báo cáo, không tính lại trong trình duyệt",
    "stats_caption": "Năm phép kiểm định của tầng stats; mục không chạy được vẫn hiện kèm lý do",
    "model_caption": "Ngưỡng đọc từ báo cáo; mục Dự đoán bên dưới chấm ở grain MỘT DÒNG HÀNG",
    "empty_notice": "Chưa có báo cáo phân tích. Chạy lệnh bên dưới để sinh tệp rồi mở lại tab này.",
    "error_notice": "Không đọc được báo cáo phân tích.",
    "partial_notice": "Báo cáo mới có một phần kết quả: thiếu {missing}; phần đã có vẫn hiển thị bên dưới.",
    "missing_stats": "Chưa chạy bước thống kê. Chạy lệnh bên dưới rồi mở lại tab này.",
    "missing_model": "Chưa chạy bước mô hình. Chạy lệnh bên dưới rồi mở lại tab này.",
    "not_available": "chưa có",
    "auc_below": "không đạt mốc {target}",
    "auc_meets": "đạt mốc {target}",
    "skipped_heading": "Kiểm định không chạy được",
    "cannot_run": "Không chạy được",
    "cannot_run_here": "Không chạy được trong lần này.",
    "comparisons_missing": "Không đủ hai bang đạt ngưỡng {threshold} đơn đã giao.",
    "late_rate": "Tỉ lệ giao trễ",
    "orders": "Số đơn đã giao",
    "skipped": "Kiểm định bị bỏ",
    "skipped_none": "Không có kiểm định nào bị bỏ",
    "skipped_listed": "Đã liệt kê ở mục thống kê",
    "late_rate_sample": "Mẫu của tỉ lệ trễ",
    "auc": "AUC trên tập kiểm tra",
    "threshold": "Ngưỡng cảnh báo",
    "threshold_readonly": "Lấy từ báo cáo; tab không tính lại trên ngưỡng khác",
    "precision": "Precision",
    "recall": "Recall",
    "on_test_split": "Trên tập kiểm tra",
    "target": "Đích",
    "train": "Huấn luyện",
    "test": "Kiểm tra",
    "flagged": "Đã gắn cờ",
    "stats_late_rate": "Tỉ lệ giao trễ",
    "stats_comparisons": "So sánh hai bang",
    "stats_correlation": "Tương quan giá hàng và phí vận chuyển",
    "stats_group_test": "Kiểm định nhóm theo vùng",
    "stats_seasonal": "Mùa vụ doanh thu theo tháng",
    "significant": "có ý nghĩa",
    "not_significant": "chưa đủ ý nghĩa",
}


@dataclass(frozen=True)
class ResultTabState:
    """Trạng thái hiển thị của tab, suy ra từ `ReportView`; chỉ `chua-chay` do giao diện tự sinh."""

    token: str
    notice: str = ""
    command_hint: str = ""


@dataclass(frozen=True)
class SummaryCard:
    """Một thẻ của dải tóm tắt; `status_note` chỉ thẻ AUC dùng."""

    card_id: str
    label: str
    value: str
    status_note: str = ""


# --- state-mapper -------------------------------------------------------------


def pending_state() -> ResultTabState:
    """Trạng thái của giao diện trong lúc đọc tệp (BR3.1)."""

    return ResultTabState(TOKEN_PENDING)


def state_for(view: ReportView) -> ResultTabState:
    """Ánh xạ thẳng `ReportView.status` thành token; không dò chuỗi thông điệp để đoán trạng thái."""

    if view.status == STATUS_EMPTY:
        return ResultTabState(STATUS_EMPTY, TEXTS["empty_notice"], RUN_STATS_HINT)
    if view.status == STATUS_ERROR:
        return ResultTabState(STATUS_ERROR, view.message or TEXTS["error_notice"])
    if view.status == STATUS_PARTIAL:
        return ResultTabState(STATUS_PARTIAL, _partial_notice(view.missing))
    return ResultTabState(view.status)


def _partial_notice(missing: tuple[str, ...]) -> str:
    """Câu chữ nêu đúng phần thiếu; khối thiếu vẫn giữ chỗ trong bố cục (BR3.4)."""

    labels = [BLOCK_LABELS.get(name, name) for name in missing]
    return TEXTS["partial_notice"].format(missing=" và ".join(labels))


def _status_line(token: str) -> html.P:
    """Huy hiệu trạng thái, dùng đúng bộ lớp và bộ nhãn của tab "Tích hợp"."""

    return html.P(
        [
            html.Span(
                STATE_ICONS.get(token, "•"),
                className="integration-status-icon",
                **{"aria-hidden": "true"},
            ),
            html.Span(CARD_TEXTS.get(f"status_{token}", token), className="integration-status-text"),
        ],
        className="integration-status",
        **{"data-state": token},
    )


def StateBanner(state: ResultTabState) -> html.Div:
    """Câu trạng thái; lệnh cần chạy hiện bằng khối mã để chép lại được (BR3.5)."""

    children: list[Any] = [_status_line(state.token)]
    if state.notice:
        children.append(html.P(state.notice, className="integration-state-message"))
    if state.command_hint:
        children.append(html.Code(state.command_hint, className="integration-sql"))
    return html.Div(
        children,
        className="integration-state",
        role="status",
        **{"data-state": state.token, "data-testid": "analysis-state"},
    )


# --- summary-strip ------------------------------------------------------------


def summary_cards(report: AnalysisReport) -> list[SummaryCard]:
    """Các thẻ có nguồn dữ liệu, theo thứ tự ti-le-tre, so-don, so-bo-qua, auc (BR3.3)."""

    cards: list[SummaryCard] = []
    if report.stats is not None:
        rate = report.stats.late_rate
        cards.append(
            SummaryCard(
                "ti-le-tre",
                TEXTS["late_rate"],
                # `late_rate.rate` là phân số 0–1 và `format_percent` không nhân 100.
                format_percent(rate.rate * 100),
                f"{format_number(rate.successes)} / {format_number(rate.total)} đơn đã giao",
            )
        )
        cards.append(
            SummaryCard("so-don", TEXTS["orders"], format_number(rate.total), TEXTS["late_rate_sample"])
        )
        cards.append(
            SummaryCard(
                "so-bo-qua",
                TEXTS["skipped"],
                format_number(len(report.stats.skipped)),
                TEXTS["skipped_listed"] if report.stats.skipped else TEXTS["skipped_none"],
            )
        )
    if report.model is None:
        cards.append(SummaryCard("auc", TEXTS["auc"], TEXTS["not_available"]))
    else:
        cards.append(
            SummaryCard("auc", TEXTS["auc"], format_number(report.model.auc, 4), _auc_note(report.model))
        )
    return cards


def _auc_note(model: ModelBlock) -> str:
    """Dấu đạt/không đạt lấy từ cờ trong tệp; nhãn nêu mốc đang áp từ `AUC_TARGET` (BR3.28)."""

    below = model.counts["auc_below_target"]
    template = TEXTS["auc_below"] if below else TEXTS["auc_meets"]
    return template.format(target=format_number(AUC_TARGET, 2))


def _card_node(card: SummaryCard) -> html.Div:
    return html.Div(
        [
            html.P(card.label, className="kpi-label"),
            html.P(card.value, className="kpi-value"),
            html.P(card.status_note, className="kpi-detail") if card.status_note else None,
        ],
        className="kpi-card",
        **{"data-card": card.card_id},
    )


def build_summary_section(report: AnalysisReport) -> html.Section:
    """Dải tóm tắt: số thẻ phụ thuộc dữ liệu có nguồn, không dựng thẻ rỗng."""

    strip = html.Div([_card_node(card) for card in summary_cards(report)], className="kpi-strip")
    return _section(SECTION_SUMMARY, TEXTS["summary"], TEXTS["summary_caption"], [strip])


# --- stats-section ------------------------------------------------------------


def _item(item_id: str, label: str, value: str, detail: str = "") -> html.Div:
    return html.Div(
        [
            html.P(label, className="kpi-label"),
            html.P(value, className="integration-total"),
            html.P(detail, className="integration-detail") if detail else None,
        ],
        className="integration-block",
        **{"data-item": item_id},
    )


def _missing_item(item_id: str, label: str, reason: str) -> html.Div:
    return _item(item_id, label, TEXTS["cannot_run"], reason)


def _skip_reason(skipped: list[SkipEntry], name: str) -> str:
    """Lý do của đúng phép bị bỏ, đọc từ `skipped` của cùng tệp (BR3.10)."""

    for entry in skipped:
        if entry.test == name:
            return entry.reason
    return TEXTS["cannot_run_here"]


def _confidence_label(stats: StatsBlock) -> str:
    return format_percent(stats.confidence * 100, 0)


def _comparison_item(stats: StatsBlock) -> html.Div:
    if not stats.comparisons:
        return _missing_item(
            "so-sanh-bang",
            TEXTS["stats_comparisons"],
            TEXTS["comparisons_missing"].format(threshold=format_number(MIN_STATE_ORDERS)),
        )
    head = stats.comparisons[0]
    lines = [
        f"{item.first} – {item.second}: chênh {format_percent(item.difference * 100)} · "
        f"z = {format_number(item.z, 4)} · p = {format_number(item.p_value, 4)} · "
        + (TEXTS["significant"] if item.significant else TEXTS["not_significant"])
        for item in stats.comparisons
    ]
    return _item(
        "so-sanh-bang",
        TEXTS["stats_comparisons"],
        f"{head.first} – {head.second}",
        " · ".join(lines),
    )


def _correlation_item(stats: StatsBlock) -> html.Div:
    block = stats.correlation
    if block is None:
        return _missing_item(
            "tuong-quan", TEXTS["stats_correlation"], _skip_reason(stats.skipped, "correlation")
        )
    return _item(
        "tuong-quan",
        TEXTS["stats_correlation"],
        f"r = {format_number(block.r, 3)}",
        f"n = {format_number(block.n)} dòng hàng · khoảng tin cậy {_confidence_label(stats)}: "
        f"{format_number(block.ci_low, 4)} – {format_number(block.ci_high, 4)}",
    )


def _group_test_item(stats: StatsBlock) -> html.Div:
    block = stats.group_test
    if block is None:
        return _missing_item(
            "kiem-dinh-nhom", TEXTS["stats_group_test"], _skip_reason(stats.skipped, "group_test")
        )
    return _item(
        "kiem-dinh-nhom",
        TEXTS["stats_group_test"],
        f"χ² = {format_number(block.statistic, 4)}",
        f"bậc tự do {format_number(block.dof)} · p = {format_number(block.p_value, 4)} · "
        f"ô kỳ vọng nhỏ nhất {format_number(block.min_expected, 3)}",
    )


def _seasonal_item(stats: StatsBlock) -> html.Div:
    block = stats.seasonal
    if block is None:
        return _missing_item("mua-vu", TEXTS["stats_seasonal"], _skip_reason(stats.skipped, "seasonal"))
    return _item(
        "mua-vu",
        TEXTS["stats_seasonal"],
        f"{format_number(len(block.months))} tháng · chu kỳ {format_number(block.period)}",
        f"{block.revenue_definition} · {block.method}",
    )


def build_stats_items(stats: StatsBlock) -> list[html.Div]:
    """Năm mục thống kê; mục null hiện tên phép kèm lý do, không bỏ trống (BR3.10)."""

    rate = stats.late_rate
    return [
        _item(
            "ti-le-tre",
            TEXTS["stats_late_rate"],
            format_percent(rate.rate * 100),
            f"{format_number(rate.successes)} / {format_number(rate.total)} đơn đã giao · "
            f"khoảng tin cậy {_confidence_label(stats)}: {format_percent(rate.ci_low * 100)} – "
            f"{format_percent(rate.ci_high * 100)}",
        ),
        _comparison_item(stats),
        _correlation_item(stats),
        _group_test_item(stats),
        _seasonal_item(stats),
    ]


def build_skipped_banner(stats: StatsBlock) -> html.Section | None:
    """Dải kiểm định bị bỏ: rỗng thì không dựng, có phần tử thì mỗi phần tử một dòng (BR3.6)."""

    if not stats.skipped:
        return None
    return html.Section(
        [
            html.P(TEXTS["skipped_heading"], className="kpi-label"),
            html.Ul(
                [html.Li(f"{entry.test} — {entry.reason}") for entry in stats.skipped],
                className="integration-state-items",
            ),
        ],
        className="integration-skipped",
        role="region",
        **{"aria-label": TEXTS["skipped_heading"], "data-testid": "skipped-banner"},
    )


def build_stats_section(report: AnalysisReport) -> html.Section:
    stats = report.stats
    if stats is None:
        return _section(
            SECTION_STATS,
            TEXTS["stats"],
            TEXTS["stats_caption"],
            [_missing_block(TEXTS["missing_stats"], "stats")],
        )
    children: list[Any] = [*build_stats_items(stats)]
    banner = build_skipped_banner(stats)
    if banner is not None:
        children.append(banner)
    return _section(SECTION_STATS, TEXTS["stats"], TEXTS["stats_caption"], children)


# --- model-section ------------------------------------------------------------


def _model_figures(model: ModelBlock) -> html.Ul:
    """Đích, cỡ mẫu hai tập và số dòng hàng đã gắn cờ; ba con số đọc trực tiếp (BR3.30)."""

    figures: list[str] = []
    if model.target:
        figures.append(f"{TEXTS['target']}: {model.target}")
    split = model.split
    figures.append(
        f"{TEXTS['train']}: {format_number(split['train_n'])} dòng hàng"
        f" ({split['train_start']} → {split['train_end']})"
    )
    figures.append(
        f"{TEXTS['test']}: {format_number(split['test_n'])} dòng hàng"
        f" ({split['test_start']} → {split['test_end']})"
    )
    figures.append(f"{TEXTS['flagged']}: {format_number(model.counts['flagged'])} dòng hàng")
    return html.Ul([html.Li(text) for text in figures], className="integration-figures")


def build_model_section(report: AnalysisReport) -> html.Section:
    """Bốn số đọc của khối mô hình, không thanh trượt và không ô nhập (BR3.7)."""

    model = report.model
    if model is None:
        return _section(
            SECTION_MODEL,
            TEXTS["model"],
            TEXTS["model_caption"],
            [_missing_block(TEXTS["missing_model"], "model")],
        )
    return _section(
        SECTION_MODEL,
        TEXTS["model"],
        TEXTS["model_caption"],
        [
            _item("auc", TEXTS["auc"], format_number(model.auc, 4), _auc_note(model)),
            _item(
                "nguong",
                TEXTS["threshold"],
                format_number(model.threshold, 2),
                TEXTS["threshold_readonly"],
            ),
            _item("precision", TEXTS["precision"], format_number(model.precision, 4), TEXTS["on_test_split"]),
            _item("recall", TEXTS["recall"], format_number(model.recall, 4), TEXTS["on_test_split"]),
            _model_figures(model),
        ],
    )


# --- khung tab ----------------------------------------------------------------


def _section_header(title: str, caption: str) -> html.Header:
    return html.Header(
        [html.H3(title), html.P(caption, className="chart-subtitle") if caption else None],
        className="chart-header",
    )


def _section(section_id: str, title: str, caption: str, children: list[Any]) -> html.Section:
    """Một khối nội dung, mang `data-section` và `aria-label` để mọi vùng đều có nhãn (BR3.8).

    Thân khối là một lưới một cột có `gap` sẵn trong `assets/style.css`, nên các mục không dính
    vào nhau mà không phải thêm lớp mới.
    """

    return html.Section(
        [_section_header(title, caption), html.Div(children, className="chart-stack")],
        className="chart-card",
        role="region",
        **{"aria-label": title, "data-section": section_id},
    )


def _missing_block(text: str, block: str) -> html.Div:
    """Chỗ của khối thiếu vẫn được giữ, kèm câu chữ và lệnh cần chạy (BR3.4)."""

    return html.Div(
        [html.P(text), html.Code(RUN_STATS_HINT, className="integration-sql")],
        className="empty-state",
        **{"data-missing": block},
    )


def sections_for(view: ReportView | None, model_present: bool = False) -> list[Any]:
    """Bốn khối theo thứ tự đọc cố định tóm tắt → thống kê → mô hình → dự đoán (BR3.11, BR3.23)."""

    body = None if view is None else view.report
    if body is None:
        return []
    sections: list[Any] = [
        build_summary_section(body),
        build_stats_section(body),
        build_model_section(body),
    ]
    if body.model is None:
        return sections
    try:
        sections.append(build_prediction_section(body, model_present))
    except Exception:  # noqa: BLE001 - mục Dự đoán hỏng không được kéo sập ba mục còn lại
        sections.append(_prediction_fallback())
    return sections


def build_prediction_section(body: AnalysisReport, model_present: bool) -> html.Section:
    """Mục Dự đoán bọc thân do `prediction_section` dựng; khung và nhãn vùng ở lại tab này (BR3.12)."""

    return _section(
        SECTION_PREDICTION,
        PREDICTION_TEXTS["heading"],
        PREDICTION_TEXTS["caption"],
        [build_prediction_body(body, model_present)],
    )


def _prediction_fallback() -> html.Section:
    """Mục thay thế khi thân mục ném; câu cố định, không lộ thông điệp lỗi thô (BR3.25)."""

    notice = html.Div(
        [html.P(PREDICTION_TEXTS["body_error"])],
        className="empty-state",
        **{"data-state": STATUS_ERROR},
    )
    return _section(SECTION_PREDICTION, PREDICTION_TEXTS["heading"], "", [notice])


def AnalysisPanel(
    state: ResultTabState,
    view: ReportView | None = None,
    model_present: bool = False,
) -> html.Div:
    """Toàn bộ nội dung của tab cho một lần đọc: tiêu đề, câu trạng thái, bốn khối."""

    return html.Div(
        [
            dmc.Title(TEXTS["heading"], order=3),
            StateBanner(state),
            *sections_for(view, model_present),
        ],
        className="chart-stack",
        role="region",
        **{"aria-label": TAB_LABEL, "data-state": state.token, "data-testid": "analysis-panel"},
    )


def AnalysisTab() -> list:
    """Khung tab: một vùng nội dung thay được, khối chờ làm `custom_spinner` của `dcc.Loading`.

    Không đọc báo cáo ở đây: tệp chỉ được đọc trong callback, nếu không nội dung đóng băng tại
    lúc khởi động dashboard và token `chua-chay` không bao giờ hiện ra.
    """

    body = html.Div(
        AnalysisPanel(pending_state()),
        id=RESULT_BODY_ID,
        **{
            "data-state": TOKEN_PENDING,
            "data-testid": RESULT_BODY_ID,
            "aria-label": TAB_LABEL,
            "aria-live": "polite",
        },
    )
    # DMC cần provider bao ngoài thì `dmc.Title` mới có theme và style (ADR-U6-S4).
    return [
        html.Div(
            className="analysis-tab",
            children=dmc.MantineProvider(
                children=dcc.Loading(
                    body,
                    custom_spinner=AnalysisPanel(pending_state()),
                    type="default",
                    color=LOADING_COLOR,
                )
            ),
        )
    ]


# --- tab-callback -------------------------------------------------------------


def render_analysis(config, tab_value: str | None, reader=None) -> Any:
    """Đọc báo cáo đúng một lần rồi dựng nội dung; tab khác được chọn thì không đọc (NFR5.6)."""

    if tab_value != TAB_VALUE:
        return no_update
    read = reader or read_report
    try:
        view = read(report_path(config))
    except Exception as exc:  # noqa: BLE001 - tab không được làm sập cả dashboard
        return AnalysisPanel(ResultTabState(STATUS_ERROR, f"{TEXTS['error_notice']} {exc}"))
    return AnalysisPanel(state_for(view), view, _model_present(config, view))


def _model_present(config, view: ReportView) -> bool:
    """Hỏi đúng một lần lúc dựng panel, và chỉ khi có khối mô hình để chấm (BR3.25)."""

    body = view.report
    if body is None or body.model is None:
        return False
    return model_available(config)


def register_callback(app: Dash, config, reader=None) -> None:
    """`tab-callback`: một callback, một Output, một lần đọc tệp mỗi lần chọn tab."""

    @app.callback(Output(RESULT_BODY_ID, "children"), Input(TABS_ID, "value"))
    def load_analysis(tab_value):  # noqa: ANN001 - chữ ký do Dash quyết định
        return render_analysis(config, tab_value, reader)
