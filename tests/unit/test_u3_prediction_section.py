"""Unit test cho khối Dự đoán của tab "Kết quả phân tích" (BR3.11–BR3.27).

Mọi báo cáo và tệp mô hình ở đây được dựng trong `tmp_path` hoặc trong bộ nhớ: không test nào
đọc `data/reports/analysis.json` hay `data/models/` của repo, nên bộ nhanh vẫn hermetic (`TD-09`).
"""

from __future__ import annotations

import pickle
import re
import time
from pathlib import Path

import pandas as pd
import pytest
from dash import Input, Output, State, html

from src.analytics.model import (
    CATEGORICAL_FEATURES,
    FEATURES,
    MODEL_DIGITS,
    NUMERIC_FEATURES,
    PredictionContribution,
    PredictionOutcome,
    build_feature_frame,
    encode_features,
)
from src.analytics.persistence import MODEL_FILE_NAME, fit_persistable, save_model
from src.analytics.report import (
    RUN_STATS_HINT,
    AnalysisReport,
    ModelBlock,
    ReportView,
    write_report,
)
from src.dashboard import prediction_section
from src.dashboard.formatting import format_number, format_percent
from src.dashboard.prediction_section import (
    FIELD_ERRORS,
    FIELD_LABELS,
    FORM_ID,
    INPUT_IDS,
    LOADING_ID,
    MODEL_UNAVAILABLE_EVENT,
    PAYMENT_TYPES,
    RESULT_BODY_ID,
    STATE_CODES,
    SUBMIT_ID,
    TEXTS3,
    TOKEN_MODEL_MISSING,
    TOKEN_PENDING,
    build_prediction_body,
    model_available,
    validate_form,
)
from src.analytics.model import score_item
from src.analytics.persistence import load_model

ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = "2026-11-12T03:09:36+00:00"

# 11 giá trị hợp lệ, đúng kiểu mà 10 thành phần của biểu mẫu trả về.
VALID = {
    "seller_state": "SP",
    "customer_state": "RJ",
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


# --- Đi cây thành phần ---------------------------------------------------------


def walk(node):
    yield node
    children = getattr(node, "children", None)
    if children is None or isinstance(children, str):
        return
    if isinstance(children, (list, tuple)):
        for child in children:
            if child is None or isinstance(child, str):
                continue
            yield from walk(child)
    elif not isinstance(children, (int, float)):
        yield from walk(children)


def props(node) -> dict:
    return node.to_plotly_json().get("props", {})


def nodes_with(node, key: str, value) -> list:
    return [item for item in walk(node) if props(item).get(key) == value]


def controls(body, component) -> list:
    return [item for item in walk(body) if item.to_plotly_json().get("type") == component]


def text_of(node) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float)):
        return ""
    if isinstance(node, (list, tuple)):
        return " ".join(text_of(child) for child in node)
    children = getattr(node, "children", None)
    return text_of(children) if children is not None else ""


def result_area(body) -> html.Div:
    found = nodes_with(body, "id", "du-doan-ket-qua")

    assert len(found) == 1
    return found[0]


# --- Hằng đóng của khối --------------------------------------------------------


def test_state_codes_are_the_27_federal_units():
    well_formed = [
        len(code) == 2 and code.isascii() and code.isalpha() and code.isupper() for code in STATE_CODES
    ]

    assert len(STATE_CODES) == 27
    assert len(set(STATE_CODES)) == 27
    assert all(well_formed)
    assert {"SP", "RJ", "MG", "BA", "RS"} <= set(STATE_CODES)


def test_payment_types_are_the_five_contract_values():
    assert len(PAYMENT_TYPES) == 5
    assert set(PAYMENT_TYPES) == {"credit_card", "boleto", "voucher", "debit_card", "not_defined"}


def test_caption_names_the_grain_and_the_form():
    """BR3.16 — dự đoán dành cho MỘT DÒNG HÀNG, không phải một đơn."""

    lowered = TEXTS3["caption"].lower()

    assert "dòng hàng" in lowered
    assert "một món" in lowered


def test_input_ids_cover_the_eleven_values_with_ten_components():
    assert set(INPUT_IDS) == set(VALID)
    assert len(set(INPUT_IDS.values())) == 10


