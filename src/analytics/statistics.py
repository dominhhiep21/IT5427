"""Năm phép kiểm định của tầng `stats` và bộ gom `skipped` (BR1.1–BR1.8)."""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pandas as pd
from scipy import stats as scipy_stats

from src.analytics.report import (
    STATUS_ERROR,
    AnalysisReport,
    ComparisonResult,
    CorrelationResult,
    GroupTestResult,
    ProportionResult,
    SeasonalResult,
    SkipEntry,
    StatsBlock,
    assemble_report,
    report_path,
    read_report,
)
from src.analytics.service import AnalyticsService
from src.common.kpis import REVENUE_DEFINITION
from src.common.logging import NullLogger
from src.common.types import KpiFilters

# Một hằng số duy nhất cho alpha và confidence (BR1.7).
ALPHA = 0.05


def confidence_for(alpha: float = ALPHA) -> float:
    """Độ tin cậy suy ra từ alpha, không truyền rời (BR1.7)."""

    return 1 - alpha


CONFIDENCE = confidence_for(ALPHA)

MIN_STATE_ORDERS = 100
MIN_CORRELATION_ROWS = 4
MIN_EXPECTED_CELL = 5.0
SEASONAL_PERIOD = 12
MIN_SEASONAL_MONTHS = 24
SEASONAL_METHOD = "classical_additive_12"
GROUP_TEST_NAME = "chi_square_region_late"

# Bốn kiểm định tuỳ chọn mới có mặt trong `skipped`; `late_rate` dừng cả tầng thay vì ghi null.
SKIP_TESTS = ("state_comparison", "correlation", "group_test", "seasonal")

PREVIOUS_REPORT_UNREADABLE_EVENT = "stats.previous_report_unreadable"


def z_critical(alpha: float = ALPHA) -> float:
    """Giá trị tới hạn hai phía của phân phối chuẩn tắc."""

    return float(scipy_stats.norm.ppf(1 - alpha / 2))


def wilson_interval(successes: int, total: int, z: float) -> tuple[float, float]:
    """Khoảng tin cậy Wilson cho một tỉ lệ, kẹp trong [0, 1]."""

    rate = successes / total
    denominator = 1 + z * z / total
    centre = (rate + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, centre - margin), min(1.0, centre + margin)


def late_rate(delivered_orders: int, late_orders: int, alpha: float = ALPHA) -> ProportionResult:
    """BR1.1 — tỉ lệ giao trễ trên đơn đã giao; không có đơn nào thì dừng cả tầng."""

    if delivered_orders <= 0:
        raise ValueError("Không có đơn đã giao: tầng stats dừng và không ghi báo cáo (BR1.1).")
    rate = late_orders / delivered_orders
    low, high = wilson_interval(late_orders, delivered_orders, z_critical(alpha))
    return ProportionResult(
        successes=late_orders,
        total=delivered_orders,
        rate=rate,
        ci_low=min(low, rate),
        ci_high=max(high, rate),
    )


def compare_states(
    rates: pd.DataFrame, alpha: float = ALPHA
) -> tuple[list[ComparisonResult], SkipEntry | None]:
    """BR1.2 — bang tỉ lệ trễ cao nhất so với thấp nhất trong các bang đủ ngưỡng đơn đã giao."""

    if rates.empty:
        return [], SkipEntry("state_comparison", "chưa có bang nào có đơn đã giao")
    eligible = rates[rates["delivered_orders"] >= MIN_STATE_ORDERS].copy()
    excluded = int(rates.loc[rates["delivered_orders"] < MIN_STATE_ORDERS, "delivered_orders"].sum())
    if len(eligible) < 2:
        return [], SkipEntry(
            "state_comparison",
            f"chỉ {len(eligible)} bang đạt ngưỡng {MIN_STATE_ORDERS} đơn đã giao, cần ít nhất 2",
        )
    eligible["rate"] = eligible["late_orders"] / eligible["delivered_orders"]
    top = eligible.sort_values(["rate", "state"], ascending=[False, True]).iloc[0]
    bottom = (
        eligible[eligible["state"] != top["state"]]
        .sort_values(["rate", "state"], ascending=[True, True])
        .iloc[0]
    )

    first_orders = int(top["delivered_orders"])
    second_orders = int(bottom["delivered_orders"])
    first_rate = float(top["late_orders"]) / first_orders
    second_rate = float(bottom["late_orders"]) / second_orders
    difference = first_rate - second_rate
    pooled = (float(top["late_orders"]) + float(bottom["late_orders"])) / (first_orders + second_orders)
    error = math.sqrt(pooled * (1 - pooled) * (1 / first_orders + 1 / second_orders))
    z = difference / error if error > 0 else 0.0
    p_value = min(1.0, max(0.0, 2 * (1 - float(scipy_stats.norm.cdf(abs(z))))))

    critical = z_critical(alpha)
    first_low, first_high = wilson_interval(int(top["late_orders"]), first_orders, critical)
    second_low, second_high = wilson_interval(int(bottom["late_orders"]), second_orders, critical)
    lower = difference - math.sqrt((first_rate - first_low) ** 2 + (second_high - second_rate) ** 2)
    upper = difference + math.sqrt((first_high - first_rate) ** 2 + (second_rate - second_low) ** 2)

    return [
        ComparisonResult(
            first=str(top["state"]),
            second=str(bottom["state"]),
            difference=difference,
            z=z,
            p_value=p_value,
            ci_low=min(lower, difference),
            ci_high=max(upper, difference),
            significant=p_value < alpha,
            excluded=excluded,
        )
    ], None


