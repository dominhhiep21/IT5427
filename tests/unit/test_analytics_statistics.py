"""Unit test cho năm phép kiểm định ở `src/analytics/statistics.py` và ba phương thức đọc mới (BR1.1–BR1.8)."""

from __future__ import annotations

import math
import re
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from src.analytics.service import (
    LATE_RATES_BY_REGION_SQL,
    LATE_RATES_BY_STATE_SQL,
    PRICE_FREIGHT_PAIRS_SQL,
    AnalyticsService,
)
from src.analytics.statistics import (
    ALPHA,
    CONFIDENCE,
    GROUP_TEST_NAME,
    MIN_SEASONAL_MONTHS,
    SEASONAL_METHOD,
    SKIP_TESTS,
    compare_states,
    confidence_for,
    collect_stats,
    late_rate,
    ordered_skips,
    price_freight_correlation,
    region_late_test,
    seasonal_decomposition,
    wilson_interval,
    z_critical,
)
from src.analytics.report import SkipEntry
from src.common.kpis import REVENUE_DEFINITION
from src.common.types import KpiFilters
from src.integrate.catalog import VIEW_TABLES


def state_rates() -> pd.DataFrame:
    """Bốn bang: hai bang đủ ngưỡng 100 đơn, hai bang bị loại."""

    return pd.DataFrame(
        {
            "state": ["AL", "AM", "RJ", "SP"],
            "delivered_orders": [150, 40, 12000, 40000],
            "late_orders": [30, 4, 600, 3000],
        }
    )


def monthly_rows(count: int, skip: int | None = None) -> pd.DataFrame:
    """`count` tháng liên tục từ 2017-01, mỗi tháng `revenue` khác nhau; `skip` bỏ một tháng."""

    rows = [
        {
            "year": 2017 + index // 12,
            "month": index % 12 + 1,
            "revenue": 1000.0 + index * 37.5,
        }
        for index in range(count)
        if index != skip
    ]
    return pd.DataFrame(rows)


def region_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["Sudeste", "Sudeste", "Nordeste", "Nordeste", "Norte", "Norte"],
            "is_late": [False, True, False, True, False, True],
            "delivered_orders": [60000, 5000, 12000, 1500, 3000, 200],
        }
    )


def test_confidence_comes_from_the_single_alpha_constant():
    assert ALPHA == 0.05
    assert CONFIDENCE == 1 - ALPHA
    assert confidence_for(0.01) == 0.99


def test_z_critical_matches_the_two_sided_normal_quantile():
    assert z_critical() == pytest.approx(1.959963984540054, rel=1e-12)


