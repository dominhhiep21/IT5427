"""Báo cáo v3: mười một trường, chín khoá, đọc v2 ra `loi`, một đường dựng duy nhất (BR2.7)."""

from __future__ import annotations

import json


from src.analytics.model import build_model_block
from src.analytics.report import (
    REPORT_VERSION,
    STATUS_ERROR,
    assemble_report,
    read_report,
    report_path,
    write_report,
)

SPLIT = {
    "train_start": "2018-01-01",
    "train_end": "2018-02-01",
    "test_start": "2018-02-02",
    "test_end": "2018-03-01",
    "train_n": 10,
    "test_n": 5,
}
COHORTS = {
    "cohort_rows": 110195,
    "cohort_orders": 96476,
    "late_rows": 8713,
    "excluded_missing_carrier": 2,
}


def _model():
    return build_model_block(
        SPLIT, 0.68, 0.4, 0.5, 0.4, 2, auc_tree=0.61, baseline_auc=0.55, cohort_counts=COHORTS
    )


def test_report_version_is_three() -> None:
    assert REPORT_VERSION == 3


def test_model_block_round_trips_through_the_file(config) -> None:  # noqa: ANN001
    report = assemble_report(config, stats=None, model=_model(), generated_at="2026-11-13T00:00:00Z")
    write_report(config, report)

    view = read_report(report_path(config))
    assert view.status != STATUS_ERROR
    assert view.report is not None
    block = view.report.model
    assert block is not None
    assert len(block.to_dict()) == 11
    assert len(block.counts) == 9


def test_old_version_is_an_error_not_a_crash(config) -> None:  # noqa: ANN001
    path = report_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"version": 2, "generated_at": "2026-11-12T00:00:00Z", "stats": None, "model": None}),
        encoding="utf-8",
    )

    view = read_report(path)
    assert view.status == STATUS_ERROR
    assert "version" in view.message or "phiên bản" in view.message


def test_missing_new_field_is_an_error(config) -> None:  # noqa: ANN001
    report = assemble_report(config, stats=None, model=_model(), generated_at="2026-11-13T00:00:00Z")
    payload = report.to_dict()
    payload["model"].pop("auc_tree")
    path = report_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")

    view = read_report(path)
    assert view.status == STATUS_ERROR


def test_missing_counts_key_is_an_error(config) -> None:  # noqa: ANN001
    report = assemble_report(config, stats=None, model=_model(), generated_at="2026-11-13T00:00:00Z")
    payload = report.to_dict()
    payload["model"]["counts"].pop("excluded_missing_carrier")
    path = report_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")

    view = read_report(path)
    assert view.status == STATUS_ERROR


def test_assemble_report_keeps_the_previous_model_block(config) -> None:  # noqa: ANN001
    first = assemble_report(config, stats=None, model=_model(), generated_at="2026-11-13T00:00:00Z")
    write_report(config, first)

    second = assemble_report(config, stats=None, model=None, generated_at="2026-11-13T01:00:00Z")
    assert second.model is not None
    assert second.model.auc == first.model.auc
    assert second.generated_at != first.generated_at


def test_only_one_place_builds_the_report() -> None:
    """ADR-008 — `AnalysisReport(` chỉ xuất hiện trong `report.py`."""
    from pathlib import Path

    offenders = []
    for path in Path("src").rglob("*.py"):
        if path.name == "report.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "AnalysisReport(" in text and "def " in text:
            offenders.append(str(path))
    assert offenders == []


def test_split_keeps_the_six_v2_keys(config) -> None:  # noqa: ANN001
    report = assemble_report(config, stats=None, model=_model(), generated_at="2026-11-13T00:00:00Z")
    assert set(report.model.split) == {
        "train_start",
        "train_end",
        "test_start",
        "test_end",
        "train_n",
        "test_n",
    }
