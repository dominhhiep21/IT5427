"""Reconcile star-schema KPIs against the verified baseline."""

from __future__ import annotations

from src.common.exceptions import QualityGateError
from src.common.types import KpiReconciliationReport

BASELINE = {
    "revenue_delivered": 15_419_773.75,
    "delivered_orders": 96_478,
    "aov": 159.83,
    "late_orders": 7_826,
    "late_rate_pct": 8.11,
}

TOLERANCE = {
    "revenue_delivered": 0.01,
    "delivered_orders": 0,
    "aov": 0.01,
    "late_orders": 0,
    "late_rate_pct": 0.01,
}


class KpiReconciler:
    def reconcile(self, dims, facts, run_id: str = "") -> KpiReconciliationReport:
        items = facts["fact_order_items"]
        orders = facts["fact_orders"]
        delivered_items = items[items["is_delivered"].fillna(False)]
        delivered_orders = orders[orders["is_delivered"].fillna(False)]

        revenue = round(float(delivered_items["item_total"].sum()), 2)
        order_count = int(delivered_items["order_id"].nunique())
        aov = round(revenue / order_count, 2) if order_count else 0.0
        late_orders = int(delivered_orders["is_late"].fillna(False).sum())
        late_rate = round(late_orders / len(delivered_orders) * 100, 2)

        metrics = {
            "revenue_delivered": revenue,
            "delivered_orders": order_count,
            "aov": aov,
            "late_orders": late_orders,
            "late_rate_pct": late_rate,
        }
        deltas = {
            key: round(abs(metrics[key] - BASELINE[key]), 4) for key in BASELINE
        }
        passed = all(
            deltas[key] <= TOLERANCE[key] for key in TOLERANCE
        )
        return KpiReconciliationReport(
            run_id=run_id,
            metrics=metrics,
            deltas=deltas,
            passed=passed,
        )

    def enforce(self, report: KpiReconciliationReport) -> None:
        if report.passed:
            return
        details = ", ".join(
            f"{key}: actual={report.metrics[key]} baseline={BASELINE[key]} delta={report.deltas[key]}"
            for key in BASELINE
            if report.deltas[key] > TOLERANCE[key]
        )
        raise QualityGateError(f"KPI reconciliation failed: {details}")
