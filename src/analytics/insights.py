"""Bộ truy vấn phân tích trên star schema (mục 17–20 của bảng phân công).

Mỗi phân tích là một `Analysis`: câu hỏi nghiệp vụ + một câu SQL chạy trên các view `v_*`.
Ba quy ước xuyên suốt, cũng là ba điều cần nói khi bảo vệ:

1. **Một định nghĩa doanh thu**: `item_total = price + freight_value` của dòng hàng thuộc đơn
   `delivered` (khớp `src/common/kpis.py::REVENUE_DEFINITION` và baseline 15.419.773,75 BRL).
2. **Grain trước, JOIN sau**: bảng nhiều dòng trên một đơn (dòng hàng, thanh toán, đánh giá)
   luôn được gộp về grain đơn hàng trong CTE trước khi ghép, để không nhân bản số liệu.
3. **Số đơn là số đo không cộng dồn**: luôn `COUNT(DISTINCT order_id)` ở grain gốc, không
   cộng số đơn của các nhóm con (một đơn có thể thuộc nhiều danh mục, nhiều người bán).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

# Mỗi đơn chỉ giữ MỘT đánh giá (mới nhất) để phân tích ở grain đơn hàng:
# 547 đơn có hơn một đánh giá, nếu ghép thẳng thì các đơn đó bị đếm nhiều lần.
REVIEW_PER_ORDER_CTE = """review_per_order AS (
        SELECT order_id, review_score
        FROM v_fact_reviews
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY order_id ORDER BY date_key DESC, review_id DESC
        ) = 1
    )"""

# Số ngày lệch so với ngày giao dự kiến: dương = trễ, âm = sớm.
DAYS_VS_ESTIMATE = "(epoch(o.order_delivered_customer_date) - epoch(o.order_estimated_delivery_date)) / 86400.0"


@dataclass(frozen=True)
class Analysis:
    """Một phân tích: thuộc mục nào, trả lời câu hỏi gì, bằng câu SQL nào."""

    key: str
    task: int
    title: str
    question: str
    sql: str
    params: tuple = ()


def _delivery_by(level: str) -> str:
    columns = "c.region" if level == "region" else "c.state, c.region"
    return f"""
    WITH freight_per_order AS (
        SELECT order_id, SUM(freight_value) AS freight
        FROM v_fact_order_items
        GROUP BY order_id
    )
    SELECT {columns},
           COUNT(*) AS delivered_orders,
           ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
           ROUND(MEDIAN(o.delivery_days), 2) AS median_delivery_days,
           ROUND(QUANTILE_CONT(o.delivery_days, 0.9), 2) AS p90_delivery_days,
           CAST(SUM(o.is_late::INT) AS BIGINT) AS late_orders,
           ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct,
           ROUND(AVG(fp.freight), 2) AS avg_freight_per_order
    FROM v_fact_orders o
    JOIN v_dim_customer c ON o.customer_id = c.customer_id
    LEFT JOIN freight_per_order fp ON o.order_id = fp.order_id
    WHERE o.is_delivered
    GROUP BY {columns}
    ORDER BY late_rate_pct DESC, {columns}
    """


_ANALYSES: tuple[Analysis, ...] = (
    # ------------------------------------------------------------------ Mục 17: kinh doanh
    Analysis(
        key="kpi_headline",
        task=17,
        title="KPI tổng quan",
        question="Toàn kỳ, sàn bán được bao nhiêu, bao nhiêu đơn, giá trị đơn trung bình là bao nhiêu?",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE},
    sales AS (
        SELECT SUM(item_total) AS revenue,
               SUM(price) AS product_revenue,
               SUM(freight_value) AS freight,
               COUNT(DISTINCT order_id) AS orders,
               COUNT(*) AS items,
               COUNT(DISTINCT seller_id) AS sellers,
               COUNT(DISTINCT product_id) AS products
        FROM v_fact_order_items
        WHERE is_delivered
    ),
    delivery AS (
        SELECT COUNT(DISTINCT c.customer_unique_id) AS customers,
               COUNT(*) AS delivered_orders,
               CAST(SUM(o.is_late::INT) AS BIGINT) AS late_orders,
               AVG(o.delivery_days) AS avg_delivery_days,
               AVG(r.review_score) AS avg_review_score
        FROM v_fact_orders o
        JOIN v_dim_customer c ON o.customer_id = c.customer_id
        LEFT JOIN review_per_order r ON o.order_id = r.order_id
        WHERE o.is_delivered
    )
    SELECT ROUND(s.revenue, 2) AS revenue,
           ROUND(s.product_revenue, 2) AS product_revenue,
           ROUND(s.freight, 2) AS freight,
           ROUND(100.0 * s.freight / s.revenue, 2) AS freight_share_pct,
           s.orders, s.items,
           ROUND(s.revenue / s.orders, 2) AS aov,
           ROUND(1.0 * s.items / s.orders, 3) AS items_per_order,
           d.customers, s.sellers, s.products,
           d.late_orders,
           ROUND(100.0 * d.late_orders / d.delivered_orders, 2) AS late_rate_pct,
           ROUND(d.avg_delivery_days, 2) AS avg_delivery_days,
           ROUND(d.avg_review_score, 2) AS avg_review_score
    FROM sales s CROSS JOIN delivery d
    """,
    ),
    Analysis(
        key="monthly_trend",
        task=17,
        title="Doanh thu, số đơn, AOV theo tháng",
        question="Doanh thu và số đơn thay đổi thế nào theo thời gian? Tháng nào cao điểm?",
        sql="""
    WITH monthly AS (
        SELECT d.year, d.month,
               BOOL_OR(d.is_sparse_period) AS is_sparse_period,
               SUM(f.item_total) AS revenue,
               COUNT(DISTINCT f.order_id) AS orders,
               COUNT(*) AS items,
               SUM(f.freight_value) AS freight
        FROM v_fact_order_items f
        JOIN v_dim_date d ON f.date_key = d.date_key
        WHERE f.is_delivered
        GROUP BY d.year, d.month
    )
    SELECT printf('%d-%02d', year, month) AS period,
           is_sparse_period,
           ROUND(revenue, 2) AS revenue,
           orders,
           items,
           ROUND(revenue / orders, 2) AS aov,
           ROUND(100.0 * freight / revenue, 2) AS freight_share_pct,
           -- Chỉ tính tăng trưởng khi tháng trước liền kề và không thuộc giai đoạn thưa dữ liệu.
           CASE
               WHEN (year * 12 + month) - LAG(year * 12 + month) OVER w = 1
                    AND NOT LAG(is_sparse_period) OVER w
               THEN ROUND(100.0 * (revenue - LAG(revenue) OVER w) / LAG(revenue) OVER w, 2)
           END AS revenue_mom_pct
    FROM monthly
    WINDOW w AS (ORDER BY year, month)
    ORDER BY year, month
    """,
    ),
    Analysis(
        key="peak_days",
        task=17,
        title="Những ngày có nhiều đơn nhất",
        question="Có ngày nào đột biến đơn hàng không?",
        sql="""
    SELECT o.date_key AS order_date,
           COUNT(*) AS orders,
           ROUND(COUNT(*) / AVG(COUNT(*)) OVER (), 1) AS times_daily_average
    FROM v_fact_orders o
    WHERE o.is_delivered
    GROUP BY o.date_key
    ORDER BY orders DESC, o.date_key
    LIMIT ?
    """,
        params=(5,),
    ),
    Analysis(
        key="yearly_same_period",
        task=17,
        title="So sánh cùng kỳ năm trước",
        question="So cùng các tháng của năm trước, kinh doanh tăng trưởng bao nhiêu?",
        sql="""
    WITH base AS (
        SELECT d.year, d.month, f.item_total, f.order_id
        FROM v_fact_order_items f
        JOIN v_dim_date d ON f.date_key = d.date_key
        WHERE f.is_delivered
    ),
    last_year AS (SELECT MAX(year) AS y FROM base),
    cutoff AS (SELECT MAX(b.month) AS m FROM base b, last_year l WHERE b.year = l.y)
    SELECT b.year,
           MIN(b.month) AS from_month,
           MAX(b.month) AS to_month,
           ROUND(SUM(b.item_total), 2) AS revenue,
           COUNT(DISTINCT b.order_id) AS orders,
           ROUND(SUM(b.item_total) / COUNT(DISTINCT b.order_id), 2) AS aov
    FROM base b, last_year l, cutoff k
    WHERE b.year IN (l.y, l.y - 1) AND b.month <= k.m
    GROUP BY b.year
    ORDER BY b.year
    """,
    ),
    Analysis(
        key="weekday_pattern",
        task=17,
        title="Số đơn theo ngày trong tuần",
        question="Khách đặt hàng nhiều vào ngày nào trong tuần?",
        sql="""
    SELECT d.weekday AS weekday_index,
           CASE d.weekday
               WHEN 0 THEN 'Thứ Hai' WHEN 1 THEN 'Thứ Ba' WHEN 2 THEN 'Thứ Tư'
               WHEN 3 THEN 'Thứ Năm' WHEN 4 THEN 'Thứ Sáu' WHEN 5 THEN 'Thứ Bảy'
               ELSE 'Chủ nhật'
           END AS weekday,
           COUNT(DISTINCT f.order_id) AS orders,
           ROUND(SUM(f.item_total), 2) AS revenue,
           ROUND(100.0 * SUM(f.item_total) / SUM(SUM(f.item_total)) OVER (), 2) AS revenue_share_pct
    FROM v_fact_order_items f
    JOIN v_dim_date d ON f.date_key = d.date_key
    WHERE f.is_delivered
    GROUP BY d.weekday
    ORDER BY d.weekday
    """,
    ),
    Analysis(
        key="revenue_by_region",
        task=17,
        title="Doanh thu theo vùng của khách hàng",
        question="Doanh thu tập trung ở vùng nào của Brazil?",
        sql="""
    SELECT c.region,
           ROUND(SUM(f.item_total), 2) AS revenue,
           COUNT(DISTINCT f.order_id) AS orders,
           ROUND(SUM(f.item_total) / COUNT(DISTINCT f.order_id), 2) AS aov,
           ROUND(100.0 * SUM(f.item_total) / SUM(SUM(f.item_total)) OVER (), 2) AS revenue_share_pct,
           ROUND(100.0 * SUM(f.freight_value) / SUM(f.item_total), 2) AS freight_share_pct
    FROM v_fact_order_items f
    JOIN v_dim_customer c ON f.customer_id = c.customer_id
    WHERE f.is_delivered
    GROUP BY c.region
    ORDER BY revenue DESC, c.region
    """,
    ),
    Analysis(
        key="payment_mix",
        task=17,
        title="Cơ cấu phương thức thanh toán",
        question="Khách trả tiền bằng phương thức nào? (đo trên bảng thanh toán, không trộn với dòng hàng)",
        sql="""
    SELECT p.payment_type,
           COUNT(DISTINCT p.order_id) AS orders,
           COUNT(*) AS payment_rows,
           ROUND(SUM(p.payment_value), 2) AS payment_value,
           ROUND(100.0 * SUM(p.payment_value) / SUM(SUM(p.payment_value)) OVER (), 2) AS value_share_pct,
           ROUND(AVG(p.payment_installments), 2) AS avg_installments
    FROM v_fact_payments p
    JOIN v_fact_orders o ON p.order_id = o.order_id
    WHERE o.is_delivered
    GROUP BY p.payment_type
    ORDER BY payment_value DESC, p.payment_type
    """,
    ),
    Analysis(
        key="customer_repeat",
        task=17,
        title="Khách hàng mua lại",
        question="Bao nhiêu khách quay lại mua lần hai? (đếm theo customer_unique_id, không phải customer_id)",
        sql="""
    WITH per_customer AS (
        SELECT c.customer_unique_id, COUNT(*) AS orders
        FROM v_fact_orders o
        JOIN v_dim_customer c ON o.customer_id = c.customer_id
        WHERE o.is_delivered
        GROUP BY c.customer_unique_id
    )
    SELECT COUNT(*) AS customers,
           CAST(SUM(orders) AS BIGINT) AS orders,
           CAST(SUM((orders > 1)::INT) AS BIGINT) AS repeat_customers,
           ROUND(100.0 * AVG((orders > 1)::INT), 2) AS repeat_rate_pct,
           ROUND(AVG(orders), 3) AS orders_per_customer,
           MAX(orders) AS max_orders_one_customer
    FROM per_customer
    """,
    ),
    Analysis(
        key="order_status",
        task=17,
        title="Phân bố trạng thái đơn hàng",
        question="Bao nhiêu phần trăm đơn được giao thành công? (cơ sở để chỉ tính KPI trên đơn delivered)",
        sql="""
    SELECT order_status,
           COUNT(*) AS orders,
           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
           CAST(SUM(has_items::INT) AS BIGINT) AS orders_with_items
    FROM v_fact_orders
    GROUP BY order_status
    ORDER BY orders DESC, order_status
    """,
    ),
    # --------------------------------------------------------- Mục 18: sản phẩm và người bán
    Analysis(
        key="category_ranking",
        task=18,
        title="Xếp hạng danh mục theo doanh thu",
        question="Danh mục nào mang lại nhiều doanh thu nhất? Doanh thu tập trung đến mức nào?",
        sql="""
    WITH by_category AS (
        SELECT p.category,
               MIN(p.category_english) AS category_english,
               SUM(f.item_total) AS revenue,
               SUM(f.price) AS price_total,
               COUNT(DISTINCT f.order_id) AS orders,
               COUNT(*) AS items
        FROM v_fact_order_items f
        JOIN v_dim_product p ON f.product_id = p.product_id
        WHERE f.is_delivered
        GROUP BY p.category
    )
    SELECT ROW_NUMBER() OVER (ORDER BY revenue DESC, category) AS rank,
           category,
           category_english,
           ROUND(revenue, 2) AS revenue,
           orders,
           items,
           ROUND(revenue / orders, 2) AS revenue_per_order,
           ROUND(price_total / items, 2) AS avg_item_price,
           ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS share_pct,
           ROUND(100.0 * SUM(revenue) OVER (
               ORDER BY revenue DESC, category ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) / SUM(revenue) OVER (), 2) AS cum_share_pct
    FROM by_category
    ORDER BY rank
    """,
    ),
    Analysis(
        key="top_products",
        task=18,
        title="Sản phẩm bán chạy nhất theo doanh thu",
        question="Những sản phẩm nào đóng góp doanh thu lớn nhất?",
        sql="""
    SELECT ROW_NUMBER() OVER (ORDER BY SUM(f.item_total) DESC, f.product_id) AS rank,
           f.product_id,
           p.category,
           ROUND(SUM(f.item_total), 2) AS revenue,
           COUNT(*) AS units,
           COUNT(DISTINCT f.order_id) AS orders,
           ROUND(AVG(f.price), 2) AS avg_price
    FROM v_fact_order_items f
    JOIN v_dim_product p ON f.product_id = p.product_id
    WHERE f.is_delivered
    GROUP BY f.product_id, p.category
    ORDER BY rank
    LIMIT ?
    """,
        params=(10,),
    ),
    Analysis(
        key="top_sellers",
        task=18,
        title="Người bán hàng đầu: doanh thu kèm chất lượng phục vụ",
        question="Người bán nào lớn nhất, và họ có giao đúng hạn, được đánh giá tốt không?",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE},
    seller_orders AS (
        -- Gộp về grain (người bán, đơn) trước khi gắn đánh giá và cờ giao trễ của đơn.
        SELECT seller_id, order_id, SUM(item_total) AS revenue, COUNT(*) AS items
        FROM v_fact_order_items
        WHERE is_delivered
        GROUP BY seller_id, order_id
    ),
    by_seller AS (
        SELECT so.seller_id,
               SUM(so.revenue) AS revenue,
               COUNT(*) AS orders,
               SUM(so.items) AS items,
               AVG(r.review_score) AS avg_review_score,
               100.0 * AVG(o.is_late::INT) AS late_rate_pct
        FROM seller_orders so
        JOIN v_fact_orders o ON so.order_id = o.order_id
        LEFT JOIN review_per_order r ON so.order_id = r.order_id
        GROUP BY so.seller_id
    )
    SELECT ROW_NUMBER() OVER (ORDER BY b.revenue DESC, b.seller_id) AS rank,
           b.seller_id,
           s.state,
           ROUND(b.revenue, 2) AS revenue,
           b.orders,
           CAST(b.items AS BIGINT) AS items,
           ROUND(b.revenue / b.orders, 2) AS revenue_per_order,
           ROUND(100.0 * b.revenue / SUM(b.revenue) OVER (), 2) AS share_pct,
           ROUND(b.avg_review_score, 2) AS avg_review_score,
           ROUND(b.late_rate_pct, 2) AS late_rate_pct
    FROM by_seller b
    JOIN v_dim_seller s ON b.seller_id = s.seller_id
    ORDER BY rank
    LIMIT ?
    """,
        params=(10,),
    ),
    Analysis(
        key="seller_concentration",
        task=18,
        title="Mức độ tập trung doanh thu theo người bán",
        question="Doanh thu phụ thuộc vào một nhóm nhỏ người bán đến mức nào (quy luật Pareto)?",
        sql="""
    WITH by_seller AS (
        SELECT seller_id, SUM(item_total) AS revenue
        FROM v_fact_order_items
        WHERE is_delivered
        GROUP BY seller_id
    ),
    ranked AS (
        SELECT revenue,
               ROW_NUMBER() OVER (ORDER BY revenue DESC, seller_id) AS rn,
               COUNT(*) OVER () AS n,
               SUM(revenue) OVER () AS total
        FROM by_seller
    )
    SELECT MAX(n) AS active_sellers,
           ROUND(MEDIAN(revenue), 2) AS median_seller_revenue,
           ROUND(100.0 * SUM(CASE WHEN rn <= 10 THEN revenue ELSE 0 END) / MAX(total), 2) AS top10_sellers_share_pct,
           ROUND(100.0 * SUM(CASE WHEN rn <= CEIL(n * 0.01) THEN revenue ELSE 0 END) / MAX(total), 2)
               AS top_1pct_share_pct,
           ROUND(100.0 * SUM(CASE WHEN rn <= CEIL(n * 0.10) THEN revenue ELSE 0 END) / MAX(total), 2)
               AS top_10pct_share_pct,
           ROUND(100.0 * SUM(CASE WHEN rn <= CEIL(n * 0.20) THEN revenue ELSE 0 END) / MAX(total), 2)
               AS top_20pct_share_pct
    FROM ranked
    """,
    ),
    Analysis(
        key="seller_by_state",
        task=18,
        title="Người bán theo bang",
        question="Người bán tập trung ở bang nào?",
        sql="""
    SELECT s.state,
           COUNT(DISTINCT f.seller_id) AS sellers,
           ROUND(SUM(f.item_total), 2) AS revenue,
           ROUND(100.0 * SUM(f.item_total) / SUM(SUM(f.item_total)) OVER (), 2) AS revenue_share_pct
    FROM v_fact_order_items f
    JOIN v_dim_seller s ON f.seller_id = s.seller_id
    WHERE f.is_delivered
    GROUP BY s.state
    ORDER BY revenue DESC, s.state
    LIMIT ?
    """,
        params=(5,),
    ),
    Analysis(
        key="category_quality",
        task=18,
        title="Danh mục theo chất lượng trải nghiệm",
        question="Danh mục nào bị đánh giá thấp hoặc hay giao trễ? (xếp theo điểm đánh giá, không theo doanh thu)",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE}
    -- fact_orders.category là danh mục đại diện của đơn: mỗi đơn đúng một danh mục,
    -- nên điểm đánh giá và cờ giao trễ của đơn không bị chia hay nhân theo dòng hàng.
    SELECT o.category,
           COUNT(*) AS delivered_orders,
           ROUND(AVG(r.review_score), 2) AS avg_review_score,
           ROUND(100.0 * AVG((r.review_score <= 2)::INT), 2) AS low_review_pct,
           ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct,
           ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days
    FROM v_fact_orders o
    LEFT JOIN review_per_order r ON o.order_id = r.order_id
    WHERE o.is_delivered
    GROUP BY o.category
    HAVING COUNT(*) >= ?
    ORDER BY avg_review_score ASC, o.category
    """,
        params=(500,),
    ),
    # ------------------------------------------------------------------ Mục 19: giao vận
    Analysis(
        key="delivery_overview",
        task=19,
        title="Tổng quan giao vận",
        question="Giao một đơn mất bao lâu? Bao nhiêu phần trăm đơn giao trễ, và trễ bao nhiêu ngày?",
        sql=f"""
    WITH delivered AS (
        SELECT o.delivery_days, o.is_late, {DAYS_VS_ESTIMATE} AS days_vs_estimate
        FROM v_fact_orders o
        WHERE o.is_delivered
    )
    SELECT COUNT(*) AS delivered_orders,
           CAST(SUM((delivery_days IS NULL)::INT) AS BIGINT) AS missing_delivery_date,
           ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
           ROUND(MEDIAN(delivery_days), 2) AS median_delivery_days,
           ROUND(QUANTILE_CONT(delivery_days, 0.9), 2) AS p90_delivery_days,
           CAST(SUM(is_late::INT) AS BIGINT) AS late_orders,
           ROUND(100.0 * AVG(is_late::INT), 2) AS late_rate_pct,
           ROUND(AVG(CASE WHEN is_late THEN days_vs_estimate END), 2) AS avg_days_late_when_late,
           ROUND(AVG(CASE WHEN NOT is_late THEN -days_vs_estimate END), 2) AS avg_days_early_when_on_time
    FROM delivered
    """,
    ),
    Analysis(
        key="delivery_by_region",
        task=19,
        title="Giao vận theo vùng",
        question="Vùng nào giao lâu và trễ nhiều nhất?",
        sql=_delivery_by("region"),
    ),
    Analysis(
        key="delivery_by_state",
        task=19,
        title="Giao vận theo bang",
        question="Bang nào có tỷ lệ giao trễ cao nhất, thấp nhất?",
        sql=_delivery_by("state"),
    ),
    Analysis(
        key="delivery_monthly",
        task=19,
        title="Giao vận theo tháng đặt hàng",
        question="Chất lượng giao vận thay đổi thế nào theo thời gian?",
        sql="""
    SELECT printf('%d-%02d', d.year, d.month) AS period,
           COUNT(*) AS delivered_orders,
           ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
           CAST(SUM(o.is_late::INT) AS BIGINT) AS late_orders,
           ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct
    FROM v_fact_orders o
    JOIN v_dim_date d ON o.date_key = d.date_key
    WHERE o.is_delivered
    GROUP BY d.year, d.month
    ORDER BY d.year, d.month
    """,
    ),
    Analysis(
        key="delivery_buckets",
        task=19,
        title="Phân bố thời gian giao hàng",
        question="Phần lớn đơn được giao trong bao nhiêu ngày?",
        sql="""
    WITH bucketed AS (
        SELECT CASE
                   WHEN delivery_days <= 7 THEN 1
                   WHEN delivery_days <= 14 THEN 2
                   WHEN delivery_days <= 21 THEN 3
                   WHEN delivery_days <= 28 THEN 4
                   ELSE 5
               END AS bucket_index,
               is_late
        FROM v_fact_orders
        WHERE is_delivered AND delivery_days IS NOT NULL
    )
    SELECT bucket_index,
           CASE bucket_index
               WHEN 1 THEN '0–7 ngày' WHEN 2 THEN '8–14 ngày' WHEN 3 THEN '15–21 ngày'
               WHEN 4 THEN '22–28 ngày' ELSE 'Trên 28 ngày'
           END AS delivery_time,
           COUNT(*) AS orders,
           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
           ROUND(100.0 * AVG(is_late::INT), 2) AS late_rate_pct
    FROM bucketed
    GROUP BY bucket_index
    ORDER BY bucket_index
    """,
    ),
    Analysis(
        key="delivery_route",
        task=19,
        title="Giao trong bang so với giao liên bang",
        question="Khoảng cách (người bán và khách khác bang) ảnh hưởng thế nào tới thời gian giao?",
        sql="""
    WITH route AS (
        -- Một đơn là "liên bang" nếu có ít nhất một dòng hàng do người bán ở bang khác gửi.
        SELECT f.order_id, MAX((s.state <> c.state)::INT) AS cross_state
        FROM v_fact_order_items f
        JOIN v_dim_seller s ON f.seller_id = s.seller_id
        JOIN v_dim_customer c ON f.customer_id = c.customer_id
        GROUP BY f.order_id
    )
    SELECT CASE WHEN r.cross_state = 1 THEN 'Liên bang' ELSE 'Trong bang' END AS route,
           COUNT(*) AS delivered_orders,
           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
           ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
           ROUND(100.0 * AVG(o.is_late::INT), 2) AS late_rate_pct
    FROM route r
    JOIN v_fact_orders o ON r.order_id = o.order_id
    WHERE o.is_delivered
    GROUP BY r.cross_state
    ORDER BY r.cross_state
    """,
    ),
    # ------------------------------------------------------- Mục 20: đánh giá khách hàng
    Analysis(
        key="review_distribution",
        task=20,
        title="Phân bố điểm đánh giá",
        question="Khách hài lòng đến mức nào? (mỗi đơn tính một đánh giá)",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE}
    SELECT r.review_score,
           COUNT(*) AS orders,
           ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
    FROM review_per_order r
    JOIN v_fact_orders o ON r.order_id = o.order_id
    WHERE o.is_delivered
    GROUP BY r.review_score
    ORDER BY r.review_score
    """,
    ),
    Analysis(
        key="review_by_late",
        task=20,
        title="Điểm đánh giá: đơn đúng hạn so với đơn giao trễ",
        question="Đơn giao trễ có điểm đánh giá khác đơn đúng hạn không?",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE}
    SELECT CASE WHEN o.is_late THEN 'Giao trễ' ELSE 'Đúng hạn' END AS delivery_status,
           COUNT(*) AS orders_with_review,
           ROUND(AVG(r.review_score), 2) AS avg_review_score,
           ROUND(100.0 * AVG((r.review_score <= 2)::INT), 2) AS low_review_pct,
           ROUND(100.0 * AVG((r.review_score = 5)::INT), 2) AS five_star_pct
    FROM review_per_order r
    JOIN v_fact_orders o ON r.order_id = o.order_id
    WHERE o.is_delivered
    GROUP BY o.is_late
    ORDER BY o.is_late
    """,
    ),
    Analysis(
        key="review_by_delay",
        task=20,
        title="Điểm đánh giá theo mức độ trễ",
        question="Trễ càng lâu thì điểm có càng thấp không (quan hệ liều lượng – đáp ứng)?",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE},
    scored AS (
        SELECT r.review_score, {DAYS_VS_ESTIMATE} AS days_vs_estimate
        FROM review_per_order r
        JOIN v_fact_orders o ON r.order_id = o.order_id
        WHERE o.is_delivered AND o.order_delivered_customer_date IS NOT NULL
    ),
    bucketed AS (
        SELECT review_score,
               CASE
                   WHEN days_vs_estimate <= -7 THEN 1
                   WHEN days_vs_estimate <= 0 THEN 2
                   WHEN days_vs_estimate <= 3 THEN 3
                   WHEN days_vs_estimate <= 7 THEN 4
                   WHEN days_vs_estimate <= 14 THEN 5
                   ELSE 6
               END AS bucket_index
        FROM scored
    )
    SELECT bucket_index,
           CASE bucket_index
               WHEN 1 THEN 'Sớm từ 7 ngày trở lên' WHEN 2 THEN 'Sớm dưới 7 ngày'
               WHEN 3 THEN 'Trễ tới 3 ngày' WHEN 4 THEN 'Trễ 3–7 ngày'
               WHEN 5 THEN 'Trễ 7–14 ngày' ELSE 'Trễ trên 14 ngày'
           END AS delay_level,
           COUNT(*) AS orders_with_review,
           ROUND(AVG(review_score), 2) AS avg_review_score,
           ROUND(100.0 * AVG((review_score <= 2)::INT), 2) AS low_review_pct
    FROM bucketed
    GROUP BY bucket_index
    ORDER BY bucket_index
    """,
    ),
    Analysis(
        key="review_late_contingency",
        task=20,
        title="Bảng chéo giao trễ × điểm đánh giá",
        question="Số đơn theo từng cặp (đúng hạn/trễ, điểm 1–5) — đầu vào của kiểm định chi-bình-phương.",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE}
    SELECT o.is_late, r.review_score, COUNT(*) AS orders
    FROM review_per_order r
    JOIN v_fact_orders o ON r.order_id = o.order_id
    WHERE o.is_delivered
    GROUP BY o.is_late, r.review_score
    ORDER BY o.is_late, r.review_score
    """,
    ),
    Analysis(
        key="review_confounder",
        task=20,
        title="Một yếu tố khác cũng đi kèm điểm thấp: đơn có nhiều người bán",
        question="Ngoài giao trễ, còn yếu tố nào đi kèm điểm thấp? (lý do không kết luận nhân quả)",
        sql=f"""
    WITH {REVIEW_PER_ORDER_CTE},
    sellers_per_order AS (
        SELECT order_id, COUNT(DISTINCT seller_id) AS sellers
        FROM v_fact_order_items
        GROUP BY order_id
    )
    SELECT CASE WHEN o.is_late THEN 'Giao trễ' ELSE 'Đúng hạn' END AS delivery_status,
           CASE WHEN s.sellers > 1 THEN 'Từ 2 người bán' ELSE '1 người bán' END AS sellers_in_order,
           COUNT(*) AS orders_with_review,
           ROUND(AVG(r.review_score), 2) AS avg_review_score
    FROM review_per_order r
    JOIN v_fact_orders o ON r.order_id = o.order_id
    JOIN sellers_per_order s ON r.order_id = s.order_id
    WHERE o.is_delivered
    GROUP BY o.is_late, (s.sellers > 1)
    ORDER BY o.is_late, (s.sellers > 1)
    """,
    ),
)

