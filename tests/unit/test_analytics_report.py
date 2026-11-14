"""Unit test cho khung báo cáo ở `src/analytics/report.py` (BR1.8–BR1.11)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.analytics import report as report_module
from src.analytics.report import (
    CORRELATION_DIGITS,
    INTERVAL_DIGITS,
    P_VALUE_DIGITS,
    RATE_DIGITS,
    REPORT_VERSION,
    AnalysisReport,
    ComparisonResult,
    CorrelationResult,
    GroupTestResult,
    ModelBlock,
    ProportionResult,
    ReportError,
    SeasonalResult,
    SkipEntry,
    StatsBlock,
    read_report,
    report_path,
    write_report,
)
from src.common.kpis import REVENUE_DEFINITION

STAMP = "2026-11-10T00:00:00+00:00"


def make_stats() -> StatsBlock:
    """Một `StatsBlock` đủ năm phép, dùng lại cho các ca đọc và ghi."""

    return StatsBlock(
        generated_at=STAMP,
        alpha=0.05,
        confidence=0.95,
        late_rate=ProportionResult(
            successes=7826,
            total=96478,
            rate=0.081117246,
            ci_low=0.07941234567,
            ci_high=0.08287654321,
        ),
        comparisons=[
            ComparisonResult(
                first="AL",
                second="SP",
                difference=0.123456789,
                z=12.3456789,
                p_value=0.000123456,
                ci_low=0.1001234,
                ci_high=0.1509876,
                significant=True,
                excluded=3500,
            )
        ],
        correlation=CorrelationResult(r=0.3456789, n=112650, ci_low=0.3301234, ci_high=0.3609876),
        group_test=GroupTestResult(
            test="chi_square_region_late",
            statistic=42.123456,
            p_value=0.000012345,
            dof=4,
            min_expected=123.45678,
        ),
        seasonal=SeasonalResult(
            revenue_definition=REVENUE_DEFINITION,
            method="classical_additive_12",
            period=12,
            months=["2020-01", "2020-02"],
            observed=[1000.125678, 2000.0],
            trend=[900.0, 1900.0],
            seasonal=[50.0, 50.0],
            residual=[50.125678, 50.0],
        ),
        skipped=[SkipEntry("correlation", "chưa đủ bốn dòng hàng")],
    )


def make_report(stats: StatsBlock | None = None, model: ModelBlock | None = None) -> AnalysisReport:
    return AnalysisReport(
        version=REPORT_VERSION,
        generated_at=STAMP,
        stats=make_stats() if stats is None else stats,
        model=model,
    )


def write_payload(path: Path, payload) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def test_report_path_comes_from_app_config(config):
    assert report_path(config) == Path(config.reports_dir) / "analysis.json"


def test_read_missing_file_is_empty_not_an_error(tmp_path):
    view = read_report(tmp_path / "analysis.json")

    assert view.status == "rong"
    assert view.report is None
    assert view.missing == ()
    assert "run --stage stats" in view.message


def test_read_unparseable_file_is_an_error_naming_the_path(tmp_path):
    path = tmp_path / "analysis.json"
    path.write_text("{hỏng", encoding="utf-8")

    view = read_report(path)

    assert view.status == "loi"
    assert view.report is None
    assert "analysis.json" in view.message


def test_read_json_that_is_not_an_object_is_an_error(tmp_path):
    path = write_payload(tmp_path / "analysis.json", [{"version": REPORT_VERSION}])

    view = read_report(path)

    assert view.status == "loi"
    assert view.report is None
    assert "đối tượng" in view.message


def test_read_version_one_asks_for_a_rerun_before_checking_fields(tmp_path):
    path = write_payload(tmp_path / "analysis.json", {"version": 1})

    view = read_report(path)

    assert view.status == "loi"
    assert "1" in view.message and str(REPORT_VERSION) in view.message
    assert "run --stage stats" in view.message
    assert "generated_at" not in view.message


def test_read_missing_required_field_names_the_field(tmp_path):
    path = write_payload(tmp_path / "analysis.json", {"version": REPORT_VERSION})

    view = read_report(path)

    assert view.status == "loi"
    assert "generated_at" in view.message


def test_read_wrong_field_type_is_an_error(tmp_path):
    payload = {
        "version": REPORT_VERSION,
        "generated_at": 20261110,
        "stats": None,
        "model": None,
    }
    path = write_payload(tmp_path / "analysis.json", payload)

    view = read_report(path)

    assert view.status == "loi"
    assert "generated_at" in view.message


def test_read_broken_seasonal_lengths_is_an_error(tmp_path):
    payload = make_report().to_dict()
    payload["stats"]["seasonal"]["observed"] = [1.0]
    path = write_payload(tmp_path / "analysis.json", payload)

    view = read_report(path)

    assert view.status == "loi"
    assert "observed" in view.message


def test_read_stats_only_is_partial(config, writer):
    write_report(config, make_report())

    view = read_report(report_path(config))

    assert view.status == "mot-phan"
    assert view.missing == ("model",)
    assert view.report is not None
    assert view.report.stats is not None


MODEL_STUB = ModelBlock(
    target="is_late",
    split={
        "train_start": "2017-01-01",
        "train_end": "2018-03-31",
        "test_start": "2018-04-01",
        "test_end": "2018-08-01",
        "train_n": 10,
        "test_n": 4,
    },
    auc=0.68,
    threshold=0.4,
    precision=0.5,
    recall=0.4,
    counts={
        "flagged": 2,
        "not_flagged": 2,
        "total": 4,
        "threshold_method": "max_f1_on_test_grid005",
        "auc_below_target": True,
        "cohort_rows": 110195,
        "cohort_orders": 96476,
        "late_rows": 8713,
        "excluded_missing_carrier": 2,
    },
    unit="dòng hàng",
    auc_tree=0.61,
    baseline_auc=0.55,
    beats_baseline=True,
)


def test_read_model_only_is_partial(config, writer):
    report = AnalysisReport(
        version=REPORT_VERSION,
        generated_at=STAMP,
        stats=None,
        model=MODEL_STUB,
    )
    write_report(config, report)

    view = read_report(report_path(config))

    assert view.status == "mot-phan"
    assert view.missing == ("stats",)
    assert view.report.model.target == "is_late"


def test_read_complete_report_has_both_blocks_and_no_message(config, writer):
    write_report(config, make_report(model=MODEL_STUB))

    view = read_report(report_path(config))

    assert view.status == "day-du"
    assert view.missing == ()
    assert view.message == ""
    assert view.report.stats.late_rate.successes == 7826
    assert view.report.stats.comparisons[0].first == "AL"


def test_write_then_read_round_trip_keeps_every_block(config, writer):
    path = write_report(config, make_report(model=MODEL_STUB))
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path == report_path(config)
    assert payload["version"] == REPORT_VERSION
    assert payload["stats"]["alpha"] == 0.05
    assert payload["stats"]["confidence"] == 0.95
    assert [entry["test"] for entry in payload["stats"]["skipped"]] == ["correlation"]


def test_write_rounds_numbers_to_the_agreed_digits(config, writer):
    path = write_report(config, make_report())
    stats = json.loads(path.read_text(encoding="utf-8"))["stats"]

    assert stats["late_rate"]["rate"] == round(0.081117246, RATE_DIGITS)
    assert stats["late_rate"]["ci_low"] == round(0.07941234567, INTERVAL_DIGITS)
    assert stats["comparisons"][0]["p_value"] == round(0.000123456, P_VALUE_DIGITS)
    assert stats["correlation"]["r"] == round(0.3456789, CORRELATION_DIGITS)
    assert stats["seasonal"]["observed"][0] == round(1000.125678, RATE_DIGITS)


def test_write_without_a_writer_builds_its_own(config):
    path = write_report(config, make_report())

    assert path.exists()
    assert read_report(path).status == "mot-phan"


def test_write_refuses_a_payload_without_any_block(config, writer):
    report = AnalysisReport(version=REPORT_VERSION, generated_at=STAMP)

    with pytest.raises(ReportError) as caught:
        write_report(config, report, writer)

    assert "rỗng" in str(caught.value)
    assert not report_path(config).exists()
    assert list(Path(writer.run.temp_dir).glob("*.pending")) == []


def test_write_failure_keeps_the_previous_file_and_leaves_no_temp(config, writer, monkeypatch):
    first = write_report(config, make_report())
    original = first.read_text(encoding="utf-8")
    verify = report_module._verify_pending

    def corrupt_then_verify(path):
        Path(path).write_text("{hỏng", encoding="utf-8")
        verify(path)

    monkeypatch.setattr(report_module, "_verify_pending", corrupt_then_verify)

    with pytest.raises(ReportError):
        write_report(config, make_report(stats=make_stats()), writer)

    assert first.read_text(encoding="utf-8") == original
    assert list(Path(writer.run.temp_dir).glob("*.pending")) == []


def test_verification_rejects_a_wrong_version(tmp_path):
    pending = tmp_path / "pending.json"
    write_payload(pending, {"version": 1, "generated_at": STAMP, "stats": {"a": 1}, "model": None})

    with pytest.raises(ReportError) as caught:
        report_module._verify_pending(pending)

    assert "phiên bản" in str(caught.value)
