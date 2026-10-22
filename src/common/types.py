"""Shared dataclasses and type aliases."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class TableSpec:
    name: str
    file_name: str
    columns: tuple[str, ...]
    key_columns: tuple[str, ...]
    expected_rows: int


@dataclass(frozen=True)
class RunContext:
    run_id: str
    stage: str
    started_at: datetime
    temp_dir: Path
    log_path: Path


@dataclass
class IngestFileReport:
    table: str
    file: str
    rows: int
    expected_rows: int
    columns: int
    sha256: str
    read_at: str


@dataclass
class IngestReport:
    run_id: str
    files: list[IngestFileReport] = field(default_factory=list)
    passed: bool = True


@dataclass
class CleaningTableReport:
    table: str
    rows_in: int
    rows_out: int
    null_counts: dict[str, int] = field(default_factory=dict)
    flag_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class GeoCleaningStats:
    raw_rows: int
    deduped_rows: int
    outside_bbox: int
    zips: int
    zips_without_coord: int
    multi_city_zips: int


@dataclass
class CleaningReport:
    run_id: str
    tables: list[CleaningTableReport] = field(default_factory=list)
    geolocation: GeoCleaningStats | None = None


@dataclass
class CheckResult:
    check_id: str
    name: str
    passed: bool
    expected: object = None
    actual: object = None
    details: str = ""


@dataclass
class QualityReport:
    run_id: str
    mode: str
    checks: list[CheckResult] = field(default_factory=list)
    passed: bool = True


@dataclass
class ReconciliationReport:
    run_id: str
    orders_compared: int
    mismatch_count: int
    max_abs_diff: float
    examples: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class KpiFilters:
    start_date: str | None = None
    end_date: str | None = None
    state: str | None = None
    region: str | None = None
    category: str | None = None
    order_status: str = "delivered"


@dataclass
class IbgeMetadata:
    url: str
    fetched_at: str
    sha256: str
    states: int
    municipalities: int = 0
    source: str = "ibge-api"


@dataclass
class IntegrationReport:
    run_id: str
    row_counts: dict[str, int] = field(default_factory=dict)
    ibge_source: str = ""
    passed: bool = True


@dataclass
class ValidationReport:
    run_id: str
    checks: list[CheckResult] = field(default_factory=list)
    passed: bool = True


@dataclass
class KpiReconciliationReport:
    run_id: str
    metrics: dict[str, float] = field(default_factory=dict)
    deltas: dict[str, float] = field(default_factory=dict)
    passed: bool = True
