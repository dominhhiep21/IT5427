# Phương thức component (Component Methods)

> Đây là interface mức cao. Business rule chi tiết (công thức, ngưỡng, xử lý null) sẽ được chốt trong Functional Design.

## Kiểu dùng chung

```python
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal
import pandas as pd

Stage = Literal["ingest", "clean", "quality", "external", "integrate", "analyze", "all"]

@dataclass(frozen=True)
class AppConfig:
    raw_dir: Path
    data_dir: Path
    warehouse_path: Path
    inbox_dir: Path
    ibge_dir: Path
    quality_thresholds: dict[str, float]
    dashboard_host: str
    dashboard_port: int

@dataclass
class RunContext:
    run_id: str
    stage: str
    started_at: datetime

@dataclass
class TableSpec:
    name: str
    required_columns: list[str]
    key_columns: list[str]
    expected_rows: int | None = None

@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str

@dataclass
class QualityReport:
    run_id: str
    checks: list[CheckResult]
    passed: bool

@dataclass
class IngestReport:
    datasets: dict[str, pd.DataFrame]
    files: list[dict]          # path, rows, sha256, read_at
    passed: bool
```

## config

```python
def load_config(path: Path | None = None) -> AppConfig: ...
```
- Nạp YAML + default; kiểm tra `dataset/` tồn tại; tạo thư mục output nếu thiếu.

## common

```python
def new_run_context(stage: str) -> RunContext: ...
def get_logger(run: RunContext) -> logging.Logger: ...
def sha256_file(path: Path) -> str: ...
def read_csv(path: Path, spec: TableSpec) -> pd.DataFrame: ...
def write_parquet(df: pd.DataFrame, path: Path, partition_cols: list[str] | None = None) -> None: ...
def read_parquet(path: Path) -> pd.DataFrame: ...
def write_json(payload: dict, path: Path) -> None: ...        # run summary, manifest
def read_json(path: Path) -> dict: ...

class ManifestStore:
    def __init__(self, path: Path) -> None: ...
    def has(self, file_hash: str) -> bool: ...
    def add(self, file_hash: str, source: str, processed_at: datetime) -> None: ...
```

## ingest

```python
def ingest_all(config: AppConfig, run: RunContext) -> IngestReport: ...
def ingest_table(name: str, spec: TableSpec, config: AppConfig, run: RunContext) -> pd.DataFrame: ...
def validate_columns(df: pd.DataFrame, spec: TableSpec) -> None: ...  # raise SchemaError
def write_raw(df: pd.DataFrame, name: str, config: AppConfig) -> Path: ...
```

## quality

```python
def check_unique(df: pd.DataFrame, columns: list[str], name: str) -> CheckResult: ...
def check_foreign_key(
    child: pd.DataFrame, child_col: str,
    parent: pd.DataFrame, parent_col: str,
    name: str, allow_missing: bool = False,
) -> CheckResult: ...
def check_row_count(df: pd.DataFrame, expected: int, name: str) -> CheckResult: ...
def check_required_not_null(df: pd.DataFrame, columns: list[str], name: str) -> CheckResult: ...
def check_value_range(df: pd.DataFrame, column: str, min_value: float, max_value: float, name: str) -> CheckResult: ...
def run_quality_gate(datasets: dict[str, pd.DataFrame], config: AppConfig, run: RunContext) -> QualityReport: ...
```

## clean

```python
def clean_orders(df: pd.DataFrame) -> pd.DataFrame: ...
def clean_customers(df: pd.DataFrame) -> pd.DataFrame: ...
def clean_sellers(df: pd.DataFrame) -> pd.DataFrame: ...
def clean_products(df: pd.DataFrame, translation: pd.DataFrame) -> pd.DataFrame: ...
def clean_order_items(df: pd.DataFrame) -> pd.DataFrame: ...
def clean_payments(df: pd.DataFrame) -> pd.DataFrame: ...
def clean_reviews(df: pd.DataFrame) -> pd.DataFrame: ...
def clean_geolocation(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame: ...
def clean_all(raw: dict[str, pd.DataFrame], config: AppConfig, run: RunContext) -> dict[str, pd.DataFrame]: ...
```

## external

```python
@dataclass
class IbgeData:
    states: pd.DataFrame
    municipalities: pd.DataFrame | None
    source_url: str
    downloaded_at: datetime
    from_cache: bool

def fetch_ibge(config: AppConfig, run: RunContext, force: bool = False) -> IbgeData: ...
def load_region_map(config: AppConfig) -> pd.DataFrame: ...
def validate_region_map(df: pd.DataFrame) -> None: ...  # 27 states, 5 regions, no null
```

## integrate

```python
def build_dimensions(cleaned: dict[str, pd.DataFrame], region_map: pd.DataFrame, config: AppConfig) -> dict[str, pd.DataFrame]: ...
def build_facts(cleaned: dict[str, pd.DataFrame], dimensions: dict[str, pd.DataFrame], config: AppConfig) -> dict[str, pd.DataFrame]: ...
def write_marts(dimensions: dict[str, pd.DataFrame], facts: dict[str, pd.DataFrame], config: AppConfig) -> None: ...
def create_duckdb_catalog(config: AppConfig, run: RunContext) -> None: ...
```

## analytics

```python
@dataclass(frozen=True)
class KpiFilters:
    start_date: str | None = None
    end_date: str | None = None
    state: str | None = None
    region: str | None = None
    category: str | None = None
    order_status: str = "delivered"

def kpi_summary(filters: KpiFilters, config: AppConfig) -> dict[str, float]: ...
def revenue_by_period(filters: KpiFilters, granularity: Literal["month", "quarter", "year"], config: AppConfig) -> pd.DataFrame: ...
def revenue_by_dimension(filters: KpiFilters, dimension: Literal["category", "region", "state"], config: AppConfig) -> pd.DataFrame: ...
def top_entities(filters: KpiFilters, entity: Literal["product", "seller"], limit: int, config: AppConfig) -> pd.DataFrame: ...
def delivery_kpis(filters: KpiFilters, group_by: Literal["state", "category", "month"] | None, config: AppConfig) -> pd.DataFrame: ...
```

## dashboard

```python
def create_app(config: AppConfig) -> Dash: ...
def build_layout(config: AppConfig) -> html.Div: ...
def register_callbacks(app: Dash, config: AppConfig) -> None: ...
def format_brl(value: float) -> str: ...
def format_date(value: str) -> str: ...
```

## pipeline

```python
@dataclass
class StageResult:
    stage: str
    status: Literal["success", "failed", "skipped"]
    rows_in: int
    rows_out: int
    duration_seconds: float

@dataclass
class RunSummary:
    run_id: str
    stages: list[StageResult]
    success: bool

def run_stage(stage: Stage, config: AppConfig) -> StageResult: ...
def run_all(config: AppConfig) -> RunSummary: ...
def run_micro_batch(config: AppConfig) -> list[StageResult]: ...
def replay(config: AppConfig, batches: int) -> list[StageResult]: ...
def main(argv: list[str] | None = None) -> int: ...  # CLI entrypoint
```

## tests

```python
# Ví dụ test interface, không phải module runtime
def test_geolocation_join_does_not_explode() -> None: ...
def test_category_fallback_keeps_rows() -> None: ...
def test_delivery_late_rate_matches_baseline() -> None: ...
def test_quality_gate_fails_on_orphan() -> None: ...
```

## Quy ước lỗi

```python
class PipelineError(Exception): ...
class SchemaError(PipelineError): ...
class QualityGateError(PipelineError): ...
class ExternalSourceError(PipelineError): ...
class ConfigurationError(PipelineError): ...
```
