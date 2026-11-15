"""Khung báo cáo dùng chung C1/C2: kiểu dữ liệu, ghi nguyên tử và đọc bốn trạng thái (BR1.8–BR1.11)."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from src.common.exceptions import PipelineError
from src.common.io import AtomicWriter
from src.common.logging import new_run_context

REPORT_VERSION = 3
REPORT_FILE_NAME = "analysis.json"

# Thang đo: tỉ lệ trong báo cáo là phân số 0–1, khác `late_rate_pct` 0–100 của KPI hiện có.
RATE_DIGITS = 4
P_VALUE_DIGITS = 4
INTERVAL_DIGITS = 4
STATISTIC_DIGITS = 4
CORRELATION_DIGITS = 3

STATUS_EMPTY = "rong"
STATUS_COMPLETE = "day-du"
STATUS_PARTIAL = "mot-phan"
STATUS_ERROR = "loi"
STATUSES = (STATUS_EMPTY, STATUS_COMPLETE, STATUS_PARTIAL, STATUS_ERROR)

BLOCK_NAMES = ("stats", "model")
RUN_STATS_HINT = "python -X utf8 -m src.pipeline run --stage stats"


class ReportError(PipelineError):
    """Báo cáo không ghi được hoặc tệp vừa ghi không đọc lại được (BR1.11)."""


@dataclass(frozen=True)
class SkipEntry:
    """Một kiểm định không chạy được, kèm lý do."""

    test: str
    reason: str

    def to_dict(self) -> dict:
        return {"test": self.test, "reason": self.reason}


@dataclass(frozen=True)
class ProportionResult:
    """Một tỉ lệ kèm khoảng tin cậy Wilson (BR1.1)."""

    successes: int
    total: int
    rate: float
    ci_low: float
    ci_high: float

    def to_dict(self) -> dict:
        return {
            "successes": self.successes,
            "total": self.total,
            "rate": _round(self.rate, RATE_DIGITS),
            "ci_low": _round(self.ci_low, INTERVAL_DIGITS),
            "ci_high": _round(self.ci_high, INTERVAL_DIGITS),
        }


@dataclass(frozen=True)
class ComparisonResult:
    """So sánh hai tỉ lệ giữa hai bang, kèm số đơn không tham gia được (BR1.2)."""

    first: str
    second: str
    difference: float
    z: float
    p_value: float
    ci_low: float
    ci_high: float
    significant: bool
    excluded: int

    def to_dict(self) -> dict:
        return {
            "first": self.first,
            "second": self.second,
            "difference": _round(self.difference, RATE_DIGITS),
            "z": _round(self.z, STATISTIC_DIGITS),
            "p_value": _round(self.p_value, P_VALUE_DIGITS),
            "ci_low": _round(self.ci_low, INTERVAL_DIGITS),
            "ci_high": _round(self.ci_high, INTERVAL_DIGITS),
            "significant": self.significant,
            "excluded": self.excluded,
        }


@dataclass(frozen=True)
class CorrelationResult:
    """Tương quan Pearson giữa giá hàng và phí vận chuyển, khoảng Fisher (BR1.3)."""

    r: float
    n: int
    ci_low: float
    ci_high: float

    def to_dict(self) -> dict:
        return {
            "r": _round(self.r, CORRELATION_DIGITS),
            "n": self.n,
            "ci_low": _round(self.ci_low, INTERVAL_DIGITS),
            "ci_high": _round(self.ci_high, INTERVAL_DIGITS),
        }


@dataclass(frozen=True)
class GroupTestResult:
    """Kết quả một phép kiểm định nhóm trên bảng dự phòng (BR1.4)."""

    test: str
    statistic: float
    p_value: float
    dof: int
    min_expected: float

    def to_dict(self) -> dict:
        return {
            "test": self.test,
            "statistic": _round(self.statistic, STATISTIC_DIGITS),
            "p_value": _round(self.p_value, P_VALUE_DIGITS),
            "dof": self.dof,
            "min_expected": _round(self.min_expected, STATISTIC_DIGITS),
        }


@dataclass(frozen=True)
class SeasonalResult:
    """Phân rã mùa vụ chuỗi doanh thu theo tháng (BR1.5)."""

    revenue_definition: str
    method: str
    period: int
    months: list[str]
    observed: list[float]
    trend: list[float]
    seasonal: list[float]
    residual: list[float]

    def to_dict(self) -> dict:
        return {
            "revenue_definition": self.revenue_definition,
            "method": self.method,
            "period": self.period,
            "months": list(self.months),
            "observed": [_round(value, RATE_DIGITS) for value in self.observed],
            "trend": [_round(value, RATE_DIGITS) for value in self.trend],
            "seasonal": [_round(value, RATE_DIGITS) for value in self.seasonal],
            "residual": [_round(value, RATE_DIGITS) for value in self.residual],
        }


@dataclass(frozen=True)
class StatsBlock:
    """Toàn bộ kết quả kiểm định thống kê của một lần chạy."""

    generated_at: str
    alpha: float
    confidence: float
    late_rate: ProportionResult
    comparisons: list[ComparisonResult] = field(default_factory=list)
    correlation: CorrelationResult | None = None
    group_test: GroupTestResult | None = None
    seasonal: SeasonalResult | None = None
    skipped: list[SkipEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "alpha": _round(self.alpha, INTERVAL_DIGITS),
            "confidence": _round(self.confidence, INTERVAL_DIGITS),
            "late_rate": self.late_rate.to_dict(),
            "comparisons": [item.to_dict() for item in self.comparisons],
            "correlation": None if self.correlation is None else self.correlation.to_dict(),
            "group_test": None if self.group_test is None else self.group_test.to_dict(),
            "seasonal": None if self.seasonal is None else self.seasonal.to_dict(),
            "skipped": [item.to_dict() for item in self.skipped],
        }


@dataclass(frozen=True)
class ModelBlock:
    """Khối mô hình do U2 sở hữu; U1 chỉ giữ nguyên nội dung khi ghi lại tệp.

    Phiên bản 3: bảy trường của v2 giữ nguyên tên và nghĩa, thêm `unit`, `auc_tree`,
    `baseline_auc`, `beats_baseline` — mười một trường; `counts` có chín khoá.
    """

    target: str = ""
    split: dict = field(default_factory=dict)
    auc: float = 0.0
    threshold: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    counts: dict = field(default_factory=dict)
    unit: str = ""
    auc_tree: float = 0.0
    baseline_auc: float = 0.0
    beats_baseline: bool = False

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "split": dict(self.split),
            "auc": self.auc,
            "threshold": self.threshold,
            "precision": self.precision,
            "recall": self.recall,
            "counts": dict(self.counts),
            "unit": self.unit,
            "auc_tree": self.auc_tree,
            "baseline_auc": self.baseline_auc,
            "beats_baseline": self.beats_baseline,
        }


@dataclass(frozen=True)
class AnalysisReport:
    """Tệp báo cáo dùng chung, gốc của cả hai khối kết quả."""

    version: int
    generated_at: str
    stats: StatsBlock | None = None
    model: ModelBlock | None = None

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "stats": None if self.stats is None else self.stats.to_dict(),
            "model": None if self.model is None else self.model.to_dict(),
        }


@dataclass(frozen=True)
class ReportView:
    """Kết quả một lần đọc báo cáo, luôn có trạng thái."""

    status: str
    report: AnalysisReport | None = None
    missing: tuple[str, ...] = ()
    message: str = ""


def report_path(config) -> Path:
    """`data/reports/analysis.json`; đường dẫn lấy từ `AppConfig`, không nhận từ dòng lệnh (SEC-5)."""

    return Path(config.reports_dir) / REPORT_FILE_NAME


def assemble_report(
    config,
    *,
    stats: StatsBlock | None,
    model: ModelBlock | None,
    generated_at: str,
) -> AnalysisReport:
    """ADR-008 — nơi DUY NHẤT dựng `AnalysisReport`; giữ khối `model` cũ khi người gọi không truyền."""

    if model is None:
        previous = read_report(report_path(config))
        model = previous.report.model if previous.report is not None else None
    return AnalysisReport(
        version=REPORT_VERSION,
        generated_at=generated_at,
        stats=stats,
        model=model,
    )


def write_report(config, report: AnalysisReport, writer: AtomicWriter | None = None) -> Path:
    """Ghi tệp tạm, đọc lại kiểm cấu trúc, rồi mới thay tệp cũ (BR1.11)."""

    final_path = report_path(config)
    owned = writer is None
    writer = writer or _writer_for(config)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    pending = Path(writer.run.temp_dir) / f"{final_path.name}.{uuid.uuid4().hex}.pending"
    try:
        writer.write_json(report.to_dict(), pending)
        try:
            _verify_pending(pending)
        except Exception:
            pending.unlink(missing_ok=True)
            raise
        os.replace(pending, final_path)
    finally:
        if owned:
            writer.cleanup()
    return final_path


def read_report(path: Path) -> ReportView:
    """Đọc báo cáo theo thứ tự cố định: tồn tại → parse → phiên bản → trường → khối (BR1.9, BR1.10)."""

    path = Path(path)
    if not path.exists():
        return ReportView(
            STATUS_EMPTY,
            message=f"Chưa có báo cáo tại {path}; chạy `{RUN_STATS_HINT}` để sinh tệp.",
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return ReportView(STATUS_ERROR, message=f"Không đọc được báo cáo {path}: {exc}")
    if not isinstance(payload, dict):
        return ReportView(STATUS_ERROR, message=f"Báo cáo {path} không phải một đối tượng JSON.")
    version = payload.get("version")
    if isinstance(version, bool) or version != REPORT_VERSION:
        return ReportView(
            STATUS_ERROR,
            message=(
                f"Báo cáo {path} có phiên bản {version!r}, cần {REPORT_VERSION}; chạy lại `{RUN_STATS_HINT}`."
            ),
        )
    try:
        report = _parse_report(payload)
    except _ShapeError as exc:
        return ReportView(
            STATUS_ERROR,
            message=f"Báo cáo {path} hỏng ở trường {exc.field}: {exc.reason}",
        )
    missing = tuple(name for name in BLOCK_NAMES if getattr(report, name) is None)
    if missing:
        return ReportView(
            STATUS_PARTIAL,
            report=report,
            missing=missing,
            message=f"Báo cáo {path} còn thiếu khối {', '.join(missing)}.",
        )
    return ReportView(STATUS_COMPLETE, report=report)


def _writer_for(config) -> AtomicWriter:
    """`AtomicWriter` cho lần gọi không có run context của pipeline để mượn."""

    run = new_run_context("stats", Path(config.logs_dir), Path(config.temp_dir))
    return AtomicWriter(run, config.parquet_compression)


def _verify_pending(path: Path) -> None:
    """`write_json` không tự đọc lại: parse, kiểm phiên bản, kiểm hai khối không cùng null."""

    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReportError(f"kiểm lại {Path(path).name}: không đọc được tệp tạm ({exc})") from exc
    if not isinstance(payload, dict) or payload.get("version") != REPORT_VERSION:
        raise ReportError(f"kiểm lại {Path(path).name}: phiên bản ghi ra không phải {REPORT_VERSION}")
    if payload.get("stats") is None and payload.get("model") is None:
        raise ReportError(f"kiểm lại {Path(path).name}: cả khối stats lẫn model đều rỗng")


class _ShapeError(Exception):
    """Một trường của tệp báo cáo thiếu hoặc sai kiểu."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f"{field}: {reason}")
        self.field = field
        self.reason = reason


