"""Quality gate for cleaned U1 datasets."""

from __future__ import annotations

import pandas as pd

from src.common.exceptions import QualityGateError
from src.common.logging import JsonLogger
from src.common.types import CheckResult, GeoCleaningStats, QualityReport
from src.ingest.schemas import TABLE_SPECS
from src.quality import checks
from src.quality.allowlist import EXPECTED_ANOMALIES

ALLOWED_STATUS = {
    "delivered",
    "shipped",
    "canceled",
    "unavailable",
    "invoiced",
    "processing",
    "created",
    "approved",
}


class QualityGate:
    """Run structural checks and the full-batch anomaly allowlist."""

    def __init__(self, logger: JsonLogger | None = None) -> None:
        self.logger = logger

    def _anomaly(
        self,
        check_id: str,
        key: str,
        actual: int,
    ) -> CheckResult:
        expected = EXPECTED_ANOMALIES[key]
        return CheckResult(
            check_id=check_id,
            name=key,
            passed=actual == expected,
            expected=expected,
            actual=actual,
            details=f"{key}: expected {expected}, actual {actual}",
        )

    def run(
        self,
        datasets: dict[str, pd.DataFrame],
        mode: str = "full",
        geo_stats: GeoCleaningStats | None = None,
        run_id: str = "",
    ) -> QualityReport:
        orders = datasets["orders"]
        customers = datasets["customers"]
        sellers = datasets["sellers"]
        products = datasets["products"]
        order_items = datasets["order_items"]
        payments = datasets["payments"]
        reviews = datasets["reviews"]
        translation = datasets["translation"]
        geo = datasets["geolocation_zip"]

        results: list[CheckResult] = [
            checks.check_unique(orders, ("order_id",), "U-01", "orders.order_id"),
            checks.check_unique(customers, ("customer_id",), "U-02", "customers.customer_id"),
            checks.check_unique(
                order_items,
                ("order_id", "order_item_id"),
                "U-03",
                "order_items composite key",
            ),
            checks.check_unique(
                payments,
                ("order_id", "payment_sequential"),
                "U-04",
                "payments composite key",
            ),
            checks.check_unique(
                reviews,
                ("review_id", "order_id"),
                "U-05",
                "reviews composite key",
            ),
            checks.check_unique(products, ("product_id",), "U-06", "products.product_id"),
            checks.check_unique(sellers, ("seller_id",), "U-07", "sellers.seller_id"),
            checks.check_unique(
                translation,
                ("product_category_name",),
                "U-08",
                "translation category",
            ),
            checks.check_unique(
                geo,
                ("zip_code_prefix",),
                "U-09",
                "geolocation_zip.zip_code_prefix",
            ),
            checks.check_foreign_key(
                order_items,
                "order_id",
                orders,
                "order_id",
                "F-01",
                "order_items.order_id -> orders",
            ),
            checks.check_foreign_key(
                order_items,
                "product_id",
                products,
                "product_id",
                "F-02",
                "order_items.product_id -> products",
            ),
            checks.check_foreign_key(
                order_items,
                "seller_id",
                sellers,
                "seller_id",
                "F-03",
                "order_items.seller_id -> sellers",
            ),
            checks.check_foreign_key(
                payments,
                "order_id",
                orders,
                "order_id",
                "F-04",
                "payments.order_id -> orders",
            ),
            checks.check_foreign_key(
                reviews,
                "order_id",
                orders,
                "order_id",
                "F-05",
                "reviews.order_id -> orders",
            ),
            checks.check_foreign_key(
                orders,
                "customer_id",
                customers,
                "customer_id",
                "F-06",
                "orders.customer_id -> customers",
            ),
            checks.check_between(
                reviews,
                "review_score",
                1,
                5,
                "D-01",
                "review_score 1..5",
            ),
            checks.check_min(order_items, "price", 0, "D-02", "price >= 0"),
            checks.check_min(
                order_items,
                "freight_value",
                0,
                "D-03",
                "freight_value >= 0",
            ),
            checks.check_min(
                payments,
                "payment_value",
                0,
                "D-04",
                "payment_value >= 0",
            ),
            checks.check_min(
                payments,
                "payment_installments",
                0,
                "D-05",
                "payment_installments >= 0",
            ),
            checks.check_allowed_values(
                orders,
                "order_status",
                ALLOWED_STATUS,
                "D-06",
                "order_status allowed",
            ),
        ]

        if mode == "full":
            expected_rows = {
                "orders": 99_441,
                "customers": 99_441,
                "order_items": 112_650,
                "payments": 103_886,
                "reviews": 99_224,
                "products": 32_951,
                "sellers": 3_095,
                "translation": 71,
                "geolocation_zip": 19_015,
            }
            for index, (name, expected) in enumerate(expected_rows.items(), start=1):
                results.append(
                    checks.check_row_count(
                        datasets[name],
                        expected,
                        f"R-{index:02d}",
                        f"{name} row count",
                    )
                )

            results.extend(
                [
                    self._anomaly(
                        "A-01",
                        "orders_without_items",
                        len(orders) - order_items["order_id"].nunique(),
                    ),
                    self._anomaly(
                        "A-02",
                        "orders_without_payment",
                        len(orders) - payments["order_id"].nunique(),
                    ),
                    self._anomaly(
                        "A-03",
                        "customer_zips_missing_geo",
                        int(
                            (~customers["customer_zip_code_prefix"].isin(
                                geo["zip_code_prefix"]
                            )).sum()
                        ),
                    ),
                    self._anomaly(
                        "A-04",
                        "seller_zips_missing_geo",
                        int(
                            (~sellers["seller_zip_code_prefix"].isin(
                                geo["zip_code_prefix"]
                            )).sum()
                        ),
                    ),
                    self._anomaly(
                        "A-05",
                        "products_missing_category",
                        int(products["category_missing"].fillna(False).sum()),
                    ),
                    self._anomaly(
                        "A-06",
                        "orders_multiple_reviews",
                        int(
                            reviews.loc[
                                reviews["multiple_reviews_per_order"].fillna(False),
                                "order_id",
                            ].nunique()
                        ),
                    ),
                    self._anomaly(
                        "A-07",
                        "geo_exact_duplicates",
                        (geo_stats.raw_rows - geo_stats.deduped_rows)
                        if geo_stats
                        else -1,
                    ),
                    self._anomaly(
                        "A-08",
                        "geo_outside_bbox",
                        geo_stats.outside_bbox if geo_stats else -1,
                    ),
                    self._anomaly(
                        "A-09",
                        "geo_zips_without_coord",
                        geo_stats.zips_without_coord if geo_stats else -1,
                    ),
                    self._anomaly(
                        "A-10",
                        "price_outliers",
                        int(order_items["price_outlier"].fillna(False).sum()),
                    ),
                ]
            )

        report = QualityReport(
            run_id=run_id,
            mode=mode,
            checks=results,
            passed=all(check.passed for check in results),
        )
        if self.logger:
            failed = [check.check_id for check in results if not check.passed]
            self.logger.info(
                "quality_gate",
                mode=mode,
                checks=len(results),
                failed=failed,
                passed=report.passed,
            )
        return report

    def enforce(self, report: QualityReport) -> None:
        if report.passed:
            return
        failed = [
            f"{check.check_id}: {check.name} expected={check.expected} actual={check.actual}"
            for check in report.checks
            if not check.passed
        ]
        raise QualityGateError("Quality gate failed:\n" + "\n".join(failed))
