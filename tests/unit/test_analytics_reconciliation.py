"""Bộ đối soát: đạt trên dữ liệu sạch, và phải bắt được lỗi khi dữ liệu bị làm hỏng có chủ đích."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics.connection import open_analysis_connection
from src.analytics.reconciliation import FAIL, INFO, PASS, SKIP, run_reconciliation
from tests.unit.analytics_marts import build_small_marts, write_small_warehouse

SMALL_BASELINE = {
    "revenue_delivered": 529.0,
    "delivered_orders": 5,
    "aov": 105.8,
    "late_orders": 3,
    "late_rate_pct": 60.0,
}


def _reconcile(config, marts=None, *, with_sources=True, baseline=SMALL_BASELINE):
    write_small_warehouse(config, marts, with_sources=with_sources)
    conn = open_analysis_connection(config)
    try:
        return run_reconciliation(conn, baseline)
    finally:
        conn.close()


def test_clean_data_passes_every_hard_check(config):
    result = _reconcile(config)
    assert result.passed
    assert result.has_sources
    assert result.counts() == {PASS: 8, FAIL: 0, INFO: 9, SKIP: 0}
    assert [check.check_id for check in result.checks] == [f"DS-{number:02d}" for number in range(1, 18)]
    assert all(check.sql for check in result.checks)


def test_three_independent_paths_agree(config):
    result = _reconcile(config)
    assert result.get("DS-05").values == {
        "fact_revenue": 529.0,
        "aggregate_revenue": 529.0,
        "source_revenue": 529.0,
    }
    assert set(result.get("DS-06").values.values()) == {5}
    # o6 thiếu ngày giao: đường tính từ CSV cũng không được coi nó là trễ.
    assert set(result.get("DS-07").values.values()) == {3}


def test_fanout_traps_are_measured(config):
    result = _reconcile(config)

    payments = result.get("DS-09")
    assert payments.status == INFO
    # o1 có 2 dòng hàng x 2 thanh toán: doanh thu 165 của nó bị tính hai lần.
    assert payments.values["correct_revenue"] == 529.0
    assert payments.values["naive_join_revenue"] == 694.0
    assert payments.values["inflation"] == 165.0
    assert (payments.values["item_rows"], payments.values["joined_rows"]) == (6, 8)

    reviews = result.get("DS-10")
    # o1 nhân đôi (+165) trong khi o6 không có đánh giá bị rơi (-11).
    assert reviews.values["naive_join_revenue"] == 683.0
    assert reviews.values["delivered_without_review"] == 1

    orders = result.get("DS-11")
    assert orders.values["distinct_orders"] == 5
    assert orders.values["summed_orders_in_aggregate"] == 6
    assert orders.values["orders_with_many_categories"] == 1

    ratio = result.get("DS-12")
    assert ratio.values["aov_overall"] == 105.8
    # (165/1 + 253/2 + 100/1 + 11/1) / 4 tháng = 100,63: trung bình của trung bình cho số khác.
    assert ratio.values["mean_of_monthly_aov"] == pytest.approx(100.63)


def test_known_differences_are_reported_not_failed(config):
    result = _reconcile(config)

    money = result.get("DS-13")
    assert money.status == INFO
    assert money.values["orders_compared"] == 6
    assert money.values["orders_mismatched"] == 1
    assert money.values["orders_paid_more"] == 1
    assert money.values["paid_more_installment_pct"] == 100.0
    assert money.values["difference"] == 5.0

    late = result.get("DS-14")
    # o3 giao lúc 10:00 của chính ngày dự kiến: trễ theo mốc thời gian, không trễ theo ngày lịch.
    assert (late.values["late_by_timestamp"], late.values["late_by_calendar_day"]) == (3, 2)
    assert late.values["same_day_orders"] == 1

    assert result.get("DS-15").values["delivered_without_date"] == 1

    reviews = result.get("DS-16")
    assert (reviews.values["review_rows"], reviews.values["orders_with_review"]) == (6, 5)
    assert reviews.values["extra_review_rows"] == 1
    assert reviews.values["avg_score_row_level"] == 3.4
    assert reviews.values["avg_score_order_level"] == 3.0

    categories = result.get("DS-17")
    assert categories.values["categories_differing"] == 1
    assert (categories.values["sum_orders_any_item"], categories.values["sum_orders_dominant"]) == (6, 5)


def test_missing_sources_skip_source_checks_only(config):
    result = _reconcile(config, with_sources=False)
    assert result.passed
    assert not result.has_sources
    assert result.get("DS-04").status == SKIP
    assert "source_revenue" not in result.get("DS-05").values
    assert result.get("DS-05").status == PASS


def test_baseline_mismatch_fails(config):
    result = _reconcile(config, baseline={**SMALL_BASELINE, "revenue_delivered": 530.0})
    check = result.get("DS-08")
    assert check.status == FAIL
    assert "revenue_delivered" in check.conclusion
    assert not result.passed


def test_without_baseline_only_records_values(config):
    check = _reconcile(config, baseline=None).get("DS-08")
    assert check.status == INFO
    assert check.values["revenue_delivered"] == 529.0


def test_duplicate_fact_row_is_caught(config):
    marts = build_small_marts()
    items = marts["fact_order_items"]
    marts["fact_order_items"] = pd.concat([items, items.iloc[[0]]], ignore_index=True)
    result = _reconcile(config, marts)
    assert result.get("DS-01").status == FAIL
    # Dòng trùng làm doanh thu trong fact (639) lệch khỏi aggregate và CSV gốc (529).
    assert result.get("DS-05").status == FAIL
    assert not result.passed


def test_duplicate_dimension_key_is_caught(config):
    marts = build_small_marts()
    products = marts["dim_product"]
    marts["dim_product"] = pd.concat([products, products.iloc[[0]]], ignore_index=True)
    result = _reconcile(config, marts)
    assert result.get("DS-02").status == FAIL
    assert result.get("DS-02").values["duplicate_products"] == 1


def test_orphan_fact_row_is_caught(config):
    marts = build_small_marts()
    marts["dim_seller"] = marts["dim_seller"][marts["dim_seller"]["seller_id"] != "s2"]
    result = _reconcile(config, marts)
    check = result.get("DS-03")
    assert check.status == FAIL
    assert check.values["items_without_seller"] == 2


def test_stale_aggregate_is_caught(config):
    marts = build_small_marts()
    stale = marts["agg_delivery_daily"].copy()
    stale.loc[stale.index[0], "late_orders"] += 1
    stale.loc[stale.index[0], "delivered_orders"] += 1
    marts["agg_delivery_daily"] = stale
    result = _reconcile(config, marts)
    assert result.get("DS-06").status == FAIL
    assert result.get("DS-07").status == FAIL


def test_result_serialises_to_plain_json_types(config):
    import json

    payload = _reconcile(config).to_dict()
    assert payload["passed"] is True
    assert payload["counts"][PASS] == 8
    assert json.loads(json.dumps(payload))["checks"][0]["check_id"] == "DS-01"