def _round(value: float, digits: int) -> float:
    return round(float(value), digits)


def _mapping(value: object, field: str) -> dict:
    if not isinstance(value, dict):
        raise _ShapeError(field, "thiếu hoặc không phải đối tượng")
    return value


def _number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _ShapeError(field, "thiếu hoặc không phải số")
    return float(value)


def _integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _ShapeError(field, "thiếu hoặc không phải số nguyên")
    return value


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise _ShapeError(field, "thiếu hoặc không phải chuỗi")
    return value


def _boolean(value: object, field: str) -> bool:
    if not isinstance(value, bool):
        raise _ShapeError(field, "thiếu hoặc không phải luận lý")
    return value


def _sequence(value: object, field: str) -> list:
    if not isinstance(value, list):
        raise _ShapeError(field, "thiếu hoặc không phải danh sách")
    return value


def _proportion(value: object, field: str) -> ProportionResult:
    block = _mapping(value, field)
    return ProportionResult(
        successes=_integer(block.get("successes"), f"{field}.successes"),
        total=_integer(block.get("total"), f"{field}.total"),
        rate=_number(block.get("rate"), f"{field}.rate"),
        ci_low=_number(block.get("ci_low"), f"{field}.ci_low"),
        ci_high=_number(block.get("ci_high"), f"{field}.ci_high"),
    )