def test_wilson_interval_matches_an_independent_computation():
    successes, total, z = 7826, 96478, z_critical()
    rate = successes / total
    denominator = 1 + z * z / total
    centre = (rate + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator

    low, high = wilson_interval(successes, total, z)

    assert low == pytest.approx(centre - margin, rel=1e-12)
    assert high == pytest.approx(centre + margin, rel=1e-12)
    assert low < rate < high


def test_late_rate_reports_a_fraction_and_a_bracket_that_holds_it():
    result = late_rate(96478, 7826)

    assert result.successes == 7826
    assert result.total == 96478
    assert 0 <= result.rate <= 1
    assert result.rate == pytest.approx(7826 / 96478, rel=1e-12)
    assert result.ci_low <= result.rate <= result.ci_high


def test_late_rate_without_a_delivered_order_stops_the_stage():
    with pytest.raises(ValueError) as caught:
        late_rate(0, 0)

    assert "BR1.1" in str(caught.value)


def test_compare_states_uses_only_eligible_states_and_reports_the_excluded_orders():
    comparisons, skipped = compare_states(state_rates())

    assert skipped is None
    assert len(comparisons) == 1
    comparison = comparisons[0]
    assert (comparison.first, comparison.second) == ("AL", "RJ")
    assert comparison.excluded == 40
    assert comparison.difference == pytest.approx(30 / 150 - 600 / 12000, rel=1e-12)
    assert comparison.ci_low <= comparison.difference <= comparison.ci_high
    assert 0 <= comparison.p_value <= 1
    assert comparison.significant == (comparison.p_value < ALPHA)


def test_compare_states_needs_two_eligible_states():
    frame = pd.DataFrame({"state": ["SP", "RJ"], "delivered_orders": [500, 90], "late_orders": [50, 9]})

    comparisons, skipped = compare_states(frame)

    assert comparisons == []
    assert skipped is not None
    assert skipped.test == "state_comparison"
    assert "100" in skipped.reason


def test_compare_states_without_any_row_is_skipped():
    comparisons, skipped = compare_states(pd.DataFrame(columns=["state", "delivered_orders", "late_orders"]))

    assert comparisons == []
    assert skipped.test == "state_comparison"


def test_correlation_reports_n_and_a_fisher_bracket_that_holds_r():
    pairs = pd.DataFrame(
        {
            "price": [10.0, 20.0, 30.0, 40.0, 50.0],
            "freight_value": [2.0, 1.0, 4.0, 3.0, 5.0],
        }
    )

    result, skipped = price_freight_correlation(pairs)

    assert skipped is None
    assert result.n == 5
    assert result.r == pytest.approx(0.8, abs=0.001)
    assert result.ci_low <= result.r <= result.ci_high


def test_correlation_with_three_rows_is_skipped():
    pairs = pd.DataFrame({"price": [1.0, 2.0, 3.0], "freight_value": [3.0, 2.0, 1.0]})

    result, skipped = price_freight_correlation(pairs)

    assert result is None
    assert skipped.test == "correlation"
    assert "3" in skipped.reason


def test_correlation_with_a_constant_series_is_skipped_instead_of_returning_nan():
    pairs = pd.DataFrame({"price": [5.0, 5.0, 5.0, 5.0], "freight_value": [1.0, 2.0, 3.0, 4.0]})

    result, skipped = price_freight_correlation(pairs)

    assert result is None
    assert skipped.test == "correlation"
    assert "không đổi" in skipped.reason


def test_region_test_runs_when_every_expected_cell_reaches_five():
    result, skipped = region_late_test(region_rows())

    assert skipped is None
    assert result.test == GROUP_TEST_NAME
    assert result.dof == 3 - 1
    assert result.min_expected >= 5
    assert 0 <= result.p_value <= 1


def test_region_test_is_skipped_when_an_expected_cell_is_below_five():
    rows = pd.DataFrame(
        {
            "region": ["A", "A", "B", "B"],
            "is_late": [False, True, False, True],
            "delivered_orders": [100, 1, 100, 1],
        }
    )

    result, skipped = region_late_test(rows)

    assert result is None
    assert skipped.test == "group_test"
    assert "dưới ngưỡng" in skipped.reason


def test_region_test_needs_two_regions_and_some_rows():
    one_region = pd.DataFrame({"region": ["A", "A"], "is_late": [False, True], "delivered_orders": [100, 20]})

    result, skipped = region_late_test(one_region)
    empty_result, empty_skip = region_late_test(pd.DataFrame(columns=["region", "is_late", "delivered_orders"]))

    assert result is None and skipped.test == "group_test"
    assert empty_result is None and empty_skip.test == "group_test"


def test_seasonal_decomposition_keeps_a_continuous_axis_and_fills_missing_months():
    result, skipped = seasonal_decomposition(monthly_rows(24, skip=5))

    assert skipped is None
    assert result.method == SEASONAL_METHOD
    assert result.period == 12
    assert result.revenue_definition == REVENUE_DEFINITION
    assert result.months[0] == "2017-01"
    assert result.months[-1] == "2018-12"
    assert len(result.months) == 24
    assert result.observed[5] == 0.0
    assert result.observed[0] == pytest.approx(1000.0, rel=1e-12)


def test_seasonal_decomposition_satisfies_the_additive_identity_on_unrounded_values():
    result, _ = seasonal_decomposition(monthly_rows(30))

    assert len(result.trend) == len(result.months)
    for observed, trend, seasonal, residual in zip(
        result.observed, result.trend, result.seasonal, result.residual
    ):
        assert observed == pytest.approx(trend + seasonal + residual, rel=1e-12, abs=1e-9)


def test_seasonal_decomposition_needs_twenty_four_months():
    result, skipped = seasonal_decomposition(monthly_rows(MIN_SEASONAL_MONTHS - 1))

    assert result is None
    assert skipped.test == "seasonal"
    assert "23" in skipped.reason


def test_seasonal_decomposition_without_months_is_skipped():
    result, skipped = seasonal_decomposition(pd.DataFrame(columns=["year", "month", "revenue"]))

    assert result is None
    assert skipped.test == "seasonal"


def test_ordered_skips_keeps_one_entry_per_test_in_the_fixed_order():
    entries = [
        SkipEntry("seasonal", "lý do 1"),
        SkipEntry("state_comparison", "lý do 2"),
        SkipEntry("seasonal", "lý do trùng"),
        None,
        SkipEntry("correlation", "lý do 3"),
    ]

    ordered = ordered_skips(entries)

    assert [entry.test for entry in ordered] == ["state_comparison", "correlation", "seasonal"]
    assert ordered[2].reason == "lý do 1"
    assert set(entry.test for entry in ordered) <= set(SKIP_TESTS)


class _FullService:
    """Service giả trả đủ dữ liệu cho cả năm phép, không chạm DuckDB."""

    def kpi_summary(self, filters):
        return {"delivered_orders": 1000, "late_orders": 80}

    def late_rates_by_state(self, filters):
        return state_rates()

    def price_freight_pairs(self, filters):
        return pd.DataFrame({"price": [1.0, 2.0, 3.0, 4.0], "freight_value": [4.0, 3.0, 2.0, 1.0]})

    def late_rates_by_region(self, filters):
        return region_rows()

    def revenue_by_period(self, filters, granularity="month"):
        assert granularity == "month"
        return monthly_rows(24)


class _EmptyService:
    """Service giả trả dữ liệu rỗng, để bốn kiểm định đều bị bỏ."""

    def kpi_summary(self, filters):
        return {"delivered_orders": 1000, "late_orders": 80}

    def late_rates_by_state(self, filters):
        return pd.DataFrame(columns=["state", "delivered_orders", "late_orders"])

    def price_freight_pairs(self, filters):
        return pd.DataFrame(columns=["price", "freight_value"])

    def late_rates_by_region(self, filters):
        return pd.DataFrame(columns=["region", "is_late", "delivered_orders"])

    def revenue_by_period(self, filters, granularity="month"):
        return pd.DataFrame(columns=["year", "month", "revenue"])


def test_collect_stats_fills_every_result_and_leaves_skipped_empty():
    block = collect_stats(_FullService(), KpiFilters(), "2026-11-10T00:00:00+00:00")

    assert block.alpha == ALPHA
    assert block.confidence == 1 - block.alpha
    assert block.late_rate.total == 1000
    assert len(block.comparisons) == 1
    assert block.correlation is not None
    assert block.group_test is not None
    assert block.seasonal is not None
    assert block.skipped == []


def test_collect_stats_records_one_skip_per_skipped_test_in_a_fixed_order():
    block = collect_stats(_EmptyService(), KpiFilters(), "2026-11-10T00:00:00+00:00")

    assert [entry.test for entry in block.skipped] == list(SKIP_TESTS)
    assert len(set(entry.test for entry in block.skipped)) == len(block.skipped)


ORDERS_ROWS = """
    ('o1', 'c1', '2017-01-05', TRUE, TRUE, 'delivered'),
    ('o2', 'c1', '2017-01-06', TRUE, FALSE, 'delivered'),
    ('o3', 'c2', '2017-02-05', TRUE, TRUE, 'delivered'),
    ('o4', 'c3', '2017-02-06', TRUE, FALSE, 'delivered'),
    ('o5', 'c2', '2017-03-05', FALSE, FALSE, 'canceled')
"""

CUSTOMER_ROWS = """
    ('c1', 'SP', 'Sudeste'),
    ('c2', 'RJ', 'Sudeste'),
    ('c3', 'BA', 'Nordeste')
"""

ITEM_ROWS = """
    ('o1', 1, 'c1', '2017-01-05', 10.0, 1.0, TRUE, 'delivered'),
    ('o2', 1, 'c1', '2017-01-06', 20.0, 2.0, TRUE, 'delivered'),
    ('o3', 1, 'c2', '2017-02-05', 30.0, 3.0, TRUE, 'delivered'),
    ('o4', 1, 'c3', '2017-02-06', NULL, 4.0, TRUE, 'delivered')
"""


def build_mart(config) -> Path:
    """Dựng mart tối thiểu cho ba phương thức đọc mới trong DuckDB tạm của test."""

    config.duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(config.duckdb_path))
    try:
        conn.execute(
            "CREATE OR REPLACE VIEW v_fact_orders AS SELECT * FROM (VALUES " + ORDERS_ROWS + ") "
            "AS t(order_id, customer_id, date_key, is_delivered, is_late, order_status)"
        )
        conn.execute(
            "CREATE OR REPLACE VIEW v_dim_customer AS SELECT * FROM (VALUES " + CUSTOMER_ROWS + ") "
            "AS t(customer_id, state, region)"
        )
        conn.execute("CREATE OR REPLACE VIEW v_dim_date AS SELECT DISTINCT date_key FROM v_fact_orders")
        conn.execute(
            "CREATE OR REPLACE VIEW v_fact_order_items AS SELECT * FROM (VALUES " + ITEM_ROWS + ") "
            "AS t(order_id, order_item_id, customer_id, date_key, price, freight_value, "
            "is_delivered, order_status)"
        )
    finally:
        conn.close()
    return config.duckdb_path


