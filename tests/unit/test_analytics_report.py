"""Báo cáo Markdown, định dạng số và CLI của phần phân tích."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from src.analytics import __main__ as cli
from src.analytics import insights
from src.analytics.connection import open_analysis_connection
from src.analytics.formatting import (
    fmt_int,
    fmt_money,
    fmt_num,
    fmt_p_value,
    fmt_pct,
    fmt_signed_pct,
    to_markdown,
)
from src.analytics.report import (
    ANALYSIS_REPORT_NAME,
    RECONCILIATION_REPORT_NAME,
    build_analysis_report,
    build_reconciliation_report,
    run_bundle,
    write_outputs,
)
from tests.unit.analytics_marts import build_small_marts, write_small_warehouse
from tests.unit.test_analytics_reconciliation import SMALL_BASELINE


@pytest.fixture
def bundle(config):
    write_small_warehouse(config)
    conn = open_analysis_connection(config)
    try:
        yield run_bundle(conn, SMALL_BASELINE)
    finally:
        conn.close()


def test_vietnamese_number_formats():
    assert fmt_int(15419773) == "15.419.773"
    assert fmt_num(15419773.75) == "15.419.773,75"
    assert fmt_money(159.83) == "159,83 BRL"
    assert fmt_pct(8.11) == "8,11%"
    assert fmt_signed_pct(143.357) == "+143,36%"
    assert fmt_signed_pct(-4.1) == "-4,10%"
    assert fmt_p_value(0.0) == "< 0,001"
    assert fmt_p_value(0.2615) == "0,262"
    assert [fmt_int(None), fmt_num(float("nan")), fmt_money(pd.NA), fmt_pct(None)] == ["–"] * 4


def test_to_markdown_aligns_and_formats_by_type():
    frame = pd.DataFrame(
        {
            "name": ["a|b", None],
            "orders": [1234, 5],
            "share_pct": [12.5, float("nan")],
            "flag": [True, False],
            "hidden": [1, 2],
        }
    )
    lines = to_markdown(
        frame, {"name": "Tên", "orders": "Số đơn", "share_pct": "Tỷ trọng", "flag": "Cờ"}
    ).splitlines()
    assert lines[0] == "| Tên | Số đơn | Tỷ trọng | Cờ |"
    assert lines[1] == "| --- | ---: | ---: | ---: |"
    assert lines[2] == "| a\\|b | 1.234 | 12,50 | có |"
    assert lines[3] == "| – | 5 | – | không |"
    assert len(to_markdown(frame, limit=1).splitlines()) == 3


def test_analysis_report_covers_every_task_and_analysis(bundle):
    text = build_analysis_report(bundle)
    for task, title in insights.TASK_TITLES.items():
        assert f"## Mục {task} — {title}" in text
    for item in insights.ANALYSES.values():
        # Bảng chéo không có mục riêng: nó là đầu vào của mục kiểm định chi-bình-phương.
        if item.key != "review_late_contingency":
            assert f"### {item.title}" in text
    assert "### Kiểm định chi-bình-phương về tính độc lập" in text
    assert text.count("<details><summary>Câu SQL</summary>") == len(insights.ANALYSES)
    assert "529,00 BRL" in text
    assert "105,80 BRL" in text
    assert "không kết luận" in text
    assert "nan" not in text.lower().replace("nhân", "")


def test_analysis_report_wording_follows_the_data(bundle):
    text = build_analysis_report(bundle)
    # Bộ dữ liệu nhỏ không rơi vào ngày Black Friday và không có danh mục nào đủ 500 đơn.
    assert "Black Friday" not in text
    assert "Không có danh mục nào đạt ngưỡng 500 đơn." in text
    # Cột 3 sao rỗng nên kiểm định chỉ còn 3 bậc tự do và không đủ bằng chứng bác bỏ H0.
    assert bundle.chi_square.dof == 3
    assert "chưa đủ cơ sở bác bỏ H0" in text


def test_reconciliation_report_lists_every_check(bundle):
    text = build_reconciliation_report(bundle.reconciliation)
    assert "**Kết luận: ĐẠT.** 8 kiểm tra đạt, 0 không đạt, 9 mục ghi nhận, 0 bỏ qua." in text
    for check in bundle.reconciliation.checks:
        assert f"### {check.check_id} — {check.title}" in text
    assert "| `naive_join_revenue` | 694,00 |" in text


def test_reconciliation_report_flags_failure(config):
    marts = build_small_marts()
    items = marts["fact_order_items"]
    marts["fact_order_items"] = pd.concat([items, items.iloc[[0]]], ignore_index=True)
    write_small_warehouse(config, marts)
    conn = open_analysis_connection(config)
    try:
        failing = run_bundle(conn, SMALL_BASELINE)
    finally:
        conn.close()
    assert "**Kết luận: KHÔNG ĐẠT.**" in build_reconciliation_report(failing.reconciliation)
    assert "CÓ KIỂM TRA KHÔNG ĐẠT" in build_analysis_report(failing)


def test_write_outputs_creates_reports_and_tables(bundle, tmp_path):
    paths = write_outputs(bundle, tmp_path / "reports", tmp_path / "docs")
    assert paths["analysis_report"] == tmp_path / "docs" / ANALYSIS_REPORT_NAME
    assert paths["reconciliation_report"] == tmp_path / "docs" / RECONCILIATION_REPORT_NAME
    assert all(path.exists() for path in paths.values())

    output_dir = tmp_path / "reports" / "analysis"
    assert {path.stem for path in output_dir.glob("*.csv")} == set(insights.ANALYSES)
    summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
    assert summary["kpi_headline"]["revenue"] == 529.0
    assert summary["reconciliation"]["passed"] is True
    assert json.loads(paths["reconciliation_json"].read_text(encoding="utf-8"))["counts"]["pass"] == 8
    # Báo cáo ghi bằng LF để diff trong git không phụ thuộc hệ điều hành.
    assert b"\r\n" not in paths["analysis_report"].read_bytes()


def test_cli_list_needs_no_data(capsys):
    assert cli.main(["--list"]) == 0
    output = capsys.readouterr().out
    assert "monthly_trend" in output
    assert "mục 20" in output


def test_cli_modes_on_small_warehouse(config, tmp_path, monkeypatch, capsys):
    write_small_warehouse(config)
    monkeypatch.setattr(cli, "load_config", lambda: config)

    assert cli.main(["--show", "customer_repeat"]) == 0
    assert "Khách hàng mua lại" in capsys.readouterr().out

    assert cli.main(["--show", "khong_co"]) == 1
    assert "Không có phân tích" in capsys.readouterr().err

    # Baseline mặc định là của bộ Olist đầy đủ nên bộ dữ liệu nhỏ phải bị chặn ở DS-08.
    assert cli.main(["--check"]) == 1
    assert "KHÔNG ĐẠT" in capsys.readouterr().out

    assert cli.main(["--docs-dir", str(tmp_path / "docs")]) == 1
    assert (tmp_path / "docs" / ANALYSIS_REPORT_NAME).exists()
    assert (config.reports_dir / "analysis" / "summary.json").exists()


def test_cli_reports_missing_marts(config, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", lambda: config)
    assert cli.main([]) == 1
    assert "Thiếu mart" in capsys.readouterr().err