def _comparison(value: object, field: str) -> ComparisonResult:
    block = _mapping(value, field)
    significant = block.get("significant")
    if not isinstance(significant, bool):
        raise _ShapeError(f"{field}.significant", "thiếu hoặc không phải giá trị đúng/sai")
    return ComparisonResult(
        first=_text(block.get("first"), f"{field}.first"),
        second=_text(block.get("second"), f"{field}.second"),
        difference=_number(block.get("difference"), f"{field}.difference"),
        z=_number(block.get("z"), f"{field}.z"),
        p_value=_number(block.get("p_value"), f"{field}.p_value"),
        ci_low=_number(block.get("ci_low"), f"{field}.ci_low"),
        ci_high=_number(block.get("ci_high"), f"{field}.ci_high"),
        significant=significant,
        excluded=_integer(block.get("excluded"), f"{field}.excluded"),
    )


def _correlation(value: object, field: str) -> CorrelationResult:
    block = _mapping(value, field)
    return CorrelationResult(
        r=_number(block.get("r"), f"{field}.r"),
        n=_integer(block.get("n"), f"{field}.n"),
        ci_low=_number(block.get("ci_low"), f"{field}.ci_low"),
        ci_high=_number(block.get("ci_high"), f"{field}.ci_high"),
    )


def _group_test(value: object, field: str) -> GroupTestResult:
    block = _mapping(value, field)
    return GroupTestResult(
        test=_text(block.get("test"), f"{field}.test"),
        statistic=_number(block.get("statistic"), f"{field}.statistic"),
        p_value=_number(block.get("p_value"), f"{field}.p_value"),
        dof=_integer(block.get("dof"), f"{field}.dof"),
        min_expected=_number(block.get("min_expected"), f"{field}.min_expected"),
    )


