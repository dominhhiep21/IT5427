"""Unit test cho tab "Kết quả phân tích": năm trạng thái, bốn thẻ, mục null, thứ tự, nhãn.

Mọi `ReportView` ở đây được dựng trong bộ nhớ: không test nào đọc `data/reports/analysis.json`
của repo, nên bộ nhanh vẫn hermetic (lỗ hổng `TD-09` không nặng thêm).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from dash import dcc, html, no_update

from src.analytics.report import (
    RUN_STATS_HINT,
    AnalysisReport,
    ComparisonResult,
    CorrelationResult,
    GroupTestResult,
    ModelBlock,
    ProportionResult,
    ReportView,
    SeasonalResult,
    SkipEntry,
    StatsBlock,
)
from src.config import load_config
from src.dashboard import analysis_tab
from src.dashboard.analysis_tab import (
    CARD_IDS,
    SECTION_IDS,
    TAB_LABEL,
    TAB_VALUE,
    AUC_TARGET,
    AnalysisPanel,
    AnalysisTab,
    pending_state,
    render_analysis,
    state_for,
    summary_cards,
)

ROOT = Path(__file__).resolve().parents[2]
STYLESHEET = ROOT / "assets" / "style.css"
GENERATED_AT = "2026-11-11T03:09:36+00:00"

# --- Dựng ReportView trong bộ nhớ ---------------------------------------------


def late_rate() -> ProportionResult:
    """Tỉ lệ trễ của dữ liệu thật: 7.826/96.478 = 0,0811 (phân số 0–1, không phải 8,11)."""

    return ProportionResult(successes=7_826, total=96_478, rate=0.0811, ci_low=0.0794, ci_high=0.0829)


def comparison() -> ComparisonResult:
    return ComparisonResult(
        first="AL",
        second="RO",
        difference=0.2105,
        z=7.0603,
        p_value=0.0,
        ci_low=0.1613,
        ci_high=0.2572,
        significant=True,
        excluded=188,
    )


def correlation() -> CorrelationResult:
    return CorrelationResult(r=0.413, n=110_197, ci_low=0.4078, ci_high=0.4176)


def group_test() -> GroupTestResult:
    return GroupTestResult(
        test="chi_square_region_late",
        statistic=535.9163,
        p_value=0.0,
        dof=4,
        min_expected=145.686,
    )


def seasonal() -> SeasonalResult:
    months = [f"2017-{month:02d}" for month in range(1, 13)] * 2
    return SeasonalResult(
        revenue_definition="price + freight_value của đơn delivered",
        method="classical_additive_12",
        period=12,
        months=months,
        observed=[float(index) for index in range(len(months))],
        trend=[float(index) for index in range(len(months))],
        seasonal=[0.0 for _ in months],
        residual=[0.0 for _ in months],
    )


def stats_block(**overrides) -> StatsBlock:
    base = {
        "generated_at": GENERATED_AT,
        "alpha": 0.05,
        "confidence": 0.95,
        "late_rate": late_rate(),
        "comparisons": [comparison()],
        "correlation": correlation(),
        "group_test": group_test(),
        "seasonal": seasonal(),
        "skipped": [],
    }
    base.update(overrides)
    return StatsBlock(**base)


def model_block(auc: float = 0.5133, below_target: bool = True) -> ModelBlock:
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
        auc=auc,
        threshold=0.4,
        precision=0.0866,
        recall=0.2645,
        counts={
            "flagged": 5_910,
            "not_flagged": 26_246,
            "total": 32_156,
            "threshold_method": "max_f1_on_test_grid005",
            "auc_below_target": below_target,
        },
    )


_MISSING = object()


def report(stats=_MISSING, model=_MISSING) -> AnalysisReport:
    return AnalysisReport(
        version=2,
        generated_at=GENERATED_AT,
        stats=stats_block() if stats is _MISSING else stats,
        model=model_block() if model is _MISSING else model,
    )


def view(status: str, body: AnalysisReport | None = None, **kwargs) -> ReportView:
    return ReportView(status, report=body, **kwargs)


def complete_view() -> ReportView:
    return view("day-du", report())


def partial_view(missing: tuple[str, ...]) -> ReportView:
    body = report(
        stats=None if "stats" in missing else stats_block(),
        model=None if "model" in missing else model_block(),
    )
    notice = f"Báo cáo còn thiếu khối {', '.join(missing)}."
    return view("mot-phan", body, missing=missing, message=notice)


def panel_of(result: ReportView) -> html.Div:
    return AnalysisPanel(state_for(result), result)


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


def types(node) -> set[str]:
    return {item.to_plotly_json().get("type") for item in walk(node)}


def nodes_with(node, key: str, value) -> list:
    return [item for item in walk(node) if props(item).get(key) == value]


def marked(node, key: str) -> list:
    return [props(item)[key] for item in walk(node) if key in props(item)]


def text_of(node) -> str:
    """Mọi chuỗi hiển thị trong cây, nối bằng khoảng trắng."""

    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, (list, tuple)):
        return " ".join(text_of(child) for child in node)
    children = getattr(node, "children", None)
    return text_of(children) if children is not None else ""


def class_names(node) -> set[str]:
    found: set[str] = set()
    for item in walk(node):
        value = props(item).get("className")
        if isinstance(value, str):
            found.update(value.split())
    return found


# --- BR3.1: trạng thái hợp đồng thành token giao diện -------------------------


def test_status_maps_straight_to_the_result_token():
    cases = [
        (view("rong", message="Chưa có báo cáo tại data/reports/analysis.json."), "rong"),
        (complete_view(), "day-du"),
        (partial_view(("model",)), "mot-phan"),
        (view("loi", message="Không đọc được báo cáo data/reports/analysis.json: hỏng."), "loi"),
    ]

    for result, expected in cases:
        assert state_for(result).token == expected


def test_only_the_loading_token_is_generated_by_the_tab():
    produced = {
        state_for(view(status, report() if status != "rong" else None)).token
        for status in ("rong", "day-du", "mot-phan", "loi")
    }

    assert produced == {"rong", "day-du", "mot-phan", "loi"}
    assert pending_state().token == "chua-chay"
    assert pending_state().token not in produced


def test_tab_layout_starts_in_the_loading_state():
    tab = html.Div(AnalysisTab())
    body = nodes_with(tab, "id", analysis_tab.RESULT_BODY_ID)

    assert len(body) == 1
    assert props(body[0]).get("data-state") == "chua-chay"
    # `loading-shell`: khối chờ nằm trong `custom_spinner` của `dcc.Loading`.
    spinners = [item for item in walk(tab) if "custom_spinner" in props(item)]
    assert len(spinners) == 1
    assert props(spinners[0])["custom_spinner"] is not None


def test_tab_layout_wraps_its_content_in_a_mantine_provider():
    """Gốc ứng dụng không bọc provider, nên tab tự bọc như `src/integration/tab.py` (ADR-U6-S4)."""

    tab = html.Div(AnalysisTab())

    assert "MantineProvider" in types(tab)
    assert "Title" in types(tab)
    provider = [item for item in walk(tab) if item.to_plotly_json().get("type") == "MantineProvider"]
    assert "Title" in types(provider[0])


# --- BR3.2: thứ tự đọc cố định ------------------------------------------------


def test_sections_keep_the_reading_order():
    for result in (complete_view(), partial_view(("stats",))):
        assert marked(panel_of(result), "data-section") == list(SECTION_IDS)


def test_partial_report_without_model_has_no_prediction_section():
    """BR3.23 — thiếu khối mô hình thì không có gì để chấm, nên không dựng mục Dự đoán."""

    panel = panel_of(partial_view(("model",)))

    assert marked(panel, "data-section") == ["tom-tat", "thong-ke", "mo-hinh"]


def test_section_ids_are_the_four_blocks_in_reading_order():
    assert SECTION_IDS == ("tom-tat", "thong-ke", "mo-hinh", "du-doan")


# --- BR3.3: bốn thẻ tóm tắt ---------------------------------------------------


def test_complete_report_shows_four_cards_in_order():
    cards = summary_cards(report())

    assert [card.card_id for card in cards] == list(CARD_IDS)
    assert CARD_IDS == ("ti-le-tre", "so-don", "so-bo-qua", "auc")


def test_summary_strip_renders_the_four_cards_with_values():
    panel = panel_of(complete_view())
    strip = nodes_with(panel, "data-section", "tom-tat")[0]
    cards = {card.card_id: card for card in summary_cards(report())}

    assert marked(strip, "data-card") == list(CARD_IDS)
    late = nodes_with(strip, "data-card", "ti-le-tre")[0]
    assert "8,11%" in text_of(late)
    assert "96.478" in text_of(late)
    assert cards["so-bo-qua"].value == "0"
    assert "Kiểm định bị bỏ" in text_of(strip)
    auc = nodes_with(strip, "data-card", "auc")[0]
    assert "0,5133" in text_of(auc)


def test_late_rate_is_shown_as_a_percentage_of_the_fraction():
    """`late_rate.rate` là phân số 0–1 và `format_percent` không nhân 100 — tab phải nhân (NFR5.1)."""

    cards = {card.card_id: card for card in summary_cards(report())}

    assert cards["ti-le-tre"].value == "8,11%"
    assert "0,08" not in cards["ti-le-tre"].value


def test_auc_card_reports_both_verdicts():
    below = {card.card_id: card for card in summary_cards(report(model=model_block(0.5133, True)))}
    meets = {card.card_id: card for card in summary_cards(report(model=model_block(0.7400, False)))}

    assert "không đạt" in below["auc"].status_note
    assert "đạt" in meets["auc"].status_note
    assert below["auc"].status_note != meets["auc"].status_note
    assert AUC_TARGET == 0.70


def test_model_figures_name_the_line_item_grain():
    """BR3.30 — ba con số của khối mô hình ở grain dòng hàng, không phải đơn; đọc trực tiếp."""

    panel = panel_of(complete_view())
    model = nodes_with(panel, "data-section", "mo-hinh")[0]
    figures = [text_of(item) for item in walk(model) if item.to_plotly_json().get("type") == "Li"]
    grain = [figure for figure in figures if "dòng hàng" in figure]

    # Đích + huấn luyện + kiểm tra + đã gắn cờ.
    assert len(figures) == 4
    assert len(grain) == 3
    assert not any(" đơn" in figure for figure in figures)
    assert "64.322" in grain[0]
    assert "32.156" in grain[1]
    assert "5.910" in grain[2]


def test_auc_label_follows_the_module_target(monkeypatch):
    """BR3.28 — nhãn nêu mốc đang áp lấy từ `AUC_TARGET`, không hard-code "0,70"."""

    monkeypatch.setattr(analysis_tab, "AUC_TARGET", 0.65)

    note = analysis_tab._auc_note(model_block(0.5133, True))

    assert "0,65" in note
    assert "0,70" not in note


def test_auc_label_reads_only_the_recorded_flag():
    """BR3.28 — cờ là nguồn duy nhất; tab không dựng lại phép so `model.auc < AUC_TARGET`."""

    assert "không đạt" in analysis_tab._auc_note(model_block(auc=0.99, below_target=True))
    assert "đạt" in analysis_tab._auc_note(model_block(auc=0.11, below_target=False))


def test_model_caption_does_not_claim_the_tab_is_read_only():
    """BR3.15 — câu chữ mục Mô hình không còn nói tab chỉ đọc; nay có mục Dự đoán ở grain dòng hàng."""

    caption = analysis_tab.TEXTS["model_caption"]

    assert "chỉ đọc" not in caption.lower()
    assert "dòng hàng" in caption.lower()


def test_missing_model_block_marks_the_auc_card_as_absent():
    cards = summary_cards(report(stats=stats_block(), model=None))

    assert [card.card_id for card in cards] == ["ti-le-tre", "so-don", "so-bo-qua", "auc"]
    assert cards[-1].value == "chưa có"
    assert cards[-1].status_note == ""


def test_missing_stats_block_leaves_only_the_auc_card():
    cards = summary_cards(report(stats=None, model=model_block()))

    assert [card.card_id for card in cards] == ["auc"]
    assert cards[0].value == "0,5133"


# --- BR3.4: thiếu một khối thì vẫn hiện phần có -------------------------------


def test_partial_report_without_model_still_shows_the_whole_stats_block():
    result = partial_view(("model",))
    panel = panel_of(result)
    stats = nodes_with(panel, "data-section", "thong-ke")[0]
    model = nodes_with(panel, "data-section", "mo-hinh")[0]

    assert marked(stats, "data-item") == [
        "ti-le-tre",
        "so-sanh-bang",
        "tuong-quan",
        "kiem-dinh-nhom",
        "mua-vu",
    ]
    lowered = text_of(model).lower()
    assert "chưa chạy bước mô hình" in lowered
    assert RUN_STATS_HINT in text_of(model)
    assert "chưa chạy bước thống kê" not in text_of(stats).lower()


def test_partial_report_without_stats_still_shows_the_whole_model_block():
    result = partial_view(("stats",))
    panel = panel_of(result)
    stats = nodes_with(panel, "data-section", "thong-ke")[0]
    model = nodes_with(panel, "data-section", "mo-hinh")[0]

    assert marked(model, "data-item") == ["auc", "nguong", "precision", "recall"]
    assert "chưa chạy bước thống kê" in text_of(stats).lower()
    assert RUN_STATS_HINT in text_of(stats)
    assert "chưa chạy bước mô hình" not in text_of(model).lower()
    assert "0,40" in text_of(model)


# --- BR3.5: ba trạng thái, ba câu chữ ----------------------------------------


def test_the_three_states_use_three_different_sentences():
    empty = state_for(view("rong", message="Chưa có báo cáo tại data/reports/analysis.json."))
    partial = state_for(partial_view(("model",)))
    error = state_for(view("loi", message="Báo cáo data/reports/analysis.json hỏng ở trường version."))

    sentences = [empty.notice, partial.notice, error.notice]
    assert all(sentence for sentence in sentences)
    assert len(set(sentences)) == 3


def test_empty_state_names_the_command_to_run():
    state = state_for(view("rong", message="Chưa có báo cáo tại data/reports/analysis.json."))
    panel = AnalysisPanel(state, view("rong"))

    assert state.command_hint == RUN_STATS_HINT
    assert "Chưa có báo cáo" in state.notice
    assert RUN_STATS_HINT in text_of(panel)


def test_error_state_names_the_reason_and_the_path():
    message = "Báo cáo data/reports/analysis.json hỏng ở trường version: phải bằng 2"
    state = state_for(view("loi", message=message))

    assert "data/reports/analysis.json" in state.notice
    assert "version" in state.notice


def test_complete_state_has_no_notice_and_no_command():
    state = state_for(complete_view())

    assert state.token == "day-du"
    assert state.notice == ""
    assert state.command_hint == ""


# --- BR3.6: kiểm định bị bỏ được liệt kê -------------------------------------


def test_no_skipped_entries_means_no_banner():
    panel = panel_of(complete_view())

    assert marked(panel, "data-testid").count("skipped-banner") == 0


def test_two_skipped_entries_make_two_lines():
    skipped = [
        SkipEntry(test="correlation", reason="cần ít nhất 4 dòng hàng"),
        SkipEntry(test="seasonal", reason="cần ít nhất 24 tháng"),
    ]
    panel = panel_of(view("day-du", report(stats=stats_block(skipped=skipped))))
    banner = nodes_with(panel, "data-testid", "skipped-banner")[0]

    lines = [text_of(item) for item in walk(banner) if item.to_plotly_json().get("type") == "Li"]
    assert len(lines) == 2
    assert skipped[0].reason in lines[0]
    assert skipped[1].reason in lines[1]


# --- BR3.7: ngưỡng chỉ đọc ---------------------------------------------------


def test_model_block_offers_no_input_control():
    panel = panel_of(complete_view())
    model = nodes_with(panel, "data-section", "mo-hinh")[0]

    assert types(model) & {"Slider", "Input", "RangeSlider"} == set()
    assert "0,40" in text_of(model)
    assert "0,0866" in text_of(model)
    assert "0,2645" in text_of(model)


# --- BR3.8: nhãn, bàn phím ---------------------------------------------------


def test_every_region_has_a_label_and_no_positive_tabindex():
    panel = panel_of(complete_view())
    regions = [nodes_with(panel, "data-section", section)[0] for section in SECTION_IDS]
    regions.append(panel)

    for region in regions:
        assert props(region).get("aria-label")

    for item in walk(panel):
        tab_index = props(item).get("tabIndex")
        assert tab_index is None or int(tab_index) <= 0


# --- BR3.9: chỉ dùng lớp đã có ----------------------------------------------


def test_every_class_is_defined_in_the_stylesheet():
    panel = panel_of(view("day-du", report(stats=stats_block(skipped=[SkipEntry("correlation", "lý do")]))))
    css = STYLESHEET.read_text(encoding="utf-8")

    missing = {name for name in class_names(panel) if not re.search(rf"\.{re.escape(name)}(?![\w-])", css)}
    assert missing == set()


# --- BR3.10: mục con null được hiện bằng câu chữ -----------------------------


def test_null_stats_item_shows_the_test_name_with_the_skip_reason():
    skipped = [SkipEntry(test="correlation", reason="cần ít nhất 4 dòng hàng")]
    panel = panel_of(view("day-du", report(stats=stats_block(correlation=None, skipped=skipped))))
    item = nodes_with(panel, "data-item", "tuong-quan")[0]
    lowered = text_of(item).lower()

    assert "tương quan" in lowered
    assert "không chạy được" in lowered
    assert "cần ít nhất 4 dòng hàng" in text_of(item)


def test_empty_comparisons_explain_the_missing_states():
    panel = panel_of(view("day-du", report(stats=stats_block(comparisons=[]))))
    item = nodes_with(panel, "data-item", "so-sanh-bang")[0]
    lowered = text_of(item).lower()

    assert "không đủ hai bang" in lowered
    assert "100" in text_of(item)


def test_a_null_item_without_a_recorded_reason_still_says_so():
    """`skipped` có thể không có dòng cho phép bị bỏ; mục null vẫn phải có câu chữ (BR3.10)."""

    panel = panel_of(view("day-du", report(stats=stats_block(correlation=None, skipped=[]))))
    item = nodes_with(panel, "data-item", "tuong-quan")[0]

    assert "không chạy được" in text_of(item).lower()
    assert "trong lần này" in text_of(item).lower()


def test_null_group_test_and_seasonal_stay_written_out():
    skipped = [
        SkipEntry(test="group_test", reason="ô kỳ vọng nhỏ hơn 5"),
        SkipEntry(test="seasonal", reason="cần ít nhất 24 tháng"),
    ]
    panel = panel_of(view("day-du", report(stats=stats_block(group_test=None, seasonal=None, skipped=skipped))))

    for item_id in ("kiem-dinh-nhom", "mua-vu"):
        item = nodes_with(panel, "data-item", item_id)[0]
        assert "không chạy được" in text_of(item).lower()


# --- NFR5.6: đọc tệp đúng một lần mỗi callback -------------------------------


def test_callback_reads_the_report_exactly_once(config):
    calls: list[Path] = []

    def reader(path):
        calls.append(Path(path))
        return complete_view()

    result = render_analysis(config, TAB_VALUE, reader=reader)

    assert len(calls) == 1
    assert calls[0].name == "analysis.json"
    assert props(result).get("data-state") == "day-du"


def test_each_render_uses_the_first_read_and_ignores_a_second(config):
    calls: list[int] = []

    def reader(path):
        calls.append(1)
        if len(calls) == 1:
            return complete_view()
        return view("loi", message="Không đọc được báo cáo lần hai.")

    result = render_analysis(config, TAB_VALUE, reader=reader)
    shown = text_of(result)

    assert len(calls) == 1
    assert "8,11%" in shown
    assert "lần hai" not in shown


def test_other_tab_values_do_not_read_the_report(config):
    calls: list[int] = []

    def reader(path):
        calls.append(1)
        return complete_view()

    assert render_analysis(config, "overview", reader=reader) is no_update
    assert calls == []


def test_reader_failure_becomes_the_error_state(config):
    def reader(path):
        raise OSError("đĩa hỏng")

    result = render_analysis(config, TAB_VALUE, reader=reader)

    assert props(result).get("data-state") == "loi"
    assert "đĩa hỏng" in text_of(result)


# --- app.py: tab mới nằm trong `tabs.children`, tra theo giá trị --------------


def test_analysis_tab_is_a_tab_of_the_layout_and_found_by_value():
    from src.dashboard.app import build_layout

    layout = build_layout(load_config())
    tabs = [child for child in layout.children if isinstance(child, dcc.Tabs)][0]
    by_value = {tab.value: tab for tab in tabs.children if isinstance(tab, dcc.Tab)}

    assert TAB_VALUE in by_value
    assert by_value[TAB_VALUE].label == TAB_LABEL
    assert marked(by_value[TAB_VALUE], "id").count(analysis_tab.RESULT_BODY_ID) == 1
    # Tab "Tích hợp" vẫn tra được khi không còn ở vị trí cuối.
    assert by_value["tich-hop"].label == "Tích hợp"


def test_tab_labels_are_unique():
    from src.dashboard.app import build_layout

    layout = build_layout(load_config())
    tabs = [child for child in layout.children if isinstance(child, dcc.Tabs)][0]
    values = [tab.value for tab in tabs.children if isinstance(tab, dcc.Tab)]

    assert len(values) == len(set(values))
    assert len(values) == 5


@pytest.mark.parametrize("section", SECTION_IDS)
def test_each_section_heading_is_a_real_heading(section):
    panel = panel_of(complete_view())
    node = nodes_with(panel, "data-section", section)[0]

    assert {"H3", "Title"} & types(node) == {"H3"}
    assert props(node).get("aria-label")


# --- mục Dự đoán: hình dạng, lỗi cục bộ, một lượt hỏi mô hình ------------------


def test_summary_strip_keeps_four_cards_with_the_prediction_section():
    panel = panel_of(complete_view())

    assert marked(panel, "data-card") == list(CARD_IDS)
    assert len(summary_cards(report())) == 4


def test_the_only_aria_live_region_is_the_result_body():
    """BR3.14 — mục Dự đoán không tự đặt `aria-live`; cả tab chỉ có một vùng thông báo."""

    tab = html.Div(AnalysisTab())
    live = [props(item)["aria-live"] for item in walk(tab) if "aria-live" in props(item)]

    assert live == ["polite"]


def test_prediction_body_failure_keeps_the_other_three_sections(monkeypatch):
    """BR3.25 — thân mục ném thì mục thay thế xuất hiện, ba mục còn lại nguyên vẹn, tab không ném."""

    def broken(body, model_present):
        raise RuntimeError("không dựng được biểu mẫu")

    monkeypatch.setattr(analysis_tab, "build_prediction_body", broken)

    panel = panel_of(complete_view())

    assert marked(panel, "data-section") == list(SECTION_IDS)
    assert analysis_tab.PREDICTION_TEXTS["body_error"] in text_of(panel)


def test_render_analysis_asks_for_the_model_once_and_passes_the_answer(config, monkeypatch):
    calls: list[int] = []

    def fake_model_available(config, logger=None):
        calls.append(1)
        return True

    monkeypatch.setattr(analysis_tab, "model_available", fake_model_available)

    result = render_analysis(config, TAB_VALUE, reader=lambda path: complete_view())
    button = nodes_with(result, "id", "nut-du-doan")[0]

    assert len(calls) == 1
    assert props(button).get("disabled") is not True


def test_render_analysis_without_a_model_disables_the_button(config):
    result = render_analysis(config, TAB_VALUE, reader=lambda path: complete_view())
    button = nodes_with(result, "id", "nut-du-doan")[0]

    assert props(button).get("disabled") is True