def price_freight_correlation(
    pairs: pd.DataFrame, alpha: float = ALPHA
) -> tuple[CorrelationResult | None, SkipEntry | None]:
    """BR1.3 — tương quan Pearson giữa giá hàng và phí vận chuyển, khoảng tin cậy Fisher."""

    frame = pairs.dropna(subset=["price", "freight_value"]) if not pairs.empty else pairs
    n = len(frame)
    if n < MIN_CORRELATION_ROWS:
        return None, SkipEntry(
            "correlation",
            f"chỉ {n} dòng hàng có đủ giá và phí, cần ít nhất {MIN_CORRELATION_ROWS}",
        )
    price = frame["price"].astype("float64")
    freight = frame["freight_value"].astype("float64")
    if float(price.std()) == 0.0 or float(freight.std()) == 0.0:
        return None, SkipEntry(
            "correlation",
            "giá hoặc phí không đổi trên mọi dòng nên hệ số tương quan không xác định",
        )
    r = float(scipy_stats.pearsonr(price, freight).statistic)

    critical = z_critical(alpha)
    clipped = max(-(1 - 1e-12), min(1 - 1e-12, r))
    centre = math.atanh(clipped)
    error = 1 / math.sqrt(n - 3)
    lower = math.tanh(centre - critical * error)
    upper = math.tanh(centre + critical * error)
    return (
        CorrelationResult(r=r, n=n, ci_low=min(lower, r), ci_high=max(upper, r)),
        None,
    )


def region_late_test(
    rows: pd.DataFrame, alpha: float = ALPHA
) -> tuple[GroupTestResult | None, SkipEntry | None]:
    """BR1.4 — kiểm định độc lập vùng × trễ, chỉ chạy khi mọi ô kỳ vọng đạt tối thiểu 5."""

    if rows.empty:
        return None, SkipEntry("group_test", "chưa có dòng nào của bảng vùng × trễ")
    frame = rows.dropna(subset=["region"])
    late = frame[frame["is_late"].astype(bool)].groupby("region")["delivered_orders"].sum()
    on_time = frame[~frame["is_late"].astype(bool)].groupby("region")["delivered_orders"].sum()
    regions = sorted(frame["region"].astype(str).unique())
    if len(regions) < 2:
        return None, SkipEntry("group_test", "cần ít nhất 2 vùng có đơn đã giao")
    table = pd.DataFrame(
        {
            "late": late.reindex(regions, fill_value=0),
            "on_time": on_time.reindex(regions, fill_value=0),
        }
    ).astype("float64")

    row_totals = table.sum(axis=1).to_numpy(dtype="float64")
    column_totals = table.sum(axis=0).to_numpy(dtype="float64")
    expected = row_totals[:, None] * column_totals[None, :] / row_totals.sum()
    min_expected = float(expected.min())
    if min_expected < MIN_EXPECTED_CELL:
        return None, SkipEntry(
            "group_test",
            f"ô kỳ vọng nhỏ nhất là {min_expected:.2f}, dưới ngưỡng {MIN_EXPECTED_CELL:g}",
        )
    statistic, p_value, dof, _ = scipy_stats.chi2_contingency(table.to_numpy(dtype="float64"), correction=False)
    return (
        GroupTestResult(
            test=GROUP_TEST_NAME,
            statistic=float(statistic),
            p_value=float(p_value),
            dof=int(dof),
            min_expected=min_expected,
        ),
        None,
    )


