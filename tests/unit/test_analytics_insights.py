"""Truy vấn phân tích trên bộ mart nhỏ: mọi con số ở đây tính nhẩm được từ analytics_marts.py."""

from __future__ import annotations

import pytest

from src.analytics import insights
from src.analytics.connection import available_views, open_analysis_connection
from tests.unit.analytics_marts import DELIVERED_ORDERS, DELIVERED_REVENUE, write_small_warehouse


@pytest.fixture
def conn(config):
    write_small_warehouse(config)
    connection = open_analysis_connection(config)
    yield connection
    connection.close()


def _one(conn, key):
    return insights.run_analysis(conn, key).iloc[0]


def test_connection_exposes_mart_and_source_views(conn):
    views = available_views(conn)
    assert {"v_fact_orders", "v_fact_order_items", "v_agg_sales_daily", "v_dim_date"} <= views
    assert {"src_orders", "src_order_items", "src_payments", "src_reviews"} <= views


def test_connection_requires_marts(config):
    with pytest.raises(FileNotFoundError, match="src.pipeline"):
        open_analysis_connection(config)


def test_connection_without_sources(config):
    write_small_warehouse(config, with_sources=False)
    connection = open_analysis_connection(config)
    try:
        assert not any(view.startswith("src_") for view in available_views(connection))
    finally:
        connection.close()


def test_every_analysis_runs_and_declares_its_task(conn):
    frames = insights.run_all(conn)
    assert set(frames) == set(insights.ANALYSES)
    assert {item.task for item in insights.ANALYSES.values()} == {17, 18, 19, 20}
    # category_quality mặc định chỉ lấy danh mục từ 500 đơn nên rỗng trên bộ dữ liệu sáu đơn.
    assert [key for key, frame in frames.items() if frame.empty] == ["category_quality"]


def test_unknown_analysis_key_lists_valid_keys():
    with pytest.raises(KeyError, match="monthly_trend"):
        insights.analysis("khong_co")


def test_kpi_headline(conn):
    row = _one(conn, "kpi_headline")
    assert row.revenue == DELIVERED_REVENUE
    assert row.product_revenue == 470.0
    assert row.freight == 59.0
    assert row.orders == DELIVERED_ORDERS
    assert row["items"] == 6
    assert row.aov == 105.8
    # u1 đặt hai đơn (c1, c2): đếm theo customer_unique_id chỉ ra 4 người.
    assert row.customers == 4
    assert row.late_orders == 3
    assert row.late_rate_pct == 60.0
    # Mỗi đơn một đánh giá (mới nhất): o1=4, o2=1, o3=5, o4=2 -> 3,0. Tính theo dòng sẽ ra 3,4.
    assert row.avg_review_score == 3.0


def test_monthly_trend_skips_growth_across_gaps(conn):
    frame = insights.run_analysis(conn, "monthly_trend").set_index("period")
    assert list(frame.index) == ["2017-01", "2017-02", "2018-01", "2018-02"]
    assert frame.loc["2017-02", "revenue"] == 253.0
    assert frame.loc["2017-02", "orders"] == 2
    assert frame.loc["2017-02", "revenue_mom_pct"] == pytest.approx(53.33)
    # 2018-01 không liền kề 2017-02 nên không được tính tăng trưởng.
    assert frame["revenue_mom_pct"].isna().tolist() == [True, False, True, False]
    assert frame["revenue"].sum() == DELIVERED_REVENUE


def test_yearly_same_period_compares_equal_month_ranges(conn):
    frame = insights.run_analysis(conn, "yearly_same_period").set_index("year")
    assert frame.loc[2017, "revenue"] == 418.0
    assert frame.loc[2018, "revenue"] == 111.0
    assert frame["to_month"].tolist() == [2, 2]


def test_customer_repeat_uses_unique_id(conn):
    row = _one(conn, "customer_repeat")
    assert row.customers == 4
    assert row.repeat_customers == 1
    assert row.repeat_rate_pct == 25.0


def test_order_status_shares(conn):
    frame = insights.run_analysis(conn, "order_status").set_index("order_status")
    assert frame.loc["delivered", "orders"] == 5
    assert frame.loc["delivered", "share_pct"] == pytest.approx(83.33)
    assert frame.loc["canceled", "orders"] == 1


def test_payment_mix_is_measured_on_payment_rows(conn):
    frame = insights.run_analysis(conn, "payment_mix").set_index("payment_type")
    assert frame.loc["credit_card", "payment_value"] == 425.0
    assert frame.loc["credit_card", "orders"] == 3
    # o1 trả bằng hai phương thức nên tổng "số đơn có dùng" vượt số đơn delivered.
    assert frame["orders"].sum() == 6
    assert frame["value_share_pct"].sum() == pytest.approx(100.0, abs=0.02)


def test_category_ranking_revenue_is_additive_but_orders_are_not(conn):
    frame = insights.run_analysis(conn, "category_ranking")
    assert frame["category"].tolist() == ["cat_a", "cat_b", "unknown"]
    assert frame["revenue"].tolist() == [330.0, 188.0, 11.0]
    assert frame["revenue"].sum() == DELIVERED_REVENUE
    assert frame["orders"].tolist() == [2, 3, 1]
    assert frame["orders"].sum() > DELIVERED_ORDERS
    assert frame["cum_share_pct"].iloc[-1] == pytest.approx(100.0)
    assert frame["rank"].tolist() == [1, 2, 3]


