"""U2 integration pipeline: dimensions, facts, aggregates, catalog."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import pandas as pd

from src.analytics.service import AnalyticsService
from src.common.io import AtomicWriter, read_parquet
from src.common.logging import JsonLogger
from src.common.types import (
    IntegrationReport,
    KpiReconciliationReport,
    RunContext,
    ValidationReport,
)
from src.external.ibge import IbgeClient
from src.external.region import RegionMapper
from src.integrate.aggregates import Aggregator
from src.integrate.catalog import DuckDbCatalog
from src.integrate.dimensions import DimensionBuilder
from src.integrate.facts import FactBuilder
from src.integrate.reconcile import KpiReconciler
from src.integrate.validate import StarSchemaValidator

CLEANED_TABLES = (
    "translation",
    "customers",
    "sellers",
    "products",
    "orders",
    "order_items",
    "payments",
    "reviews",
    "geolocation_zip",
)


@dataclass
class IntegrationResult:
    dims: dict[str, pd.DataFrame] = field(default_factory=dict)
    facts: dict[str, pd.DataFrame] = field(default_factory=dict)
    aggregates: dict[str, pd.DataFrame] = field(default_factory=dict)
    validation: ValidationReport | None = None
    reconciliation: KpiReconciliationReport | None = None
    report: IntegrationReport | None = None


def load_cleaned(config) -> dict[str, pd.DataFrame]:
    datasets = {}
    for table in CLEANED_TABLES:
        path = config.cleaned_dir / f"{table}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Cleaned table not found: {path}")
        datasets[table] = read_parquet(path)
    return datasets


def integrate_all(
    config,
    run: RunContext,
    writer: AtomicWriter,
    logger: JsonLogger,
    refresh_ibge: bool = False,
) -> IntegrationResult:
    cleaned = load_cleaned(config)

    ibge = IbgeClient(config, logger)
    region_map, ibge_source = ibge.fetch_states(refresh=refresh_ibge)
    RegionMapper.validate(
        region_map,
        states_in_data=set(cleaned["customers"]["customer_state"].dropna().unique())
        | set(cleaned["sellers"]["seller_state"].dropna().unique()),
    )

    dims = DimensionBuilder().build_all(cleaned, region_map)
    facts = FactBuilder().build_all(cleaned, dims)
    aggregates = Aggregator().build_all(facts, dims)

    validator = StarSchemaValidator()
    validation = validator.validate(dims, facts, run.run_id)
    validator.enforce(validation)

    reconciler = KpiReconciler()
    reconciliation = reconciler.reconcile(dims, facts, run.run_id)
    reconciler.enforce(reconciliation)

    temp_marts = run.temp_dir / "marts"
    temp_marts.mkdir(parents=True, exist_ok=True)
    all_tables = {**dims, **facts, **aggregates}
    for name, frame in all_tables.items():
        writer.write_parquet(frame, temp_marts / f"{name}.parquet")

    config.marts_dir.mkdir(parents=True, exist_ok=True)
    for name in all_tables:
        os.replace(temp_marts / f"{name}.parquet", config.marts_dir / f"{name}.parquet")

    DuckDbCatalog(config).create()

    report = IntegrationReport(
        run_id=run.run_id,
        row_counts={name: len(frame) for name, frame in all_tables.items()},
        ibge_source=ibge_source,
        passed=True,
    )
    writer.write_json(
        report.__dict__, config.reports_dir / "integration-report.json"
    )
    writer.write_json(
        reconciliation.__dict__, config.reports_dir / "kpi-reconciliation.json"
    )
    logger.info(
        "integrate_complete",
        dims=len(dims),
        facts=len(facts),
        aggregates=len(aggregates),
        ibge_source=ibge_source,
    )
    return IntegrationResult(
        dims=dims,
        facts=facts,
        aggregates=aggregates,
        validation=validation,
        reconciliation=reconciliation,
        report=report,
    )