def seasonal_decomposition(
    monthly: pd.DataFrame,
) -> tuple[SeasonalResult | None, SkipEntry | None]:
    """BR1.5 — phân rã cộng tính cổ điển chu kỳ 12, tháng thiếu điền 0, tối thiểu 24 tháng."""

    if monthly.empty:
        return None, SkipEntry("seasonal", "chưa có tháng nào có doanh thu delivered")
    frame = (
        monthly.assign(
            revenue=monthly["revenue"].astype("float64"),
            stamp=monthly["year"].astype(int) * 12 + (monthly["month"].astype(int) - 1),
        )
        .groupby("stamp", as_index=True)["revenue"]
        .sum()
    )
    axis = list(range(int(frame.index.min()), int(frame.index.max()) + 1))
    if len(axis) < MIN_SEASONAL_MONTHS:
        return None, SkipEntry(
            "seasonal",
            f"trục tháng liên tục chỉ dài {len(axis)} tháng, cần ít nhất {MIN_SEASONAL_MONTHS}",
        )
    observed = [float(frame.get(index, 0.0)) for index in axis]
    series = pd.Series(observed, index=axis, dtype="float64")
    # Trung bình động giữa, cửa sổ thu hẹp dần ở hai đầu thay vì bỏ trống (BR1.5, entities.md).
    trend = series.rolling(window=SEASONAL_PERIOD, center=True, min_periods=1).mean()
    detrended = series - trend
    # Chỉ số mùa vụ gắn với tháng trong năm (stamp % 12), không với vị trí đầu chuỗi.
    by_month = detrended.groupby(detrended.index % SEASONAL_PERIOD).mean()
    by_month = by_month - by_month.mean()
    seasonal = pd.Series(
        [float(by_month[index % SEASONAL_PERIOD]) for index in series.index],
        index=series.index,
        dtype="float64",
    )
    residual = series - trend - seasonal
    return (
        SeasonalResult(
            revenue_definition=REVENUE_DEFINITION,
            method=SEASONAL_METHOD,
            period=SEASONAL_PERIOD,
            months=[f"{index // 12:04d}-{index % 12 + 1:02d}" for index in axis],
            observed=observed,
            trend=[float(value) for value in trend],
            seasonal=[float(value) for value in seasonal],
            residual=[float(value) for value in residual],
        ),
        None,
    )


def ordered_skips(entries: list[SkipEntry | None]) -> list[SkipEntry]:
    """Mỗi tên kiểm định xuất hiện tối đa một lần trong `skipped` (BR1.6)."""

    seen: dict[str, SkipEntry] = {}
    for entry in entries:
        if entry is not None and entry.test not in seen:
            seen[entry.test] = entry
    return [seen[test] for test in SKIP_TESTS if test in seen]


def collect_stats(service, filters: KpiFilters, generated_at: str, alpha: float = ALPHA) -> StatsBlock:
    """Đọc dữ liệu một lần cho mỗi phép, rồi dựng `StatsBlock` với `skipped` gom đủ (BR1.6, PD-1)."""

    summary = service.kpi_summary(filters)
    proportion = late_rate(int(summary["delivered_orders"]), int(summary["late_orders"]), alpha)
    comparisons, comparison_skip = compare_states(service.late_rates_by_state(filters), alpha)
    correlation, correlation_skip = price_freight_correlation(service.price_freight_pairs(filters), alpha)
    group_test, group_skip = region_late_test(service.late_rates_by_region(filters), alpha)
    seasonal, seasonal_skip = seasonal_decomposition(service.revenue_by_period(filters, "month"))
    return StatsBlock(
        generated_at=generated_at,
        alpha=alpha,
        confidence=confidence_for(alpha),
        late_rate=proportion,
        comparisons=comparisons,
        correlation=correlation,
        group_test=group_test,
        seasonal=seasonal,
        skipped=ordered_skips([comparison_skip, correlation_skip, group_skip, seasonal_skip]),
    )


def build_analysis_report(config, generated_at: str | None = None, logger=None) -> AnalysisReport:
    """Dựng báo cáo mới qua `assemble_report` — ADR-008: đây không phải nơi dựng khối."""

    logger = logger or NullLogger()
    stamp = generated_at or datetime.now(timezone.utc).isoformat()
    path = report_path(config)
    previous = read_report(path)
    if previous.status == STATUS_ERROR:
        logger.warning(
            PREVIOUS_REPORT_UNREADABLE_EVENT,
            path=str(path),
            message=previous.message,
        )
    stats_block = collect_stats(AnalyticsService(config), KpiFilters(), stamp)
    return assemble_report(config, stats=stats_block, model=None, generated_at=stamp)