def test_top_products_respects_limit(conn):
    assert len(insights.run_analysis(conn, "top_products", (2,))) == 2
    top = insights.run_analysis(conn, "top_products").iloc[0]
    assert (top.product_id, top.revenue, top.units) == ("p1", 330.0, 2)


def test_top_sellers_attach_order_level_quality_without_duplication(conn):
    frame = insights.run_analysis(conn, "top_sellers").set_index("seller_id")
    assert frame.loc["s1", "revenue"] == 441.0
    assert frame.loc["s2", "revenue"] == 88.0
    assert frame["revenue"].sum() == DELIVERED_REVENUE
    assert frame.loc["s1", "orders"] == 4
    # s1: o1=4, o2=1, o4=2, o6 không có đánh giá -> 7/3.
    assert frame.loc["s1", "avg_review_score"] == pytest.approx(2.33)
    assert frame.loc["s1", "late_rate_pct"] == 50.0
    assert frame["share_pct"].sum() == pytest.approx(100.0, abs=0.02)


def test_seller_concentration(conn):
    row = _one(conn, "seller_concentration")
    assert row.active_sellers == 2
    assert row.top10_sellers_share_pct == 100.0
    assert row.top_10pct_share_pct == pytest.approx(83.36)


def test_category_quality_uses_one_category_per_order(conn):
    frame = insights.run_analysis(conn, "category_quality", (1,)).set_index("category")
    assert frame["delivered_orders"].sum() == DELIVERED_ORDERS
    assert frame.loc["cat_a", "avg_review_score"] == 2.5
    assert frame.loc["cat_b", "late_rate_pct"] == 100.0
    assert insights.run_analysis(conn, "category_quality", (10,)).empty


def test_delivery_overview(conn):
    row = _one(conn, "delivery_overview")
    assert row.delivered_orders == 5
    assert row.missing_delivery_date == 1
    assert row.avg_delivery_days == 13.25
    assert row.late_orders == 3
    assert row.late_rate_pct == 60.0
    # o2 trễ 5 ngày 10 giờ, o3 trễ 10 giờ, o4 trễ 10 ngày 10 giờ.
    assert row.avg_days_late_when_late == pytest.approx(5.42)


def test_delivery_by_region_aggregates_freight_per_order_first(conn):
    frame = insights.run_analysis(conn, "delivery_by_region").set_index("region")
    assert frame.loc["Sudeste", "delivered_orders"] == 4
    assert frame.loc["Nordeste", "late_rate_pct"] == 100.0
    # Sudeste: o1 (10+5), o2 20, o3 3, o6 1 -> 39 / 4 đơn. Ghép thẳng dòng hàng sẽ chia cho 5.
    assert frame.loc["Sudeste", "avg_freight_per_order"] == 9.75
    states = insights.run_analysis(conn, "delivery_by_state")
    assert set(states["state"]) == {"SP", "RJ", "BA"}


def test_delivery_route_flags_cross_state_orders(conn):
    frame = insights.run_analysis(conn, "delivery_route").set_index("route")
    # Liên bang: o1 (một dòng từ RJ về SP) và o4 (SP về BA).
    assert frame.loc["Liên bang", "delivered_orders"] == 2
    assert frame.loc["Trong bang", "delivered_orders"] == 3
    assert frame.loc["Liên bang", "avg_delivery_days"] == 15.0


def test_delivery_buckets_exclude_missing_dates(conn):
    frame = insights.run_analysis(conn, "delivery_buckets")
    assert frame["orders"].sum() == 4
    assert frame["share_pct"].sum() == pytest.approx(100.0)


def test_review_distribution_counts_each_order_once(conn):
    frame = insights.run_analysis(conn, "review_distribution").set_index("review_score")
    # o1 có hai đánh giá (5 rồi 4) nhưng chỉ đánh giá mới nhất (4) được tính.
    assert frame["orders"].to_dict() == {1: 1, 2: 1, 4: 1, 5: 1}


def test_review_by_late_and_contingency(conn):
    frame = insights.run_analysis(conn, "review_by_late").set_index("delivery_status")
    assert frame.loc["Đúng hạn", "avg_review_score"] == 4.0
    assert frame.loc["Giao trễ", "avg_review_score"] == pytest.approx(2.67)
    assert frame.loc["Giao trễ", "low_review_pct"] == pytest.approx(66.67)

    table = insights.contingency_table(insights.run_analysis(conn, "review_late_contingency"))
    assert table == [[0, 0, 0, 1, 0], [1, 1, 0, 0, 1]]


def test_review_by_delay_and_confounder(conn):
    delay = insights.run_analysis(conn, "review_by_delay").set_index("delay_level")
    assert delay.loc["Trễ tới 3 ngày", "avg_review_score"] == 5.0
    assert delay["orders_with_review"].sum() == 4

    confounder = insights.run_analysis(conn, "review_confounder")
    multi = confounder[confounder["sellers_in_order"] == "Từ 2 người bán"]
    assert multi["orders_with_review"].tolist() == [1]
    assert multi["avg_review_score"].tolist() == [4.0]
