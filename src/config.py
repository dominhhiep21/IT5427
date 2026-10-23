"""Application configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.common.exceptions import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AppConfig:
    """Immutable runtime configuration."""

    workspace_root: Path
    config_path: Path
    raw_csv_dir: Path
    data_dir: Path
    raw_dir: Path
    cleaned_dir: Path
    marts_dir: Path
    reports_dir: Path
    logs_dir: Path
    temp_dir: Path
    duckdb_path: Path
    ibge_dir: Path
    inbox_dir: Path
    parquet_compression: str = "snappy"
    duckdb_memory_limit: str = "1GB"
    duckdb_threads: int = 4
    ibge_url: str = "https://servicodados.ibge.gov.br/api/v1/localidades"
    ibge_timeout_seconds: int = 10
    ibge_retries: int = 2
    max_batch_rows: int = 10000
    batch_timeout_seconds: int = 30
    geo_lat_min: float = -34.0
    geo_lat_max: float = 6.0
    geo_lng_min: float = -74.0
    geo_lng_max: float = -34.0
    iqr_multiplier: float = 1.5
    memory_warn_mb: int = 1536
    memory_fail_mb: int = 2048
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8050


def _resolve(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def load_config(path: Path | None = None) -> AppConfig:
    """Load config.yaml and create output directories."""

    config_path = Path(path).resolve() if path else PROJECT_ROOT / "config.yaml"
    if path is not None and not config_path.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")

    raw: dict = {}
    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    paths = raw.get("paths", {})
    parquet = raw.get("parquet", {})
    geo = raw.get("geolocation", {})
    quality = raw.get("quality", {})
    dashboard = raw.get("dashboard", {})

    workspace_root = config_path.parent
    raw_csv_dir = _resolve(workspace_root, paths.get("raw_csv_dir", "dataset"))
    if not raw_csv_dir.exists():
        raise ConfigurationError(f"Raw CSV directory not found: {raw_csv_dir}")

    data_dir = _resolve(workspace_root, paths.get("data_dir", "data"))
    marts_dir = _resolve(workspace_root, paths.get("marts_dir", "data/marts"))
    reports_dir = _resolve(workspace_root, paths.get("reports_dir", "data/reports"))
    logs_dir = _resolve(workspace_root, paths.get("logs_dir", "logs"))
    temp_dir = _resolve(workspace_root, paths.get("temp_dir", "data/.tmp"))
    duckdb_path = _resolve(
        workspace_root, paths.get("duckdb_path", "warehouse/olist.duckdb")
    )
    ibge_dir = _resolve(
        workspace_root, paths.get("ibge_dir", "dataset/external/ibge")
    )
    inbox_dir = _resolve(workspace_root, paths.get("inbox_dir", "inbox"))
    duckdb_config = raw.get("duckdb", {})
    ibge_config = raw.get("ibge", {})
    batch_config = raw.get("micro_batch", {})

    config = AppConfig(
        workspace_root=workspace_root,
        config_path=config_path,
        raw_csv_dir=raw_csv_dir,
        data_dir=data_dir,
        raw_dir=data_dir / "raw",
        cleaned_dir=data_dir / "cleaned",
        marts_dir=marts_dir,
        reports_dir=reports_dir,
        logs_dir=logs_dir,
        temp_dir=temp_dir,
        duckdb_path=duckdb_path,
        ibge_dir=ibge_dir,
        inbox_dir=inbox_dir,
        parquet_compression=parquet.get("compression", "snappy"),
        duckdb_memory_limit=duckdb_config.get("memory_limit", "1GB"),
        duckdb_threads=int(duckdb_config.get("threads", 4)),
        ibge_url=ibge_config.get(
            "url", "https://servicodados.ibge.gov.br/api/v1/localidades"
        ),
        ibge_timeout_seconds=int(ibge_config.get("timeout_seconds", 10)),
        ibge_retries=int(ibge_config.get("retries", 2)),
        max_batch_rows=int(batch_config.get("max_rows", 10000)),
        batch_timeout_seconds=int(batch_config.get("timeout_seconds", 30)),
        geo_lat_min=float(geo.get("lat_min", -34.0)),
        geo_lat_max=float(geo.get("lat_max", 6.0)),
        geo_lng_min=float(geo.get("lng_min", -74.0)),
        geo_lng_max=float(geo.get("lng_max", -34.0)),
        iqr_multiplier=float(quality.get("iqr_multiplier", 1.5)),
        memory_warn_mb=int(quality.get("memory_warn_mb", 1536)),
        memory_fail_mb=int(quality.get("memory_fail_mb", 2048)),
        dashboard_host=dashboard.get("host", "127.0.0.1"),
        dashboard_port=int(dashboard.get("port", 8050)),
    )

    for directory in (
        config.data_dir,
        config.raw_dir,
        config.cleaned_dir,
        config.marts_dir,
        config.reports_dir,
        config.logs_dir,
        config.temp_dir,
        config.duckdb_path.parent,
        config.ibge_dir,
        config.inbox_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    return config
