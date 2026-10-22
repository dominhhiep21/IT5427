"""Validate star-schema grains and relationships."""

from __future__ import annotations

import pandas as pd

from src.common.exceptions import QualityGateError
from src.common.types import CheckResult, ValidationReport


class StarSchemaValidator:
    EXPECTED = {
        "dim_customer": 99_441,
        "dim_product": 32_951,
        "dim_seller": 3_095,
        "dim_geography": 19_015,
        "dim_date": 774,
        "fact_order_items": 112_650,
        "fact_orders": 99_441,
        "fact_payments": 103_886,
        "fact_reviews": 99_224,
    }

    def _count_check(self, name: str, frame: pd.DataFrame, expected: int) -> CheckResult:
        return CheckResult(
            check_id=f"C-{name}",
            name=f"{name} row count",
            passed=len(frame) == expected,
            expected=expected,
            actual=len(frame),
        )

    def _unique_check(
        self, name: str, frame: pd.DataFrame, columns: list[str]
    ) -> CheckResult:
        duplicates = int(frame.duplicated(subset=columns, keep=False).sum())
        return CheckResult(
            check_id=f"U-{name}",
            name=f"{name} unique {columns}",
            passed=duplicates == 0,
            expected=0,
            actual=duplicates,
        )

    def validate(
        self,
        dims: dict[str, pd.DataFrame],
        facts: dict[str, pd.DataFrame],
        run_id: str = "",
    ) -> ValidationReport:
        checks: list[CheckResult] = []
        for name, expected in self.EXPECTED.items():
            if name in dims:
                frame = dims[name]
            elif name in facts:
                frame = facts[name]
            else:
                raise KeyError(f"Missing dataset: {name}")
            checks.append(self._count_check(name, frame, expected))

        checks.extend(
            [
                self._unique_check("customer", dims["dim_customer"], ["customer_id"]),
                self._unique_check("product", dims["dim_product"], ["product_id"]),
                self._unique_check("seller", dims["dim_seller"], ["seller_id"]),
                self._unique_check(
                    "geography", dims["dim_geography"], ["zip_code_prefix"]
                ),
                self._unique_check("date", dims["dim_date"], ["date_key"]),
                self._unique_check(
                    "order_items",
                    facts["fact_order_items"],
                    ["order_id", "order_item_id"],
                ),
                self._unique_check("orders", facts["fact_orders"], ["order_id"]),
                self._unique_check(
                    "payments",
                    facts["fact_payments"],
                    ["order_id", "payment_sequential"],
                ),
                self._unique_check(
                    "reviews", facts["fact_reviews"], ["review_id", "order_id"]
                ),
            ]
        )

        region_nulls = int(dims["dim_customer"]["region"].isna().sum())
        checks.append(
            CheckResult(
                check_id="R-01",
                name="dim_customer region not null",
                passed=region_nulls == 0,
                expected=0,
                actual=region_nulls,
            )
        )

        joined = facts["fact_order_items"].merge(
            dims["dim_customer"][["customer_id"]], on="customer_id", how="left"
        )
        joined = joined.merge(
            dims["dim_product"][["product_id"]], on="product_id", how="left"
        )
        joined = joined.merge(
            dims["dim_seller"][["seller_id"]], on="seller_id", how="left"
        )
        checks.append(
            CheckResult(
                check_id="J-01",
                name="fact_order_items x dims row count",
                passed=len(joined) == 112_650,
                expected=112_650,
                actual=len(joined),
            )
        )

        late_not_delivered = int(
            (
                facts["fact_orders"]["is_late"].fillna(False)
                & ~facts["fact_orders"]["is_delivered"].fillna(False)
            ).sum()
        )
        checks.append(
            CheckResult(
                check_id="L-01",
                name="is_late only for delivered",
                passed=late_not_delivered == 0,
                expected=0,
                actual=late_not_delivered,
            )
        )

        return ValidationReport(
            run_id=run_id,
            checks=checks,
            passed=all(check.passed for check in checks),
        )

    def enforce(self, report: ValidationReport) -> None:
        if report.passed:
            return
        failed = [
            f"{check.check_id}: expected={check.expected} actual={check.actual}"
            for check in report.checks
            if not check.passed
        ]
        raise QualityGateError("Star schema validation failed:\n" + "\n".join(failed))
