"""Khối Dự đoán của tab "Kết quả phân tích": hằng đóng, kiểm biểu mẫu, dựng cây và một callback.

Mô-đun này chỉ dựng cây Dash và kiểm đầu vào ở một chỗ (SD3.1); nó không đọc DuckDB, không đi qua
dịch vụ đọc mart, và không import ngược tab — hướng phụ thuộc một chiều.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd
from dash import Dash, Input, Output, dcc, html

from src.analytics.model import (
    MAX_DAYS,
    MODEL_DIGITS,
    STATE_CODE_LENGTH,
    ModelError,
    PredictionOutcome,
    score_item,
)
from src.analytics.persistence import load_model
from src.analytics.report import (
    RUN_STATS_HINT,
    AnalysisReport,
    ReportView,
    read_report,
    report_path,
)
from src.dashboard.formatting import format_number, format_percent

# Ba token render được của khối; `dang-tai` là spinner của `dcc.Loading`, không phải token.
TOKEN_PENDING = "chua-chay"
TOKEN_MODEL_MISSING = "mo-hinh-chua-san"
TOKEN_RESULT = "day-du"

# Lỗi hiện trong vùng kết quả — nhập sai hoặc không chấm được; dùng lại token đóng của repo.
TOKEN_INVALID = "loi"

FORM_ID = "bieu-mau-du-doan"
SUBMIT_ID = "nut-du-doan"
RESULT_BODY_ID = "du-doan-ket-qua"
LOADING_ID = "du-doan-dang-tai"
CHECKLIST_ID = "o-co-hang"

MODEL_UNAVAILABLE_EVENT = "prediction.model_unavailable"
SCORED_EVENT = "prediction.scored"
REJECTED_EVENT = "prediction.input_rejected"

# `score_item` trả đúng hai kết luận; khối không tự dựng lại phép so ngưỡng (BR3.17).
VERDICT_ABOVE = "at_or_above_threshold"

# 27 mã UF; SD3.2 — hằng đóng, không nhận danh sách từ tệp hay từ người dùng.
STATE_CODES = (
    "AC",
    "AL",
    "AM",
    "AP",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MG",
    "MS",
    "MT",
    "PA",
    "PB",
    "PE",
    "PI",
    "PR",
    "RJ",
    "RN",
    "RO",
    "RR",
    "RS",
    "SC",
    "SE",
    "SP",
    "TO",
)

# Năm giá trị thanh toán; miền do giao diện khai, U2 coi đây là chuỗi tự do (BR3.18).
PAYMENT_TYPES = ("credit_card", "boleto", "voucher", "debit_card", "not_defined")

# Tên trường → id thành phần; hai cờ boolean dùng chung một `dcc.Checklist`.
INPUT_IDS = {
    "seller_state": "o-bang-nguoi-ban",
    "customer_state": "o-bang-nguoi-mua",
    "payment_type": "o-thanh-toan",
    "order_date": "o-ngay-dat",
    "item_price": "o-gia-mon",
    "item_count": "o-so-mon",
    "installments": "o-tra-gop",
    "approval_days": "o-ngay-duyet",
    "handling_days": "o-ngay-ban-giao",
    "has_items": CHECKLIST_ID,
    "has_payment": CHECKLIST_ID,
}

# Thứ tự mười một giá trị mà callback nhận: chín ô đơn lẻ rồi hai cờ của `dcc.Checklist`.
INPUT_FIELDS = (
    "seller_state",
    "customer_state",
    "payment_type",
    "order_date",
    "item_price",
    "item_count",
    "installments",
    "approval_days",
    "handling_days",
    "has_items",
    "has_payment",
)

FLAG_FIELDS = ("has_items", "has_payment")

# Mười một giá trị mặc định của biểu mẫu (BR3.18).
DEFAULT_VALUES = {
    "seller_state": "SP",
    "customer_state": "SP",
    "payment_type": "credit_card",
    "order_date": "2018-01-01",
    "item_price": 100,
    "item_count": 1,
    "installments": 1,
    "handling_days": 3,
    "approval_days": 1,
    "has_items": True,
    "has_payment": True,
}

TEXTS3 = {
    "heading": "Dự đoán",
    "caption": "Dự đoán cho MỘT DÒNG HÀNG: một món trong một đơn, có người bán riêng",
    "legend": "Thông tin một dòng hàng",
    "submit": "Dự đoán",
    "pending": "Chưa dự đoán. Điền thông tin một dòng hàng rồi bấm nút Dự đoán.",
    # BR3.25 — dùng lại `RUN_STATS_HINT`, không viết lệnh thành literal thứ hai.
    "model_missing": (
        f"Chưa có mô hình để dự đoán. Chạy `{RUN_STATS_HINT}` để sinh tệp trong `data/models/`, "
        "rồi tải lại trang."
    ),
    "body_error": "Mục Dự đoán tạm thời không dựng được; ba mục còn lại vẫn hiển thị bình thường.",
    "checklist_label": "Dòng hàng có món và có thanh toán",
    # BR3.17, BR3.20, BR3.21 — ba dòng của thẻ kết quả.
    "probability": "Xác suất dòng hàng bị giao trễ",
    "comparison_above": "Xác suất bằng hoặc trên ngưỡng cảnh báo {threshold}",
    "comparison_below": "Xác suất dưới ngưỡng cảnh báo {threshold}",
    "verdict_above": "Kết luận cho dòng hàng này: bị gắn cờ giao trễ",
    "verdict_below": "Kết luận cho dòng hàng này: không bị gắn cờ giao trễ",
    "contributions": "Ba đóng góp lớn nhất (log-odds, không phải tổng)",
    "invalid": "Kiểm lại các ô được đánh dấu rồi bấm Dự đoán lần nữa.",
    "score_failed": "Không chấm được dòng hàng này:",
}

# Nhãn tiếng Việt của từng trường, dùng cho `aria-label` và cho phần đóng góp (BR3.20).
FIELD_LABELS = {
    "seller_state": "Bang người bán",
    "customer_state": "Bang người mua",
    "customer_region": "Vùng người mua",
    "payment_type": "Hình thức thanh toán",
    "payment_installments": "Số kỳ trả góp",
    "order_date": "Ngày đặt hàng (YYYY-MM-DD)",
    "item_price": "Giá món hàng (BRL)",
    "item_price_max": "Giá cao nhất trong đơn",
    "item_count": "Số món trong đơn",
    "item_total": "Tổng giá trị đơn",
    "purchase_month": "Tháng đặt hàng",
    "purchase_weekday": "Thứ trong tuần",
    "installments": "Số kỳ trả góp",
    "approval_days": "Số ngày đặt → duyệt",
    "handling_days": "Số ngày duyệt → bàn giao",
    "has_items": "Có món trong đơn",
    "has_payment": "Có thanh toán",
}

# Thông điệp lỗi hiện ngay dưới đúng ô (BR3.19).
FIELD_ERRORS = {
    "seller_state": "Chọn bang người bán",
    "customer_state": "Chọn bang người mua",
    "payment_type": "Chọn hình thức thanh toán",
    "order_date": "Ngày phải theo dạng YYYY-MM-DD",
    "item_price": "Giá phải là số không âm",
    "item_count": "Số món phải là số nguyên từ 1",
    "installments": "Số kỳ trả góp phải từ 1",
    "approval_days": "Số ngày đặt→duyệt phải trong 0…365",
    "handling_days": "Số ngày duyệt→bàn giao phải trong 0…365",
}

DAY_FIELDS = ("handling_days", "approval_days")


def _number(value: Any) -> float | None:
    """Đọc một ô số; trả `None` khi giá trị trống, không đọc được, hay không hữu hạn."""

    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    return number


def _is_state_code(value: Any) -> bool:
    """Mã bang phải là một trong 27 UF; dạng hai chữ cái trùng `_serve_features` của U2."""

    text = str(value).upper()
    return len(text) == STATE_CODE_LENGTH and text in STATE_CODES


def _is_date(value: Any) -> bool:
    """Ngày phải đọc được bằng `pd.Timestamp`, cùng phép đọc mà U2 dùng lúc chấm điểm."""

    if value is None or value == "":
        return False
    try:
        pd.Timestamp(str(value))
    except (TypeError, ValueError):
        return False
    return True


def validate_form(values: Mapping[str, Any]) -> dict[str, str]:
    """SD3.1 — kiểm 11 giá trị ở một chỗ, trả lỗi theo id ô; hàm thuần, không I/O."""

    errors: dict[str, str] = {}
    for field in ("seller_state", "customer_state"):
        if not _is_state_code(values.get(field)):
            errors[INPUT_IDS[field]] = FIELD_ERRORS[field]
    if str(values.get("payment_type", "")) not in PAYMENT_TYPES:
        errors[INPUT_IDS["payment_type"]] = FIELD_ERRORS["payment_type"]
    if not _is_date(values.get("order_date")):
        errors[INPUT_IDS["order_date"]] = FIELD_ERRORS["order_date"]

    price = _number(values.get("item_price"))
    if price is None or price < 0:
        errors[INPUT_IDS["item_price"]] = FIELD_ERRORS["item_price"]

    for field in ("item_count", "installments"):
        count = _number(values.get(field))
        if count is None or count < 1 or count != int(count):
            errors[INPUT_IDS[field]] = FIELD_ERRORS[field]

    for field in DAY_FIELDS:
        days = _number(values.get(field))
        if days is None or days < 0 or days > MAX_DAYS:
            errors[INPUT_IDS[field]] = FIELD_ERRORS[field]

    return errors


# --- dựng cây ------------------------------------------------------------------


def _field(input_id: str, label: str, control: Any) -> html.Div:
    """Một ô của biểu mẫu kèm nhãn hiển thị; `data-field` để test tra đúng ô."""

    return html.Div(
        [html.Label(label), control],
        className="filter-field",
        **{"data-field": input_id},
    )


def _dropdown(field: str, options: tuple[str, ...]) -> html.Div:
    control = dcc.Dropdown(
        id=INPUT_IDS[field],
        options=[{"label": option, "value": option} for option in options],
        value=DEFAULT_VALUES[field],
        clearable=False,
    )
    return _field(INPUT_IDS[field], FIELD_LABELS[field], control)


def _input(field: str, input_type: str, **limits: Any) -> html.Div:
    control = dcc.Input(id=INPUT_IDS[field], type=input_type, value=DEFAULT_VALUES[field], **limits)
    return _field(INPUT_IDS[field], FIELD_LABELS[field], control)


def _form_fields() -> list[Any]:
    """Mười thành phần mang mười một giá trị, đúng thứ tự đọc của biểu mẫu (BR3.18)."""

    checklist = dcc.Checklist(
        id=CHECKLIST_ID,
        options=[
            {"label": FIELD_LABELS["has_items"], "value": "has_items"},
            {"label": FIELD_LABELS["has_payment"], "value": "has_payment"},
        ],
        value=["has_items", "has_payment"],
        inline=True,
    )
    return [
        _dropdown("seller_state", STATE_CODES),
        _dropdown("customer_state", STATE_CODES),
        _dropdown("payment_type", PAYMENT_TYPES),
        _input("order_date", "text"),
        _input("item_price", "number", min=0, step=1),
        _input("item_count", "number", min=1, step=1),
        _input("installments", "number", min=1, step=1),
        _input("approval_days", "number", min=0, max=MAX_DAYS, step=1),
        _input("handling_days", "number", min=0, max=MAX_DAYS, step=1),
        _field(CHECKLIST_ID, TEXTS3["checklist_label"], checklist),
    ]


def _notice(token: str, text: str) -> html.Div:
    """Một khối thông báo của vùng kết quả: đúng một câu, kèm token trạng thái."""

    return html.Div(
        [html.P(text, className="integration-state-message")],
        className="integration-state",
        **{"data-state": token},
    )


def _result_area(model_present: bool) -> html.Div:
    """Vùng kết quả ở `chua-chay` hoặc `mo-hinh-chua-san`; trạng thái có kết quả do callback dựng."""

    if model_present:
        token, notice = TOKEN_PENDING, TEXTS3["pending"]
    else:
        token, notice = TOKEN_MODEL_MISSING, TEXTS3["model_missing"]
    return html.Div(
        _notice(token, notice).children,
        id=RESULT_BODY_ID,
        className="integration-state",
        **{"data-state": token},
    )


def build_prediction_body(report: AnalysisReport, model_present: bool) -> html.Fieldset:
    """LC3.1 — thân mục Dự đoán: biểu mẫu và vùng kết quả; hàm thuần, không I/O."""

    children: list[Any] = [html.Legend(TEXTS3["legend"])]
    children.extend(_form_fields())
    children.append(
        html.Button(
            TEXTS3["submit"],
            id=SUBMIT_ID,
            n_clicks=0,
            type="button",
            className="integration-action",
            disabled=not model_present,
        )
    )
    children.append(
        dcc.Loading(_result_area(model_present), id=LOADING_ID, type="default"),
    )
    return html.Fieldset(children, id=FORM_ID)


# --- thẻ kết quả ---------------------------------------------------------------


def build_outcome_view(outcome: PredictionOutcome, threshold: float) -> html.Div:
    """LC3.2 — xác suất, phép so ngưỡng, câu kết luận về dòng hàng và ba đóng góp (BR3.17, BR3.20)."""

    percent = format_percent(outcome.probability * 100)
    threshold_text = format_number(threshold, 2)
    above = outcome.verdict == VERDICT_ABOVE
    comparison = TEXTS3["comparison_above"] if above else TEXTS3["comparison_below"]
    verdict = TEXTS3["verdict_above"] if above else TEXTS3["verdict_below"]
    rows = [
        html.Li(
            f"{FIELD_LABELS.get(item.field, item.field)}: {format_number(item.log_odds, MODEL_DIGITS)}",
            **{"data-field": item.field, "data-sign": item.sign},
        )
        for item in outcome.contributions
    ]
    return html.Div(
        [
            html.P(
                [html.Span(TEXTS3["probability"], className="kpi-label"), " ", html.Span(percent)],
                className="integration-detail",
                **{"data-line": "probability"},
            ),
            html.P(
                comparison.format(threshold=threshold_text),
                className="integration-detail",
                **{"data-line": "threshold"},
            ),
            html.P(verdict, className="integration-state-message", **{"data-line": "verdict"}),
            html.P(TEXTS3["contributions"], className="kpi-label"),
            html.Ul(rows, className="integration-figures", **{"data-contributions": "top-three"}),
        ],
        className="integration-state",
        **{"data-state": TOKEN_RESULT},
    )


def build_error_view(errors: Mapping[str, str]) -> html.Div:
    """BR3.19 — mỗi lỗi hiện tại đúng ô của nó, không ném và không chấm điểm."""

    lines = [
        html.P(
            message,
            className="field-error",
            role="alert",
            **{"data-field": input_id},
        )
        for input_id, message in errors.items()
    ]
    return html.Div(
        [html.P(TEXTS3["invalid"], className="integration-state-message"), *lines],
        className="integration-state",
        **{"data-state": TOKEN_INVALID},
    )


# --- I/O có kiểm soát và callback ----------------------------------------------


def _warning(logger, event: str, **fields: object) -> None:
    """Ghi cảnh báo qua logger đã có; `app.py` truyền factory nên hàm nhận cả factory lẫn đối tượng."""

    target = logger() if callable(logger) else logger
    if target is not None:
        target.warning(event, **fields)


def _info(logger, event: str, **fields: object) -> None:
    """Ghi thông tin qua logger đã có; `app.py` truyền factory nên hàm nhận cả factory lẫn đối tượng."""

    target = logger() if callable(logger) else logger
    if target is not None:
        target.info(event, **fields)


def model_available(config, logger=None) -> bool:
    """LC3.11 — một lượt nạp lúc dựng panel; vắng tệp hay payload hỏng đều là "chưa sẵn", không ném."""

    return load_prediction_model(config, logger) is not None


def read_prediction_report(config) -> ReportView:
    """LC3.4 — nguồn duy nhất của `threshold`: đọc lại tệp báo cáo cục bộ mỗi lần bấm, không `State`."""

    return read_report(report_path(config))


def load_prediction_model(config, logger=None):
    """LC3.5 — `load_model` có bọc: vắng tệp là `None`; payload hỏng cũng `None` kèm nhật ký (BR3.25)."""

    try:
        return load_model(config.models_dir)
    except ModelError as error:
        _warning(logger, MODEL_UNAVAILABLE_EVENT, error=str(error))
        return None


def _form_values(values: Sequence[Any]) -> dict[str, Any]:
    """Mười một giá trị theo đúng thứ tự `INPUT_FIELDS`; hai cờ cùng đọc từ danh sách đã chọn."""

    form: dict[str, Any] = dict(zip(INPUT_FIELDS[:-2], values[:-2], strict=True))
    checked = list(values[9] or ())
    form.update({field: field in checked for field in FLAG_FIELDS})
    return form


def predict_outcome(config, values: Mapping[str, Any], logger=None) -> html.Div:
    """LC3.4–LC3.6 — một lượt bấm: đọc báo cáo, kiểm biểu mẫu, nạp mô hình, chấm; không ném ra ngoài."""

    view = read_prediction_report(config)
    body = view.report
    if body is None or body.model is None:
        return _notice(TOKEN_MODEL_MISSING, TEXTS3["model_missing"])
    threshold = body.model.threshold

    errors = validate_form(values)
    if errors:
        _info(logger, REJECTED_EVENT, fields=sorted(errors))
        return build_error_view(errors)

    model = load_prediction_model(config, logger)
    if model is None:
        return _notice(TOKEN_MODEL_MISSING, TEXTS3["model_missing"])

    try:
        outcome = score_item(model, values, threshold=threshold)
    except (ModelError, ValueError, KeyError) as error:
        # Payload nạp được nhưng rỗng (thiếu khoá) cũng là lỗi chấm, không được thoát khỏi callback.
        _warning(logger, MODEL_UNAVAILABLE_EVENT, error=str(error))
        return _notice(TOKEN_INVALID, TEXTS3["score_failed"])
    _info(logger, SCORED_EVENT, verdict=outcome.verdict, threshold=threshold)
    return build_outcome_view(outcome, threshold)


def _value_inputs() -> list[Input]:
    """Mười một `Input` cho mười một giá trị; hai cờ dùng chung `Checklist` nên `value` xuất hiện hai lần."""

    return [Input(INPUT_IDS[field], "value") for field in INPUT_FIELDS]


def register_prediction_callback(app: Dash, config, logger=None) -> None:
    """LC3.3 — một callback mới, một Output, mười hai Input, không `State` (BR3.13, BR3.27)."""

    @app.callback(
        Output(RESULT_BODY_ID, "children"),
        Input(SUBMIT_ID, "n_clicks"),
        *_value_inputs(),
        prevent_initial_call=True,
    )
    def score_one_line(n_clicks: int, *values: Any) -> Any:
        return predict_outcome(config, _form_values(values), logger)