def test_the_guidance_sentence_reuses_the_shared_command():
    """BR3.25 — câu hướng dẫn dùng lại `RUN_STATS_HINT`, không viết lệnh thành literal thứ hai."""

    assert RUN_STATS_HINT in TEXTS3["model_missing"]
    assert "data/models/" in TEXTS3["model_missing"]


# --- validate_form: chín luật, lỗi tại ô ---------------------------------------


def test_a_valid_form_has_no_errors():
    assert validate_form(VALID) == {}


def test_a_valid_form_typed_as_strings_has_no_errors():
    """`dcc.Input` trả chuỗi khi người dùng đang gõ, nên miền phải nhận cả chuỗi số."""

    typed = {**VALID, "item_price": "100", "item_count": "2", "installments": "3"}

    assert validate_form(typed) == {}


@pytest.mark.parametrize(
    ("field", "value", "input_id"),
    [
        ("seller_state", "ZZ", "o-bang-nguoi-ban"),
        ("customer_state", "SAO PAULO", "o-bang-nguoi-mua"),
        ("order_date", "không-phải-ngày", "o-ngay-dat"),
        ("item_price", -1, "o-gia-mon"),
        ("item_price", "abc", "o-gia-mon"),
        ("item_count", 0, "o-so-mon"),
        ("installments", 0, "o-tra-gop"),
        ("handling_days", -1, "o-ngay-ban-giao"),
        ("approval_days", 366, "o-ngay-duyet"),
        ("payment_type", "pix", "o-thanh-toan"),
    ],
)
def test_each_bad_field_reports_one_error_at_its_own_input(field, value, input_id):
    errors = validate_form({**VALID, field: value})

    assert errors == {input_id: errors[input_id]}
    assert errors[input_id]


def test_an_empty_field_reports_an_error_instead_of_raising():
    errors = validate_form({**VALID, "order_date": None, "item_price": None})

    assert set(errors) == {"o-ngay-dat", "o-gia-mon"}


def test_boundary_values_are_accepted():
    boundary = {**VALID, "item_price": 0, "handling_days": 0, "approval_days": "365"}
    beyond = validate_form({**boundary, "handling_days": 365.5})

    assert validate_form(boundary) == {}
    assert set(beyond) == {"o-ngay-ban-giao"}


def test_a_fractional_item_count_is_rejected():
    assert set(validate_form({**VALID, "item_count": 1.5})) == {"o-so-mon"}


# --- Ranh giới phụ thuộc của mô-đun -------------------------------------------


def _source() -> str:
    return Path(prediction_section.__file__).read_text(encoding="utf-8")


def _imported_top_levels() -> set[str]:
    names: set[str] = set()
    for line in _source().splitlines():
        match = re.match(r"^(?:from|import)\s+([A-Za-z0-9_.]+)", line.strip())
        if match:
            names.add(match.group(1).split(".")[0])
    return names


def test_prediction_module_imports_no_new_dependency():
    """SD3.10 — chỉ dash, dash_mantine_components, pandas và gói của repo."""

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    pinned = {line.split("==")[0].strip().lower() for line in requirements.splitlines() if "==" in line}
    third_party = _imported_top_levels() - {"__future__", "collections", "typing", "pathlib", "src"}

    assert third_party <= pinned


def test_prediction_module_imports_no_analytics_service_and_no_warehouse():
    """SR3.11 — khối không mở DuckDB và không import dịch vụ đọc mart."""

    source = _source()

    assert "AnalyticsService" not in source
    assert "warehouse" not in source
    assert "analysis_tab" not in source


def test_prediction_module_has_no_remote_or_upload_path():
    source = _source()

    for banned in ("requests", "urlopen", "upload"):
        assert banned not in source


def test_no_secret_like_literals_in_prediction_module():
    lowered = _source().lower()

    for banned in ("password", "secret", "api_key"):
        assert banned not in lowered


# --- Báo cáo và mô hình dựng trong bộ nhớ -------------------------------------


