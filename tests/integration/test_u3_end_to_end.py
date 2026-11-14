"""End-to-end U3 tests: CLI stage, replay batch, dashboard layout."""

from __future__ import annotations

from pathlib import Path

import pytest
from dash import dcc

from src.analytics.report import read_report, report_path
from src.analytics.model import AUC_TARGET
from src.analytics.service import AnalyticsService
from src.clean.pipeline import clean_all
from src.common.io import AtomicWriter
from src.common.logging import JsonLogger, new_run_context
from src.common.types import KpiFilters
from src.dashboard.analysis_tab import SECTION_IDS, TAB_VALUE, render_analysis
from src.dashboard.app import create_app
from src.dashboard.formatting import format_number
from src.ingest.reader import ingest_all
from src.integrate.pipeline import integrate_all
from src.pipeline.micro_batch import process_inbox
from src.pipeline.replay import generate
from src.pipeline.stages import run_stage


def _visible_text(node) -> str:
    """Mọi chuỗi hiển thị trong cây thành phần."""

    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, (list, tuple)):
        return " ".join(_visible_text(child) for child in node)
    children = getattr(node, "children", None)
    return _visible_text(children) if children is not None else ""


def _walk(node):
    yield node
    children = getattr(node, "children", None)
    if children is None:
        return
    if isinstance(children, (list, tuple)):
        for child in children:
            if child is not None and not isinstance(child, str):
                yield from _walk(child)
    elif not isinstance(children, (str, int, float)):
        yield from _walk(children)


def _props(node) -> dict:
    return node.to_plotly_json().get("props", {})


@pytest.mark.slow
def test_u3_end_to_end(real_config, tmp_path: Path):
    run = new_run_context("u3-setup", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)
    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    integrate_all(real_config, run, writer, logger)

    summary = run_stage(real_config, "analyze")
    assert summary.success

    replay_dir = tmp_path / "replay"
    batches = generate(real_config, batches=1, target_dir=replay_dir)
    assert len(batches) == 1
    results = process_inbox(real_config, replay_dir)
    assert results
    assert all(result.status in {"success", "skipped"} for result in results)

    service = AnalyticsService(real_config)
    kpi = service.kpi_summary(KpiFilters())
    assert kpi["revenue"] == 15_419_773.75
    assert kpi["orders"] == 96_478

    app = create_app(real_config)
    assert app.title == "Olist | Bảng điều hành"
    # Hai callback của ba tab báo cáo + sáu callback của tab "Tích hợp" (năm của U6 + một của vùng
    # `don-theo-thang`) + một callback của tab "Kết quả phân tích" + một callback của khối Dự đoán
    # (BR3.13: mười callback; Output của callback KPI vẫn chín).
    assert len(app.callback_map) == 10

    tabs = [child for child in app.layout.children if isinstance(child, dcc.Tabs)][0]
    values = {tab.value for tab in tabs.children if isinstance(tab, dcc.Tab)}
    assert len(tabs.children) == 5
    assert {"tich-hop", TAB_VALUE} <= values

    writer.cleanup()


@pytest.mark.slow
def test_u3_analysis_tab_renders_the_real_report(real_config):
    """Tab thứ năm đọc báo cáo thật của tầng `stats` — dựng đủ ba khối, AUC thật dưới mốc 0,70."""

    run = new_run_context("u3-display", real_config.logs_dir, real_config.temp_dir)
    writer = AtomicWriter(run, real_config.parquet_compression)
    logger = JsonLogger(run, console=False)
    raw, _ = ingest_all(real_config, run, writer, logger)
    clean_all(raw, real_config, run, writer, logger)
    integrate_all(real_config, run, writer, logger)

    assert run_stage(real_config, "stats").success
    view = read_report(report_path(real_config))
    assert view.status == "day-du"

    panel = render_analysis(real_config, TAB_VALUE)
    text = _visible_text(panel)

    sections = [_props(node).get("data-section") for node in _walk(panel) if "data-section" in _props(node)]
    assert sections == list(SECTION_IDS)
    assert "8,11%" in text
    assert "96.478" in text
    assert "7.826" in text
    # Chỉ số mô hình đọc từ báo cáo, không ghim một AUC cụ thể vào test (mốc sàn thuộc U3).
    assert format_number(view.report.model.auc, 4) in text
    # Nhãn thẻ AUC nêu mốc đang áp lấy từ `AUC_TARGET`, không phải literal "0,70" (BR3.28).
    assert f"không đạt mốc {format_number(AUC_TARGET, 2)}" in text
    assert "0,4000" not in text

    writer.cleanup()