def _seasonal(value: object, field: str) -> SeasonalResult:
    block = _mapping(value, field)
    months = [_text(item, f"{field}.months") for item in _sequence(block.get("months"), f"{field}.months")]
    series = {}
    for name in ("observed", "trend", "seasonal", "residual"):
        values = [_number(item, f"{field}.{name}") for item in _sequence(block.get(name), f"{field}.{name}")]
        if len(values) != len(months):
            raise _ShapeError(f"{field}.{name}", "không cùng độ dài với months")
        series[name] = values
    return SeasonalResult(
        revenue_definition=_text(block.get("revenue_definition"), f"{field}.revenue_definition"),
        method=_text(block.get("method"), f"{field}.method"),
        period=_integer(block.get("period"), f"{field}.period"),
        months=months,
        observed=series["observed"],
        trend=series["trend"],
        seasonal=series["seasonal"],
        residual=series["residual"],
    )


def _skip(value: object, field: str) -> SkipEntry:
    block = _mapping(value, field)
    return SkipEntry(
        test=_text(block.get("test"), f"{field}.test"),
        reason=_text(block.get("reason"), f"{field}.reason"),
    )


def _optional(value: object, field: str, parse):
    return None if value is None else parse(value, field)


def _model_block(value: object, field: str) -> ModelBlock:
    """Đọc khối mô hình v3 theo đúng mười một trường C2 khai; thiếu trường là `loi`."""
    block = _mapping(value, field)
    counts = _mapping(block.get("counts"), f"{field}.counts")
    missing_counts = [
        key
        for key in (
            "flagged",
            "not_flagged",
            "total",
            "threshold_method",
            "auc_below_target",
            "cohort_rows",
            "cohort_orders",
            "late_rows",
            "excluded_missing_carrier",
        )
        if key not in counts
    ]
    if missing_counts:
        raise _ShapeError(f"{field}.counts", f"thiếu khoá: {', '.join(missing_counts)}")
    return ModelBlock(
        target=_text(block.get("target"), f"{field}.target"),
        split=_mapping(block.get("split"), f"{field}.split"),
        auc=_number(block.get("auc"), f"{field}.auc"),
        threshold=_number(block.get("threshold"), f"{field}.threshold"),
        precision=_number(block.get("precision"), f"{field}.precision"),
        recall=_number(block.get("recall"), f"{field}.recall"),
        counts=counts,
        unit=_text(block.get("unit"), f"{field}.unit"),
        auc_tree=_number(block.get("auc_tree"), f"{field}.auc_tree"),
        baseline_auc=_number(block.get("baseline_auc"), f"{field}.baseline_auc"),
        beats_baseline=_boolean(block.get("beats_baseline"), f"{field}.beats_baseline"),
    )


def _stats_block(value: object, field: str) -> StatsBlock:
    block = _mapping(value, field)
    return StatsBlock(
        generated_at=_text(block.get("generated_at"), f"{field}.generated_at"),
        alpha=_number(block.get("alpha"), f"{field}.alpha"),
        confidence=_number(block.get("confidence"), f"{field}.confidence"),
        late_rate=_proportion(block.get("late_rate"), f"{field}.late_rate"),
        comparisons=[
            _comparison(item, f"{field}.comparisons")
            for item in _sequence(block.get("comparisons"), f"{field}.comparisons")
        ],
        correlation=_optional(block.get("correlation"), f"{field}.correlation", _correlation),
        group_test=_optional(block.get("group_test"), f"{field}.group_test", _group_test),
        seasonal=_optional(block.get("seasonal"), f"{field}.seasonal", _seasonal),
        skipped=[
            _skip(item, f"{field}.skipped") for item in _sequence(block.get("skipped"), f"{field}.skipped")
        ],
    )


def _parse_report(payload: dict) -> AnalysisReport:
    version = _integer(payload.get("version"), "version")
    if version != REPORT_VERSION:
        raise _ShapeError("version", f"phải bằng {REPORT_VERSION}")
    stats = _optional(payload.get("stats"), "stats", _stats_block)
    model = _optional(payload.get("model"), "model", _model_block)
    return AnalysisReport(
        version=version,
        generated_at=_text(payload.get("generated_at"), "generated_at"),
        stats=stats,
        model=model,
    )