def model_block(threshold: float = 0.4) -> ModelBlock:
    return ModelBlock(
        target="is_late",
        split={
            "train_start": "2016-09-15",
            "train_end": "2018-03-31",
            "test_start": "2018-04-01",
            "test_end": "2018-08-29",
            "train_n": 64_322,
            "test_n": 32_156,
        },
        auc=0.5133,
        threshold=threshold,
        precision=0.0866,
        recall=0.2645,
        unit="line_item",
        counts={
            "flagged": 5_910,
            "not_flagged": 26_246,
            "total": 32_156,
            "threshold_method": "max_f1_on_test_grid005",
            "auc_below_target": True,
            "cohort_rows": 112_650,
            "cohort_orders": 98_666,
            "late_rows": 8_713,
            "excluded_missing_carrier": 0,
        },
    )


def report(model: ModelBlock | None = None) -> AnalysisReport:
    return AnalysisReport(version=3, generated_at=GENERATED_AT, stats=None, model=model or model_block())


# Payload tối thiểu mà `load_model` chấp nhận; dùng chung cho ba test về tệp mô hình.
PAYLOAD = {
    "estimator": None,
    "categories": {},
    "scaler_means": [],
    "scaler_scales": [],
    "feature_names": [],
    "state_regions": {},
}


def store_payload(config) -> Path:
    """Ghi payload tối thiểu vào `config.models_dir`; trả đường dẫn tệp."""

    path = Path(config.models_dir) / MODEL_FILE_NAME
    with path.open("wb") as handle:
        pickle.dump(PAYLOAD, handle)
    return path