ANALYSES: dict[str, Analysis] = {analysis.key: analysis for analysis in _ANALYSES}

TASK_TITLES: dict[int, str] = {
    17: "Phân tích kinh doanh",
    18: "Phân tích sản phẩm và người bán",
    19: "Phân tích giao vận",
    20: "Phân tích đánh giá khách hàng",
}


def analysis(key: str) -> Analysis:
    """Tra một phân tích theo mã, báo lỗi rõ ràng khi mã lạ."""

    try:
        return ANALYSES[key]
    except KeyError as exc:
        raise KeyError(f"Không có phân tích {key!r}. Các mã hợp lệ: {sorted(ANALYSES)}") from exc


def run_analysis(conn, key: str, params: tuple | None = None) -> pd.DataFrame:
    """Chạy một phân tích và trả DataFrame; `params` ghi đè tham số mặc định (ví dụ số dòng top N)."""

    item = analysis(key)
    return conn.execute(item.sql, list(item.params if params is None else params)).fetchdf()


def run_all(conn) -> dict[str, pd.DataFrame]:
    """Chạy toàn bộ phân tích với tham số mặc định, giữ nguyên thứ tự khai báo."""

    return {key: run_analysis(conn, key) for key in ANALYSES}


def contingency_table(frame: pd.DataFrame) -> list[list[int]]:
    """Chuyển kết quả `review_late_contingency` thành bảng 2 x 5 (đúng hạn/trễ x điểm 1–5)."""

    table = [[0] * 5 for _ in range(2)]
    for row in frame.itertuples(index=False):
        table[int(bool(row.is_late))][int(row.review_score) - 1] = int(row.orders)
    return table
