"""Dashboard layout smoke tests (no browser)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from dash import dcc

from src.config import load_config
from src.dashboard import app as app_module
from src.dashboard.app import (
    build_dashboard_outputs,
    create_app,
    reset_integration_logs,
)
from src.integration.tab import SCREENS


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


def _props(node) -> dict:
    return node.to_plotly_json().get("props", {})


def _tabs(app):
    return [child for child in app.layout.children if isinstance(child, dcc.Tabs)][0]


def _tab(tabs, value):
    """Tra tab theo `value` — danh tính của tab, không phải vị trí trong `children`.

    Tab thứ năm làm `children[-1]` trỏ sang tab mới, nên mọi chỗ đọc tab phải tra theo giá trị.
    """

    found = [child for child in tabs.children if isinstance(child, dcc.Tab) and child.value == value]
    assert len(found) == 1, f"không thấy đúng một tab {value!r}"
    return found[0]


def test_dashboard_builds_with_five_tabs():
    app = create_app(load_config())
    tabs = _tabs(app)
    assert len(tabs.children) == 5
    assert _tab(tabs, "tich-hop").label == "Tích hợp"
    assert _tab(tabs, "phan-tich").label == "Kết quả phân tích"
    # Hai callback của ba tab báo cáo + sáu callback của tab "Tích hợp" (năm của U6,
    # một của vùng `don-theo-thang` — C9 `result_region_ids`) + một của tab "Kết quả phân tích"
    # + một của khối Dự đoán (BR3.13: mười callback, Output của callback KPI vẫn chín).
    assert len(app.callback_map) == 10


def test_integration_tab_holds_four_empty_cards():
    app = create_app(load_config())
    tabs = _tabs(app)
    loading = _tab(tabs, "tich-hop").children
    nodes = list(_walk(loading))

    cards = [node for node in nodes if _props(node).get("data-testid") == "integration-card"]
    assert len(cards) == 4
    assert {_props(card).get("data-state") for card in cards} == {"rong"}

    ids = {_props(node).get("id") for node in nodes}
    assert {"overview-cards", "screen-body", "reload-token", "don-theo-thang"} <= ids
    assert "doanh_thu_theo_thang" not in ids
    assert not [node for node in nodes if _props(node).get("data-testid") == "back-to-overview"]


def test_screen_action_buttons_use_pattern_matching_ids():
    """Nút "Quay lại"/"Tải lại" chỉ tồn tại trong màn hình chi tiết, nên callback phải nhận
    chúng bằng pattern-matching id. Nếu dùng id cố định `back-<screen>`, Dash báo
    "nonexistent object" ngay khi tải trang và cả bốn nút "Xem chi tiết" không mở được màn hình
    (lỗi thật gặp 2026-11-09, chỉ hiện trên trình duyệt).
    """

    app = create_app(load_config())
    detail_ids = {f"back-{screen}" for screen in SCREENS} | {f"reload-{screen}" for screen in SCREENS}

    fixed_ids = [
        item["id"]
        for entry in app.callback_map.values()
        for item in entry["inputs"]
        if isinstance(item["id"], str) and item["id"] in detail_ids
    ]

    assert fixed_ids == []


def test_integration_tab_holds_the_thin_slice_region():
    """C9 `result_region_ids`: vùng số liệu của lát cắt nằm trong tab, không phải một card_id."""

    app = create_app(load_config())
    tabs = _tabs(app)
    nodes = list(_walk(_tab(tabs, "tich-hop").children))

    region = [node for node in nodes if _props(node).get("data-testid") == "don-theo-thang"]
    assert len(region) == 1
    assert "Chưa chạy truy vấn lần nào" in str(region[0])


def test_dashboard_outputs_with_real_data():
    outputs = build_dashboard_outputs(load_config(), {})
    assert len(outputs) == 9
    assert outputs[0] is not None
    assert outputs[1] is not None


def test_dashboard_all_status_filter():
    outputs = build_dashboard_outputs(load_config(), {"order_status": "all"})
    assert "15.843.553,24" in str(outputs[0])
    assert "99.441" in str(outputs[0])


def test_dashboard_empty_period_does_not_crash():
    outputs = build_dashboard_outputs(
        load_config(),
        {"start_date": "2019-01-01", "end_date": "2019-12-31"},
    )
    assert len(outputs) == 9
    assert outputs[0] is not None


def test_dashboard_outputs_error_state():
    config = replace(load_config(), duckdb_path=Path("missing.duckdb"))
    outputs = build_dashboard_outputs(config, {})
    assert "error-banner" in outputs[0].className


def test_integration_logger_appends_to_the_newest_pipeline_log(tmp_path: Path):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    older = logs_dir / "20260101T000000-aaaaaaaa.jsonl"
    newer = logs_dir / "20260102T000000-bbbbbbbb.jsonl"
    older.write_text("{}\n", encoding="utf-8")
    newer.write_text("{}\n", encoding="utf-8")
    import os

    os.utime(older, (1_700_000_000, 1_700_000_000))
    os.utime(newer, (1_800_000_000, 1_800_000_000))
    config = replace(load_config(), logs_dir=logs_dir)
    reset_integration_logs()

    logger = app_module._integration_logger(config)

    assert logger.run.log_path == newer
    assert logger.run.stage == "integration"


def test_integration_logger_opens_its_own_file_without_pipeline_log(tmp_path: Path):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    config = replace(load_config(), logs_dir=logs_dir)
    reset_integration_logs()

    logger = app_module._integration_logger(config)
    logger.warning("probe")

    assert logger.run.log_path.name.startswith("integration-")
    events = [
        json.loads(line)
        for line in logger.run.log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(event["event"] == "integration.log.no_pipeline_run" for event in events)