def test_late_rates_by_state_returns_one_row_per_delivered_state(config):
    build_mart(config)

    frame = AnalyticsService(config).late_rates_by_state(KpiFilters(order_status="all"))

    ordered = frame.set_index("state").sort_index()
    assert list(ordered.index) == ["BA", "RJ", "SP"]
    assert ordered.loc["SP", "delivered_orders"] == 2
    assert ordered.loc["SP", "late_orders"] == 1
    assert ordered.loc["BA", "late_orders"] == 0
    assert int(ordered["delivered_orders"].sum()) == 4


def test_price_freight_pairs_drops_rows_without_a_price_and_respects_the_limit(config):
    build_mart(config)
    service = AnalyticsService(config)

    frame = service.price_freight_pairs(KpiFilters(order_status="all"))

    assert list(frame.columns) == ["price", "freight_value"]
    assert len(frame) == 3
    assert frame["price"].isna().sum() == 0
    assert len(service.price_freight_pairs(KpiFilters(order_status="all"), limit=2)) == 2


def test_late_rates_by_region_returns_cell_counts(config):
    build_mart(config)

    frame = AnalyticsService(config).late_rates_by_region(KpiFilters(order_status="all"))
    cells = {(row.region, bool(row.is_late)): int(row.delivered_orders) for row in frame.itertuples()}

    assert cells[("Sudeste", True)] == 2
    assert cells[("Sudeste", False)] == 1
    assert cells[("Nordeste", False)] == 1
    assert ("Nordeste", True) not in cells


def test_stats_sql_only_touches_views_of_the_mart():
    views = {f"v_{table}" for table in VIEW_TABLES}

    for sql in (LATE_RATES_BY_STATE_SQL, LATE_RATES_BY_REGION_SQL, PRICE_FREIGHT_PAIRS_SQL):
        touched = set(re.findall(r"v_[a-z_]+", sql))
        assert touched
        assert touched <= views