def store_fitted_model(config) -> None:
    """Ghi một mô hình thật nhỏ vào `config.models_dir` để callback chấm bằng `score_item` thật."""

    rows = 40
    frame = pd.DataFrame(
        {
            "item_count": [1.0 + index % 3 for index in range(rows)],
            "item_total": [10.0 + index for index in range(rows)],
            "item_price_max": [5.0 + index % 9 for index in range(rows)],
            "payment_installments": [1.0 + index % 4 for index in range(rows)],
            "handling_days": [float(index % 5) for index in range(rows)],
            "approval_days": [float(index % 3) for index in range(rows)],
            "payment_type": ["credit_card", "boleto"] * (rows // 2),
            "customer_state": ["SP", "RJ"] * (rows // 2),
            "customer_region": ["Sudeste"] * rows,
            "purchase_month": [str(1 + index % 12) for index in range(rows)],
            "purchase_weekday": [str(index % 7) for index in range(rows)],
            "seller_state": ["SP", "RJ"] * (rows // 2),
            "has_items": [True] * rows,
            "has_payment": [True] * rows,
        }
    )
    features = build_feature_frame(frame)
    matrix, _ = encode_features(features, features)
    labels = pd.Series([bool(index % 3) for index in range(rows)])
    categories = {
        column: sorted({"unknown"} | set(frame[column].astype(str))) for column in CATEGORICAL_FEATURES
    }
    fitted = fit_persistable(
        matrix,
        labels,
        categories=categories,
        scaler_means=matrix[list(NUMERIC_FEATURES)].mean().to_numpy(),
        scaler_scales=matrix[list(NUMERIC_FEATURES)].std(ddof=0).replace(0, 1).to_numpy(),
    )
    save_model(fitted, Path(config.models_dir))


# --- Biểu mẫu: mười thành phần, mười một giá trị -------------------------------


def test_body_is_a_fieldset_with_ten_controls_for_eleven_values():
    body = build_prediction_body(report(), model_present=True)
    checklist = controls(body, "Checklist")

    assert isinstance(body, html.Fieldset)
    assert props(body).get("id") == FORM_ID
    assert len(controls(body, "Dropdown")) == 3
    assert len(controls(body, "Input")) == 6
    assert len(checklist) == 1
    assert len(props(checklist[0]).get("options")) == 2
    assert len(props(checklist[0]).get("value")) == 2


def test_every_input_id_appears_exactly_once():
    body = build_prediction_body(report(), model_present=True)

    for input_id in set(INPUT_IDS.values()):
        assert len(nodes_with(body, "id", input_id)) == 1


def test_every_control_sits_in_its_own_labelled_field():
    """BR3.12 — nhãn là phần tử thật trong DOM; `dcc` không nhận `aria-label`."""

    body = build_prediction_body(report(), model_present=True)
    wrappers = {props(item)["data-field"]: item for item in walk(body) if "data-field" in props(item)}

    assert set(wrappers) == set(INPUT_IDS.values())
    for field, input_id in INPUT_IDS.items():
        assert len(nodes_with(wrappers[input_id], "id", input_id)) == 1
        if field not in ("has_items", "has_payment"):
            assert FIELD_LABELS[field] in text_of(wrappers[input_id])


def test_form_has_a_fieldset_and_a_legend():
    body = build_prediction_body(report(), model_present=True)
    legends = [item for item in walk(body) if item.to_plotly_json().get("type") == "Legend"]

    assert len(legends) == 1
    assert TEXTS3["legend"] in text_of(legends[0])


def test_dropdowns_offer_the_closed_domains():
    body = build_prediction_body(report(), model_present=True)
    by_id = {props(item).get("id"): props(item) for item in walk(body) if props(item).get("id")}

    for input_id in (INPUT_IDS["seller_state"], INPUT_IDS["customer_state"]):
        values = [option["value"] for option in by_id[input_id]["options"]]
        assert values == list(STATE_CODES)
    payments = [option["value"] for option in by_id[INPUT_IDS["payment_type"]]["options"]]
    assert payments == list(PAYMENT_TYPES)


def test_four_fields_show_their_defaults_and_stay_editable():
    """BR3.18 — bốn trường mặc định hiện đúng giá trị và sửa được, không ẩn và không khoá."""

    body = build_prediction_body(report(), model_present=True)
    by_id = {props(item).get("id"): props(item) for item in walk(body) if props(item).get("id")}

    assert by_id[INPUT_IDS["payment_type"]]["value"] == "credit_card"
    assert by_id[INPUT_IDS["installments"]]["value"] == 1
    assert by_id["o-co-hang"]["value"] == ["has_items", "has_payment"]
    assert by_id[INPUT_IDS["seller_state"]]["value"] == "SP"
    assert by_id[INPUT_IDS["customer_state"]]["value"] == "SP"
    for input_id in (
        INPUT_IDS["payment_type"],
        INPUT_IDS["installments"],
        "o-co-hang",
        INPUT_IDS["order_date"],
    ):
        assert by_id[input_id].get("disabled") is not True
        assert by_id[input_id].get("readOnly") is not True


# --- Sáu trạng thái của khối --------------------------------------------------


def test_button_is_enabled_when_the_model_is_ready():
    body = build_prediction_body(report(), model_present=True)
    button = nodes_with(body, "id", SUBMIT_ID)[0]

    assert props(button).get("disabled") is not True
    assert TEXTS3["submit"] in text_of(button)


def test_missing_model_disables_the_button_and_shows_both_verbatim_strings():
    """BR3.25 — câu hướng dẫn chứa nguyên văn lệnh và đường dẫn, nút tắt."""

    body = build_prediction_body(report(), model_present=False)
    button = nodes_with(body, "id", SUBMIT_ID)[0]
    area = result_area(body)

    assert props(button).get("disabled") is True
    assert props(area).get("data-state") == TOKEN_MODEL_MISSING
    assert RUN_STATS_HINT in text_of(area)
    assert "data/models/" in text_of(area)


def test_pending_area_shows_one_guidance_line_and_no_digits():
    """BR3.26 — trước lần dự đoán đầu, vùng kết quả không hiện chữ số nào."""

    body = build_prediction_body(report(), model_present=True)
    area = result_area(body)
    lines = [item for item in walk(area) if item.to_plotly_json().get("type") == "P"]

    assert props(area).get("data-state") == TOKEN_PENDING
    assert len(lines) == 1
    assert not any(character.isdigit() for character in text_of(area))


def test_loading_wraps_the_result_area():
    """BR3.27 — "đang tính" là spinner của `dcc.Loading`, không có Output thứ hai."""

    body = build_prediction_body(report(), model_present=True)
    loadings = controls(body, "Loading")

    assert len(loadings) == 1
    assert props(loadings[0]).get("id") == LOADING_ID
    assert nodes_with(loadings[0], "id", RESULT_BODY_ID)


def test_result_area_shows_no_filesystem_path(config):
    """SD3.4 — cây con kết quả không lộ đường dẫn tuyệt đối của máy chạy."""

    for model_present in (True, False):
        body = build_prediction_body(report(), model_present=model_present)
        rendered = str(result_area(body).to_plotly_json())

        assert str(config.workspace_root) not in rendered
        assert "\\" not in rendered


def test_block_does_not_add_a_second_aria_live():
    """BR3.14 — `RESULT_BODY_ID` của tab là nơi thông báo duy nhất."""

    for model_present in (True, False):
        body = build_prediction_body(report(), model_present=model_present)

        assert [item for item in walk(body) if props(item).get("aria-live")] == []


# --- model_available: một lượt nạp, không ném ---------------------------------


def test_model_available_is_false_when_the_models_directory_is_empty(config):
    assert model_available(config) is False


def test_model_available_is_true_when_the_payload_loads(config):
    store_payload(config)

    assert model_available(config) is True


def test_model_available_returns_false_and_logs_the_raw_message_for_a_corrupt_payload(config):
    (Path(config.models_dir) / MODEL_FILE_NAME).write_bytes(b"not-a-pickle")
    records: list[tuple[str, dict]] = []

    class Recorder:
        def warning(self, event: str, **fields: object) -> None:
            records.append((event, fields))

    assert model_available(config, Recorder()) is False
    assert [event for event, _ in records] == [MODEL_UNAVAILABLE_EVENT]
    assert MODEL_FILE_NAME in records[0][1]["error"]


def test_model_available_loads_the_payload_once(config, monkeypatch):
    calls: list[Path] = []

    def fake_load(models_dir):
        calls.append(Path(models_dir))
        return object()

    monkeypatch.setattr(prediction_section, "load_model", fake_load)

    assert model_available(config) is True
    assert len(calls) == 1


# --- Kết quả một lần chấm: xác suất, ngưỡng, kết luận, ba đóng góp ------------


def outcome(probability: float = 0.0811, verdict: str = "below_threshold") -> PredictionOutcome:
    return PredictionOutcome(
        probability=probability,
        verdict=verdict,
        contributions=(
            PredictionContribution(field="handling_days", sign="positive", log_odds=0.4213),
            PredictionContribution(field="customer_state", sign="negative", log_odds=-0.3187),
            PredictionContribution(field="payment_type", sign="positive", log_odds=0.2014),
        ),
    )


def outcome_view(probability: float = 0.0811, verdict: str = "below_threshold", threshold=0.4):
    return prediction_section.build_outcome_view(outcome(probability, verdict), threshold)


def test_outcome_view_shows_probability_threshold_and_a_line_item_verdict():
    """BR3.17 — xác suất định dạng Brazil, phép so ngưỡng, câu kết luận nói về dòng hàng."""

    shown = text_of(outcome_view())

    assert format_percent(0.0811 * 100) in shown
    assert format_number(0.4, 2) in shown
    assert "dòng hàng" in shown.lower()
    assert props(outcome_view()).get("data-state") == prediction_section.TOKEN_RESULT


def test_outcome_view_switches_the_verdict_at_the_threshold():
    below = text_of(outcome_view(0.0811, "below_threshold"))
    above = text_of(outcome_view(0.9137, "at_or_above_threshold"))

    assert below != above
    assert "không bị gắn cờ" in below.lower()
    assert "không bị gắn cờ" not in above.lower()
    assert "dòng hàng" in above.lower()


def test_outcome_view_lists_exactly_three_contributions_with_vietnamese_labels():
    """BR3.20, BR3.21 — đúng ba dòng, mỗi dòng nhãn tiếng Việt của trường, nhãn log-odds nguyên văn."""

    view = outcome_view()
    rows = [item for item in walk(view) if item.to_plotly_json().get("type") == "Li"]
    label = "Ba đóng góp lớn nhất (log-odds, không phải tổng)"

    assert len(rows) == 3
    assert TEXTS3["contributions"] == label
    assert label in text_of(view)
    for row, contribution in zip(rows, outcome().contributions, strict=True):
        assert FIELD_LABELS[contribution.field] in text_of(row)
        assert format_number(contribution.log_odds, MODEL_DIGITS) in text_of(row)


def test_outcome_view_shows_no_filesystem_path(config):
    """SD3.4 — cây kết quả không lộ đường dẫn tuyệt đối của máy chạy."""

    rendered = str(outcome_view().to_plotly_json())

    assert str(config.workspace_root) not in rendered
    assert "\\" not in rendered


# --- Báo cáo và mô hình: hai lần đọc có kiểm soát ------------------------------


def report_view(threshold: float = 0.4) -> ReportView:
    return ReportView("day-du", report=report(model_block(threshold)))


def report_without_model() -> ReportView:
    return ReportView(
        "mot-phan",
        report=AnalysisReport(version=3, generated_at=GENERATED_AT),
        missing=("model",),
    )


def test_read_prediction_report_returns_the_empty_status_without_a_file(config):
    assert prediction_section.read_prediction_report(config).status == "rong"


def test_read_prediction_report_reads_the_report_the_stats_stage_writes(config):
    write_report(config, report())

    view = prediction_section.read_prediction_report(config)

    # Báo cáo chỉ có khối mô hình là `mot-phan` (thiếu khối thống kê), nhưng vẫn đọc được ngưỡng.
    assert view.status == "mot-phan"
    assert view.report is not None
    assert view.report.model.threshold == 0.4


def test_load_prediction_model_returns_none_when_the_directory_is_empty(config):
    assert prediction_section.load_prediction_model(config) is None


def test_load_prediction_model_returns_the_payload_when_it_loads(config):
    store_payload(config)

    assert prediction_section.load_prediction_model(config) is not None


def test_load_prediction_model_returns_none_and_logs_the_raw_message_for_a_corrupt_payload(config):
    (Path(config.models_dir) / MODEL_FILE_NAME).write_bytes(b"not-a-pickle")
    records: list[tuple[str, dict]] = []

    class Recorder:
        def warning(self, event: str, **fields: object) -> None:
            records.append((event, fields))

    assert prediction_section.load_prediction_model(config, Recorder()) is None
    assert [event for event, _ in records] == [MODEL_UNAVAILABLE_EVENT]
    assert MODEL_FILE_NAME in records[0][1]["error"]


# --- Callback: một Output, mười hai Input, không State ------------------------


# 11 giá trị theo đúng thứ tự `INPUT_FIELDS`; hai cờ cuối cùng một danh sách đã chọn.
FORM_VALUES = (
    "SP",
    "RJ",
    "credit_card",
    "2018-01-01",
    100,
    1,
    1,
    1,
    3,
    ["has_items", "has_payment"],
    ["has_items", "has_payment"],
)


def form_values(**overrides) -> tuple:
    values = list(FORM_VALUES)
    for field, value in overrides.items():
        values[prediction_section.INPUT_FIELDS.index(field)] = value
    return tuple(values)


class RecordingApp:
    """`app.callback` giả: giữ Output/Input đã khai để test đếm, và trả nguyên hàm được trang trí."""

    def __init__(self) -> None:
        self.outputs: list = []
        self.inputs: list = []
        self.states: list = []
        self.prevent_initial_call = None
        self.function = None

    def callback(self, *args, **kwargs):
        for item in args:
            if isinstance(item, Output):
                self.outputs.append(item)
            elif isinstance(item, Input):
                self.inputs.append(item)
            elif isinstance(item, State):
                self.states.append(item)
        self.prevent_initial_call = kwargs.get("prevent_initial_call")

        def decorator(function):
            self.function = function
            return function

        return decorator


def registered(config, logger=None) -> RecordingApp:
    app = RecordingApp()
    prediction_section.register_prediction_callback(app, config, logger)
    return app


def test_callback_declares_one_output_and_twelve_inputs_without_state(config):
    """BR3.13, BR3.27 — một Output, mười hai Input (nút + 11 giá trị), không State."""

    app = registered(config)

    assert len(app.outputs) == 1
    assert app.outputs[0].component_id == RESULT_BODY_ID
    assert app.outputs[0].component_property == "children"
    assert len(app.inputs) == 12
    assert len({(item.component_id, item.component_property) for item in app.inputs}) == 11
    assert app.states == []
    assert app.prevent_initial_call is True


def test_callback_scores_with_the_threshold_read_from_the_report(config, monkeypatch):
    """BR3.17 — ngưỡng LUÔN lấy từ báo cáo vừa đọc, không có giá trị mặc định."""

    seen: dict[str, float] = {}
    monkeypatch.setattr(prediction_section, "read_report", lambda path: report_view(0.85))
    monkeypatch.setattr(prediction_section, "load_model", lambda models_dir: object())

    def fake_score(model, item, *, threshold):
        seen["threshold"] = threshold
        return outcome()

    monkeypatch.setattr(prediction_section, "score_item", fake_score)

    tree = registered(config).function(1, *FORM_VALUES)

    assert seen["threshold"] == 0.85
    assert props(tree).get("data-state") == prediction_section.TOKEN_RESULT


def test_callback_reports_a_field_error_and_never_scores(config, monkeypatch):
    """BR3.19 — lỗi hiện tại đúng ô, và `score_item` không được gọi."""

    scored: list[int] = []
    monkeypatch.setattr(prediction_section, "read_report", lambda path: report_view())
    monkeypatch.setattr(prediction_section, "load_model", lambda models_dir: object())
    monkeypatch.setattr(prediction_section, "score_item", lambda *args, **kwargs: scored.append(1))

    tree = registered(config).function(1, *form_values(seller_state="ZZ"))
    errors = [item for item in walk(tree) if "field-error" in str(props(item).get("className"))]

    assert scored == []
    assert len(errors) == 1
    assert props(errors[0]).get("data-field") == INPUT_IDS["seller_state"]
    assert FIELD_ERRORS["seller_state"] in text_of(errors[0])
    assert props(tree).get("data-state") == prediction_section.TOKEN_INVALID


def test_callback_reads_the_report_and_loads_the_model_once_per_click(config, monkeypatch):
    reads: list[Path] = []
    loads: list[Path] = []

    def fake_read(path):
        reads.append(Path(path))
        return report_view()

    def fake_load(models_dir):
        loads.append(Path(models_dir))
        return object()

    monkeypatch.setattr(prediction_section, "read_report", fake_read)
    monkeypatch.setattr(prediction_section, "load_model", fake_load)
    monkeypatch.setattr(prediction_section, "score_item", lambda *args, **kwargs: outcome())

    tree = registered(config).function(1, *FORM_VALUES)

    assert [path.name for path in reads] == ["analysis.json"]
    assert loads == [Path(config.models_dir)]
    assert props(tree).get("data-state") == prediction_section.TOKEN_RESULT


def test_callback_shows_the_guidance_instead_of_touching_a_missing_model_block(config, monkeypatch):
    """BR3.24 — `report.model is None` ⇒ trạng thái thiếu mô hình, không đọc `None.threshold`."""

    scored: list[int] = []
    monkeypatch.setattr(prediction_section, "read_report", lambda path: report_without_model())
    monkeypatch.setattr(prediction_section, "score_item", lambda *args, **kwargs: scored.append(1))

    tree = registered(config).function(1, *FORM_VALUES)

    assert props(tree).get("data-state") == TOKEN_MODEL_MISSING
    assert RUN_STATS_HINT in text_of(tree)
    assert scored == []


def test_callback_shows_the_fixed_guidance_for_a_corrupt_payload_without_a_path(config, monkeypatch):
    """BR3.25, SR3.10 — payload hỏng ⇒ câu cố định, không lộ `str(error)` chứa đường dẫn tuyệt đối."""

    (Path(config.models_dir) / MODEL_FILE_NAME).write_bytes(b"not-a-pickle")
    monkeypatch.setattr(prediction_section, "read_report", lambda path: report_view())

    tree = registered(config).function(1, *FORM_VALUES)
    rendered = str(tree.to_plotly_json())

    assert props(tree).get("data-state") == TOKEN_MODEL_MISSING
    assert RUN_STATS_HINT in text_of(tree)
    assert "data/models/" in text_of(tree)
    assert str(config.models_dir) not in rendered
    assert "\\" not in rendered


def test_callback_is_deterministic_for_the_same_eleven_values(config):
    """BR3.22 — hai lần bấm cùng đầu vào cho cùng xác suất, chấm bằng mô hình thật trong `tmp_path`."""

    store_fitted_model(config)
    write_report(config, report())
    app = registered(config)

    first = text_of(app.function(1, *FORM_VALUES))
    second = text_of(app.function(1, *FORM_VALUES))

    assert first == second
    assert "dòng hàng" in first.lower()
    assert props(app.function(1, *FORM_VALUES)).get("data-state") == prediction_section.TOKEN_RESULT


# --- Câu chữ của tab và README ------------------------------------------------


def dashboard_section() -> str:
    """Đúng mục "Dashboard" của README, từ tiêu đề tới mục kế tiếp."""

    text = (ROOT / "README.md").read_text(encoding="utf-8")
    start = text.index("## Dashboard")
    end = text.index("## Micro-batch")
    return text[start:end]


def test_readme_dashboard_section_drops_the_read_only_claim():
    """BR3.15 — README không còn nói tab chỉ đọc, và nói rõ tệp mô hình nằm ở `data/models/`."""

    section = dashboard_section()

    assert "chỉ đọc" not in section.lower()
    assert "data/models/" in section


# --- Ngân sách tương tác (PR3.1–PR3.3) ---------------------------------------


def _mean_seconds(call, runs: int = 20) -> float:
    """Thời gian trung bình của `runs` lần gọi, tính bằng giây."""

    call()
    started = time.perf_counter()
    for _ in range(runs):
        call()
    return (time.perf_counter() - started) / runs


def test_scoring_one_item_stays_under_the_interaction_budget(config):
    """PR3.1 — `score_item` trên một dòng hàng < 200 ms (đo được ~10,5 ms)."""

    store_fitted_model(config)
    fitted = load_model(config.models_dir)
    assert fitted is not None

    elapsed = _mean_seconds(lambda: score_item(fitted, dict(VALID), threshold=0.4))

    assert elapsed < 0.2


def test_loading_the_model_file_stays_under_the_interaction_budget(config):
    """PR3.2 — `load_model` trên tệp do `save_model` sinh < 2 s (đo được ~0,3 ms)."""

    store_fitted_model(config)

    elapsed = _mean_seconds(lambda: load_model(config.models_dir), runs=5)

    assert elapsed < 2.0


def test_building_the_prediction_body_stays_under_the_interaction_budget():
    """PR3.3 — dựng thân mục Dự đoán < 300 ms (đo được ~2 ms)."""

    body = report()

    elapsed = _mean_seconds(lambda: build_prediction_body(body, model_present=True))

    assert elapsed < 0.3


def test_the_registered_callback_scores_without_a_server_error(config):
    """BR3.13, MON3.6 — gọi callback **thật** đã đăng ký, như Dash gọi.

    Lỗi thật gặp trên trình duyệt 2026-11-14: `app.py` truyền factory `_integration_logger`
    (cần `config`), `_info` gọi `logger()` ⇒ `TypeError` ⇒ HTTP 500 và khối kẹt ở "chưa dự đoán".
    Test gọi qua `app.callback_map` nên bắt được đúng đường dây đó.
    """

    from src.dashboard.app import create_app

    store_fitted_model(config)
    write_report(config, report())

    app = create_app(config)
    callback = app.callback_map[f"{RESULT_BODY_ID}.children"]["callback"].__wrapped__

    result = callback(1, *FORM_VALUES)

    assert isinstance(result, html.Div)
    assert props(result).get("data-state") == prediction_section.TOKEN_RESULT


@pytest.mark.parametrize("feature", FEATURES)
def test_every_trained_feature_has_a_vietnamese_label(feature: str):
    """BR3.20 — mọi trường có thể xuất hiện trong ba đóng góp đều có nhãn tiếng Việt."""

    label = FIELD_LABELS.get(feature)

    assert label is not None
    assert label != feature
    assert not label.isascii()
