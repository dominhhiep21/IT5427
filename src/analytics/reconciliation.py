"""Đối soát các chỉ số (mục 16 của bảng phân công).

Câu hỏi cần trả lời: "Tổng tiền và số đơn trên dashboard có đúng không, có bị đếm trùng do
JOIN không?". Cách làm: tính cùng một con số bằng nhiều đường độc lập (CSV gốc, bảng fact,
bảng aggregate, baseline) rồi so với nhau; đồng thời chạy thử chính các câu JOIN sai để đo
được mức sai lệch nếu làm ẩu.

Bốn nhóm kiểm tra:

- **A. Cấu trúc**: grain của fact, khóa của dimension, khóa ngoại mồ côi.
- **B. Nguồn ↔ kho**: số dòng, doanh thu, số đơn, số đơn trễ khớp giữa CSV, fact, aggregate, baseline.
- **C. Bẫy đếm trùng**: minh họa có số liệu cho JOIN nhân bản dòng và số đo không cộng dồn được.
- **D. Khác biệt đã biết**: những chỗ lệch có lý do nghiệp vụ, cần nêu rõ khi đọc KPI.

Trạng thái: `pass` / `fail` cho kiểm tra có đúng–sai; `info` cho minh họa và khác biệt đã biết;
`skip` khi thiếu dữ liệu đầu vào (ví dụ không có CSV gốc).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal

from src.analytics.connection import available_views
from src.analytics.formatting import fmt_int, fmt_money, fmt_num, fmt_pct
from src.analytics.insights import REVIEW_PER_ORDER_CTE
from src.integrate.reconcile import BASELINE, TOLERANCE

PASS = "pass"
FAIL = "fail"
INFO = "info"
SKIP = "skip"

MONEY_TOLERANCE = 0.01
SOURCE_VIEWS = ("src_orders", "src_order_items", "src_payments", "src_reviews")


@dataclass(frozen=True)
class ReconCheck:
    """Một kiểm tra đối soát: câu SQL đã chạy, số liệu thu được và kết luận."""

    check_id: str
    group: str
    title: str
    purpose: str
    sql: str
    status: str
    values: dict
    conclusion: str


@dataclass
class ReconciliationResult:
    checks: list[ReconCheck] = field(default_factory=list)
    has_sources: bool = False

    @property
    def passed(self) -> bool:
        return all(check.status != FAIL for check in self.checks)

    def counts(self) -> dict[str, int]:
        summary = {PASS: 0, FAIL: 0, INFO: 0, SKIP: 0}
        for check in self.checks:
            summary[check.status] += 1
        return summary

    def get(self, check_id: str) -> ReconCheck:
        for check in self.checks:
            if check.check_id == check_id:
                return check
        raise KeyError(check_id)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "has_sources": self.has_sources,
            "counts": self.counts(),
            "checks": [asdict(check) for check in self.checks],
        }


def _plain(value):
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "item"):
        return value.item()
    return value


def _row(conn, sql: str) -> dict:
    cursor = conn.execute(sql)
    columns = [column[0] for column in cursor.description]
    return {column: _plain(value) for column, value in zip(columns, cursor.fetchone())}


def _same(values: list, tolerance: float = 0.0) -> bool:
    numbers = [float(value) for value in values if value is not None]
    return len(numbers) == len(values) and max(numbers) - min(numbers) <= tolerance


def _select(parts: list[str]) -> str:
    return "SELECT\n    " + ",\n    ".join(parts)


def _skipped(check_id: str, group: str, title: str, purpose: str) -> ReconCheck:
    return ReconCheck(
        check_id,
        group,
        title,
        purpose,
        sql="",
        status=SKIP,
        values={},
        conclusion="Bỏ qua: không tìm thấy CSV gốc trong `dataset/` nên không dựng được view `src_*`.",
    )


# --------------------------------------------------------------------------- A. Cấu trúc


def check_fact_grain(conn, has_sources: bool) -> ReconCheck:
    sql = _select(
        [
            "(SELECT COUNT(*) FROM v_fact_order_items) AS item_rows",
            "(SELECT COUNT(*) FROM (SELECT DISTINCT order_id, order_item_id FROM v_fact_order_items)) AS item_keys",
            "(SELECT COUNT(*) FROM v_fact_orders) AS order_rows",
            "(SELECT COUNT(DISTINCT order_id) FROM v_fact_orders) AS order_keys",
            "(SELECT COUNT(*) FROM v_fact_payments) AS payment_rows",
            "(SELECT COUNT(*) FROM (SELECT DISTINCT order_id, payment_sequential FROM v_fact_payments))"
            " AS payment_keys",
            "(SELECT COUNT(*) FROM v_fact_reviews) AS review_rows",
            "(SELECT COUNT(*) FROM (SELECT DISTINCT review_id, order_id FROM v_fact_reviews)) AS review_keys",
        ]
    )
    values = _row(conn, sql)
    ok = all(
        values[f"{name}_rows"] == values[f"{name}_keys"] for name in ("item", "order", "payment", "review")
    )
    return ReconCheck(
        "DS-01",
        "A. Cấu trúc",
        "Grain của bốn bảng fact",
        "Mỗi bảng fact phải đúng một dòng cho một khóa grain; có dòng trùng thì mọi phép SUM đều sai.",
        sql,
        PASS if ok else FAIL,
        values,
        (
            f"Cả bốn fact đúng grain: {fmt_int(values['item_rows'])} dòng hàng, {fmt_int(values['order_rows'])} đơn, "
            f"{fmt_int(values['payment_rows'])} dòng thanh toán, {fmt_int(values['review_rows'])} dòng đánh giá; "
            "số dòng bằng số khóa phân biệt."
            if ok
            else "Có bảng fact chứa khóa grain trùng — phải xử lý trước khi tin bất kỳ KPI nào."
        ),
    )


def check_dimension_keys(conn, has_sources: bool) -> ReconCheck:
    sql = _select(
        [
            "(SELECT COUNT(*) - COUNT(DISTINCT customer_id) FROM v_dim_customer) AS duplicate_customers",
            "(SELECT COUNT(*) - COUNT(DISTINCT product_id) FROM v_dim_product) AS duplicate_products",
            "(SELECT COUNT(*) - COUNT(DISTINCT seller_id) FROM v_dim_seller) AS duplicate_sellers",
            "(SELECT COUNT(*) - COUNT(DISTINCT date_key) FROM v_dim_date) AS duplicate_dates",
        ]
    )
    values = _row(conn, sql)
    ok = all(value == 0 for value in values.values())
    return ReconCheck(
        "DS-02",
        "A. Cấu trúc",
        "Khóa của dimension là duy nhất",
        "JOIN fact với dimension chỉ an toàn (không nhân dòng) khi khóa dimension không trùng.",
        sql,
        PASS if ok else FAIL,
        values,
        "Bốn dimension dùng để ghép (khách hàng, sản phẩm, người bán, ngày) đều có khóa duy nhất, "
        "nên JOIN fact → dimension là quan hệ nhiều–một và không nhân bản dòng."
        if ok
        else "Có dimension trùng khóa: JOIN fact → dimension sẽ nhân bản dòng fact.",
    )


def check_orphans(conn, has_sources: bool) -> ReconCheck:
    def orphan(alias: str, left: str, right: str, key: str) -> str:
        return f"(SELECT COUNT(*) FROM {left} l LEFT JOIN {right} r ON l.{key} = r.{key} WHERE r.{key} IS NULL) AS {alias}"

    sql = _select(
        [
            orphan("items_without_order", "v_fact_order_items", "v_fact_orders", "order_id"),
            orphan("items_without_product", "v_fact_order_items", "v_dim_product", "product_id"),
            orphan("items_without_seller", "v_fact_order_items", "v_dim_seller", "seller_id"),
            orphan("items_without_customer", "v_fact_order_items", "v_dim_customer", "customer_id"),
            orphan("items_without_date", "v_fact_order_items", "v_dim_date", "date_key"),
            orphan("orders_without_customer", "v_fact_orders", "v_dim_customer", "customer_id"),
            orphan("orders_without_date", "v_fact_orders", "v_dim_date", "date_key"),
            orphan("payments_without_order", "v_fact_payments", "v_fact_orders", "order_id"),
            orphan("reviews_without_order", "v_fact_reviews", "v_fact_orders", "order_id"),
        ]
    )
    values = _row(conn, sql)
    ok = all(value == 0 for value in values.values())
    return ReconCheck(
        "DS-03",
        "A. Cấu trúc",
        "Không có khóa ngoại mồ côi",
        "Truy vấn phân tích dùng INNER JOIN; một dòng fact không tìm thấy dimension sẽ bị rơi âm thầm "
        "và doanh thu bị thiếu.",
        sql,
        PASS if ok else FAIL,
        values,
        "Mọi dòng fact đều tìm thấy dimension tương ứng, nên INNER JOIN không làm rơi dòng nào."
        if ok
        else "Có dòng fact mồ côi: INNER JOIN sẽ làm thiếu số liệu.",
    )


# ----------------------------------------------------------------------- B. Nguồn ↔ kho


def check_row_counts(conn, has_sources: bool) -> ReconCheck:
    title = "Số dòng: CSV gốc = bảng fact"
    purpose = "Pipeline không được làm mất hay sinh thêm dòng so với nguồn (làm sạch bằng cờ, không xóa dòng)."
    if not has_sources:
        return _skipped("DS-04", "B. Nguồn ↔ kho", title, purpose)
    pairs = (
        ("orders", "src_orders", "v_fact_orders"),
        ("items", "src_order_items", "v_fact_order_items"),
        ("payments", "src_payments", "v_fact_payments"),
        ("reviews", "src_reviews", "v_fact_reviews"),
    )
    parts = []
    for name, source, fact in pairs:
        parts.append(f"(SELECT COUNT(*) FROM {source}) AS source_{name}")
        parts.append(f"(SELECT COUNT(*) FROM {fact}) AS fact_{name}")
    sql = _select(parts)
    values = _row(conn, sql)
    ok = all(values[f"source_{name}"] == values[f"fact_{name}"] for name, _, _ in pairs)
    return ReconCheck(
        "DS-04",
        "B. Nguồn ↔ kho",
        title,
        purpose,
        sql,
        PASS if ok else FAIL,
        values,
        (
            f"Khớp cả bốn bảng: {fmt_int(values['fact_orders'])} đơn, {fmt_int(values['fact_items'])} dòng hàng, "
            f"{fmt_int(values['fact_payments'])} thanh toán, {fmt_int(values['fact_reviews'])} đánh giá."
            if ok
            else "Số dòng trong kho lệch so với CSV gốc."
        ),
    )


def check_revenue(conn, has_sources: bool) -> ReconCheck:
    parts = [
        "(SELECT ROUND(SUM(item_total), 2) FROM v_fact_order_items WHERE is_delivered) AS fact_revenue",
        "(SELECT ROUND(SUM(revenue), 2) FROM v_agg_sales_daily) AS aggregate_revenue",
    ]
    if has_sources:
        parts.append(
            "(SELECT ROUND(SUM(CAST(i.price AS DOUBLE) + CAST(i.freight_value AS DOUBLE)), 2)\n"
            "     FROM src_order_items i JOIN src_orders o ON i.order_id = o.order_id\n"
            "     WHERE o.order_status = 'delivered') AS source_revenue"
        )
    sql = _select(parts)
    values = _row(conn, sql)
    ok = _same(list(values.values()), MONEY_TOLERANCE)
    ways = "CSV gốc, bảng fact và bảng aggregate" if has_sources else "bảng fact và bảng aggregate"
    return ReconCheck(
        "DS-05",
        "B. Nguồn ↔ kho",
        "Doanh thu delivered tính bằng nhiều đường",
        "Cùng một định nghĩa doanh thu (price + freight_value của đơn delivered) phải cho cùng một số "
        "dù tính từ đâu.",
        sql,
        PASS if ok else FAIL,
        values,
        f"Tính từ {ways} đều ra {fmt_money(values['fact_revenue'])}."
        if ok
        else "Doanh thu lệch giữa các đường tính — có đếm trùng hoặc rơi dòng ở một tầng.",
    )


def check_delivered_orders(conn, has_sources: bool) -> ReconCheck:
    parts = [
        "(SELECT COUNT(*) FROM v_fact_orders WHERE is_delivered) AS fact_orders",
        "(SELECT COUNT(DISTINCT order_id) FROM v_fact_order_items WHERE is_delivered) AS orders_from_items",
        "(SELECT CAST(SUM(delivered_orders) AS BIGINT) FROM v_agg_delivery_daily) AS aggregate_orders",
    ]
    if has_sources:
        parts.append("(SELECT COUNT(*) FROM src_orders WHERE order_status = 'delivered') AS source_orders")
    sql = _select(parts)
    values = _row(conn, sql)
    ok = _same(list(values.values()))
    return ReconCheck(
        "DS-06",
        "B. Nguồn ↔ kho",
        "Số đơn delivered đếm bằng nhiều đường",
        "Số đơn là mẫu số của AOV và tỷ lệ giao trễ; đếm ở grain đơn và đếm DISTINCT ở grain dòng hàng "
        "phải bằng nhau.",
        sql,
        PASS if ok else FAIL,
        values,
        f"Mọi đường đếm đều ra {fmt_int(values['fact_orders'])} đơn delivered."
        if ok
        else "Số đơn delivered lệch giữa các đường đếm.",
    )


def check_late_orders(conn, has_sources: bool) -> ReconCheck:
    parts = [
        "(SELECT CAST(COALESCE(SUM(is_late::INT), 0) AS BIGINT) FROM v_fact_orders WHERE is_delivered)"
        " AS fact_late_orders",
        "(SELECT CAST(SUM(late_orders) AS BIGINT) FROM v_agg_delivery_daily) AS aggregate_late_orders",
    ]
    if has_sources:
        parts.append(
            "(SELECT COUNT(*) FROM src_orders\n"
            "     WHERE order_status = 'delivered'\n"
            "       AND TRY_CAST(order_delivered_customer_date AS TIMESTAMP)\n"
            "           > TRY_CAST(order_estimated_delivery_date AS TIMESTAMP)) AS source_late_orders"
        )
    sql = _select(parts)
    values = _row(conn, sql)
    ok = _same(list(values.values()))
    return ReconCheck(
        "DS-07",
        "B. Nguồn ↔ kho",
        "Số đơn giao trễ tính bằng nhiều đường",
        "Cờ is_late trong kho phải khớp với việc so trực tiếp hai mốc thời gian trong CSV gốc.",
        sql,
        PASS if ok else FAIL,
        values,
        f"Mọi đường tính đều ra {fmt_int(values['fact_late_orders'])} đơn giao trễ."
        if ok
        else "Số đơn giao trễ lệch giữa các đường tính.",
    )


def check_baseline(conn, has_sources: bool, baseline: dict | None = None) -> ReconCheck:
    title = "KPI khớp baseline đã chốt"
    purpose = "Năm KPI chuẩn của nhóm (README, mục KPI baseline) là hợp đồng hồi quy: lệch quá dung sai là lỗi."
    sql = """WITH sales AS (
    SELECT SUM(item_total) AS revenue, COUNT(DISTINCT order_id) AS orders
    FROM v_fact_order_items
    WHERE is_delivered
),
delivery AS (
    SELECT COUNT(*) AS delivered, COALESCE(SUM(is_late::INT), 0) AS late
    FROM v_fact_orders
    WHERE is_delivered
)
SELECT ROUND(s.revenue, 2) AS revenue_delivered,
       s.orders AS delivered_orders,
       ROUND(s.revenue / s.orders, 2) AS aov,
       CAST(d.late AS BIGINT) AS late_orders,
       ROUND(100.0 * d.late / d.delivered, 2) AS late_rate_pct
FROM sales s CROSS JOIN delivery d"""
    values = _row(conn, sql)
    if baseline is None:
        return ReconCheck(
            "DS-08",
            "B. Nguồn ↔ kho",
            title,
            purpose,
            sql,
            INFO,
            values,
            "Không truyền baseline nên chỉ ghi nhận giá trị KPI hiện tại.",
        )
    deltas = {key: round(abs(float(values[key]) - float(baseline[key])), 4) for key in baseline}
    ok = all(deltas[key] <= TOLERANCE.get(key, 0) + 1e-9 for key in baseline)
    merged = {**values, **{f"baseline_{key}": baseline[key] for key in baseline}}
    return ReconCheck(
        "DS-08",
        "B. Nguồn ↔ kho",
        title,
        purpose,
        sql,
        PASS if ok else FAIL,
        merged,
        (
            f"Khớp baseline: doanh thu {fmt_money(values['revenue_delivered'])}, "
            f"{fmt_int(values['delivered_orders'])} đơn, AOV {fmt_money(values['aov'])}, "
            f"{fmt_int(values['late_orders'])} đơn trễ ({fmt_pct(values['late_rate_pct'])})."
            if ok
            else "KPI lệch baseline: "
            + ", ".join(f"{key} lệch {deltas[key]}" for key in baseline if deltas[key] > TOLERANCE.get(key, 0))
        ),
    )


# -------------------------------------------------------------------- C. Bẫy đếm trùng


def check_fanout_payments(conn, has_sources: bool) -> ReconCheck:
    sql = _select(
        [
            "(SELECT ROUND(SUM(item_total), 2) FROM v_fact_order_items WHERE is_delivered) AS correct_revenue",
            "(SELECT ROUND(SUM(f.item_total), 2)\n"
            "     FROM v_fact_order_items f JOIN v_fact_payments p ON f.order_id = p.order_id\n"
            "     WHERE f.is_delivered) AS naive_join_revenue",
            "(SELECT COUNT(*) FROM v_fact_order_items WHERE is_delivered) AS item_rows",
            "(SELECT COUNT(*)\n"
            "     FROM v_fact_order_items f JOIN v_fact_payments p ON f.order_id = p.order_id\n"
            "     WHERE f.is_delivered) AS joined_rows",
            "(SELECT COUNT(*) FROM (SELECT order_id FROM v_fact_payments GROUP BY order_id HAVING COUNT(*) > 1))"
            " AS orders_with_many_payments",
        ]
    )
    values = _row(conn, sql)
    correct = float(values["correct_revenue"] or 0)
    naive = float(values["naive_join_revenue"] or 0)
    inflation = naive - correct
    values["inflation"] = round(inflation, 2)
    values["inflation_pct"] = round(100.0 * inflation / correct, 2) if correct else 0.0
    return ReconCheck(
        "DS-09",
        "C. Bẫy đếm trùng",
        "Bẫy JOIN: dòng hàng × thanh toán",
        "Hai bảng đều nhiều dòng trên một đơn. Ghép thẳng qua order_id tạo tích Descartes trong từng đơn, "
        "doanh thu bị nhân lên.",
        sql,
        INFO,
        values,
        f"JOIN thẳng cho {fmt_money(naive)} thay vì {fmt_money(correct)}: thừa {fmt_money(inflation)} "
        f"({fmt_pct(values['inflation_pct'])}), vì {fmt_int(values['orders_with_many_payments'])} đơn có nhiều "
        f"dòng thanh toán làm {fmt_int(values['item_rows'])} dòng hàng phình thành {fmt_int(values['joined_rows'])} dòng. "
        "Cách đúng: gộp thanh toán về grain đơn trước rồi mới ghép, hoặc không ghép hai fact này.",
    )


def check_fanout_reviews(conn, has_sources: bool) -> ReconCheck:
    sql = _select(
        [
            "(SELECT ROUND(SUM(item_total), 2) FROM v_fact_order_items WHERE is_delivered) AS correct_revenue",
            "(SELECT ROUND(SUM(f.item_total), 2)\n"
            "     FROM v_fact_order_items f JOIN v_fact_reviews r ON f.order_id = r.order_id\n"
            "     WHERE f.is_delivered) AS naive_join_revenue",
            "(SELECT COUNT(*) FROM v_fact_orders WHERE is_delivered AND NOT has_review) AS delivered_without_review",
            "(SELECT COUNT(*) FROM (SELECT order_id FROM v_fact_reviews GROUP BY order_id HAVING COUNT(*) > 1))"
            " AS orders_with_many_reviews",
        ]
    )
    values = _row(conn, sql)
    correct = float(values["correct_revenue"] or 0)
    naive = float(values["naive_join_revenue"] or 0)
    values["difference"] = round(naive - correct, 2)
    return ReconCheck(
        "DS-10",
        "C. Bẫy đếm trùng",
        "Bẫy JOIN: dòng hàng × đánh giá",
        "INNER JOIN với bảng đánh giá sai theo hai chiều cùng lúc: đơn không có đánh giá bị rơi, "
        "đơn nhiều đánh giá bị nhân.",
        sql,
        INFO,
        values,
        f"JOIN thẳng cho {fmt_money(naive)}, lệch {fmt_money(values['difference'])} so với {fmt_money(correct)}: "
        f"{fmt_int(values['delivered_without_review'])} đơn delivered không có đánh giá bị loại, trong khi "
        f"{fmt_int(values['orders_with_many_reviews'])} đơn có nhiều đánh giá bị đếm lặp. Hai sai số ngược chiều "
        "bù trừ nhau nên con số trông 'gần đúng' — loại lỗi khó phát hiện nhất.",
    )


def check_non_additive_orders(conn, has_sources: bool) -> ReconCheck:
    sql = _select(
        [
            "(SELECT COUNT(DISTINCT order_id) FROM v_fact_order_items WHERE is_delivered) AS distinct_orders",
            "(SELECT CAST(SUM(orders) AS BIGINT) FROM v_agg_sales_daily) AS summed_orders_in_aggregate",
            "(SELECT COUNT(*) FROM (\n"
            "        SELECT f.order_id\n"
            "        FROM v_fact_order_items f JOIN v_dim_product p ON f.product_id = p.product_id\n"
            "        WHERE f.is_delivered\n"
            "        GROUP BY f.order_id HAVING COUNT(DISTINCT p.category) > 1)) AS orders_with_many_categories",
        ]
    )
    values = _row(conn, sql)
    extra = int(values["summed_orders_in_aggregate"] or 0) - int(values["distinct_orders"] or 0)
    values["overcount"] = extra
    return ReconCheck(
        "DS-11",
        "C. Bẫy đếm trùng",
        "Số đơn không cộng dồn được qua danh mục",
        "Doanh thu là số đo cộng được; số đơn thì không, vì một đơn có thể chứa hàng của nhiều danh mục.",
        sql,
        INFO,
        values,
        f"Cộng cột orders của agg_sales_daily ra {fmt_int(values['summed_orders_in_aggregate'])}, nhiều hơn "
        f"{fmt_int(extra)} so với {fmt_int(values['distinct_orders'])} đơn thật, do "
        f"{fmt_int(values['orders_with_many_categories'])} đơn thuộc nhiều danh mục. Vì vậy số đơn tổng luôn được "
        "đếm DISTINCT ở grain gốc; bảng aggregate chỉ dùng cho doanh thu và cho số đơn trong một danh mục.",
    )


def check_ratio_metric(conn, has_sources: bool) -> ReconCheck:
    sql = """WITH monthly AS (
    SELECT d.year, d.month, SUM(f.item_total) AS revenue, COUNT(DISTINCT f.order_id) AS orders
    FROM v_fact_order_items f
    JOIN v_dim_date d ON f.date_key = d.date_key
    WHERE f.is_delivered
    GROUP BY d.year, d.month
)
SELECT ROUND(SUM(revenue) / SUM(orders), 2) AS aov_overall,
       ROUND(AVG(revenue / orders), 2) AS mean_of_monthly_aov,
       COUNT(*) AS months
FROM monthly"""
    values = _row(conn, sql)
    return ReconCheck(
        "DS-12",
        "C. Bẫy đếm trùng",
        "AOV là tỷ số: không lấy trung bình của trung bình",
        "KPI dạng tỷ số (AOV, tỷ lệ giao trễ) phải tính lại từ tử số và mẫu số, không lấy trung bình các nhóm.",
        sql,
        INFO,
        values,
        f"AOV đúng (tổng doanh thu / tổng số đơn) là {fmt_money(values['aov_overall'])}; nếu lấy trung bình "
        f"AOV của {fmt_int(values['months'])} tháng thì ra {fmt_money(values['mean_of_monthly_aov'])} — sai vì "
        "tháng ít đơn được tính nặng ngang tháng nhiều đơn.",
    )


# ------------------------------------------------------------------ D. Khác biệt đã biết


def check_items_vs_payments(conn, has_sources: bool) -> ReconCheck:
    sql = """WITH items AS (
    SELECT order_id, SUM(item_total) AS item_total FROM v_fact_order_items GROUP BY order_id
),
pays AS (
    SELECT order_id, SUM(payment_value) AS paid, MAX(payment_installments) AS installments
    FROM v_fact_payments
    GROUP BY order_id
),
compared AS (
    SELECT i.item_total, p.paid, p.installments, ROUND(p.paid - i.item_total, 2) AS diff
    FROM items i
    JOIN pays p ON i.order_id = p.order_id
)
SELECT COUNT(*) AS orders_compared,
       COUNT(*) FILTER (WHERE ABS(diff) > 0.011) AS orders_mismatched,
       COUNT(*) FILTER (WHERE ABS(diff) BETWEEN 0.009 AND 0.011) AS orders_off_by_one_cent,
       COUNT(*) FILTER (WHERE diff > 0.011) AS orders_paid_more,
       COUNT(*) FILTER (WHERE diff < -0.011) AS orders_paid_less,
       ROUND(100.0 * COUNT(*) FILTER (WHERE diff > 0.011 AND installments > 1)
             / NULLIF(COUNT(*) FILTER (WHERE diff > 0.011), 0), 2) AS paid_more_installment_pct,
       ROUND(SUM(item_total), 2) AS item_total,
       ROUND(SUM(paid), 2) AS payment_total,
       ROUND(SUM(paid) - SUM(item_total), 2) AS difference,
       ROUND(MAX(ABS(paid - item_total)), 2) AS max_abs_difference
FROM compared"""
    values = _row(conn, sql)
    share = 100.0 * float(values["orders_mismatched"] or 0) / float(values["orders_compared"] or 1)
    values["mismatch_share_pct"] = round(share, 2)
    return ReconCheck(
        "DS-13",
        "D. Khác biệt đã biết",
        "Tiền hàng so với tiền thanh toán theo từng đơn",
        "Hai nguồn độc lập cùng mô tả giá trị đơn. Chúng gần bằng nhau thì định nghĩa doanh thu đáng tin; "
        "phần lệch phải được giải thích.",
        sql,
        INFO,
        values,
        f"So {fmt_int(values['orders_compared'])} đơn có cả dòng hàng và thanh toán (mỗi bên gộp về grain đơn trước): "
        f"{fmt_int(values['orders_mismatched'])} đơn lệch từ 0,02 BRL trở lên ({fmt_pct(share)}), thêm "
        f"{fmt_int(values['orders_off_by_one_cent'])} đơn lệch đúng 0,01 BRL do làm tròn. Tổng lệch "
        f"{fmt_money(values['difference'])}, lệch lớn nhất {fmt_money(values['max_abs_difference'])}. "
        f"Trong nhóm lệch, {fmt_int(values['orders_paid_more'])} đơn khách trả nhiều hơn tiền hàng và "
        f"{fmt_pct(values['paid_more_installment_pct'])} số đó trả góp nhiều kỳ — phù hợp với giả thuyết lãi trả góp, "
        "nhưng dữ liệu không có cột lãi nên chưa khẳng định được. Vì hai nguồn lệch nhau, nhóm chọn dòng hàng làm "
        "định nghĩa doanh thu duy nhất.",
    )


def check_late_definition(conn, has_sources: bool) -> ReconCheck:
    sql = """SELECT COUNT(*) AS delivered_orders,
       CAST(COALESCE(SUM(is_late::INT), 0) AS BIGINT) AS late_by_timestamp,
       CAST(COALESCE(SUM((CAST(order_delivered_customer_date AS DATE)
                          > CAST(order_estimated_delivery_date AS DATE))::INT), 0) AS BIGINT) AS late_by_calendar_day
FROM v_fact_orders
WHERE is_delivered"""
    values = _row(conn, sql)
    delivered = float(values["delivered_orders"] or 1)
    values["late_rate_by_timestamp_pct"] = round(100.0 * values["late_by_timestamp"] / delivered, 2)
    values["late_rate_by_calendar_day_pct"] = round(100.0 * values["late_by_calendar_day"] / delivered, 2)
    gap = int(values["late_by_timestamp"]) - int(values["late_by_calendar_day"])
    values["same_day_orders"] = gap
    return ReconCheck(
        "DS-14",
        "D. Khác biệt đã biết",
        "Độ nhạy của định nghĩa 'giao trễ'",
        "Ngày giao dự kiến trong dữ liệu luôn là 00:00. So theo mốc thời gian thì đơn giao trong chính ngày "
        "dự kiến cũng bị tính là trễ.",
        sql,
        INFO,
        values,
        f"Định nghĩa của nhóm (so mốc thời gian) cho {fmt_int(values['late_by_timestamp'])} đơn trễ "
        f"({fmt_pct(values['late_rate_by_timestamp_pct'])}). Nếu so theo ngày lịch thì còn "
        f"{fmt_int(values['late_by_calendar_day'])} đơn ({fmt_pct(values['late_rate_by_calendar_day_pct'])}); "
        f"{fmt_int(gap)} đơn chênh lệch là đơn giao đúng trong ngày dự kiến. Nhóm giữ định nghĩa theo mốc thời gian "
        "vì nó khớp baseline và là cách tính chặt hơn, nhưng phải nói rõ khi trình bày.",
    )


def check_missing_delivery_date(conn, has_sources: bool) -> ReconCheck:
    sql = """SELECT COUNT(*) AS delivered_orders,
       COUNT(*) FILTER (WHERE order_delivered_customer_date IS NULL) AS delivered_without_date
FROM v_fact_orders
WHERE is_delivered"""
    values = _row(conn, sql)
    return ReconCheck(
        "DS-15",
        "D. Khác biệt đã biết",
        "Đơn delivered thiếu ngày giao thực tế",
        "Đơn thiếu ngày giao không tính được thời gian giao và mặc định không bị coi là trễ.",
        sql,
        INFO,
        values,
        f"{fmt_int(values['delivered_without_date'])} trong {fmt_int(values['delivered_orders'])} đơn delivered không có "
        "ngày giao thực tế. Chúng vẫn nằm trong mẫu số tỷ lệ giao trễ nhưng bị loại khỏi thời gian giao trung bình; "
        "ảnh hưởng không đáng kể nhưng cần biết.",
    )


def check_review_grain(conn, has_sources: bool) -> ReconCheck:
    sql = f"""WITH {REVIEW_PER_ORDER_CTE}
SELECT (SELECT COUNT(*) FROM v_fact_reviews) AS review_rows,
       (SELECT COUNT(DISTINCT order_id) FROM v_fact_reviews) AS orders_with_review,
       (SELECT COUNT(*) FROM (SELECT order_id FROM v_fact_reviews GROUP BY order_id HAVING COUNT(*) > 1))
           AS orders_with_many_reviews,
       (SELECT ROUND(AVG(r.review_score), 4)
        FROM v_fact_reviews r JOIN v_fact_orders o ON r.order_id = o.order_id
        WHERE o.is_delivered) AS avg_score_row_level,
       (SELECT ROUND(AVG(l.review_score), 4)
        FROM review_per_order l JOIN v_fact_orders o ON l.order_id = o.order_id
        WHERE o.is_delivered) AS avg_score_order_level"""
    values = _row(conn, sql)
    extra = int(values["review_rows"]) - int(values["orders_with_review"])
    values["extra_review_rows"] = extra
    return ReconCheck(
        "DS-16",
        "D. Khác biệt đã biết",
        "Đánh giá: đếm theo dòng hay theo đơn",
        "Một đơn có thể có nhiều đánh giá. Phân tích ở grain đơn phải chọn một đánh giá cho mỗi đơn.",
        sql,
        INFO,
        values,
        f"{fmt_int(values['review_rows'])} dòng đánh giá thuộc {fmt_int(values['orders_with_review'])} đơn: "
        f"{fmt_int(values['orders_with_many_reviews'])} đơn có nhiều đánh giá, tạo {fmt_int(extra)} dòng dư. "
        f"Điểm trung bình đơn delivered là {fmt_num(values['avg_score_row_level'], 4)} nếu tính theo dòng và "
        f"{fmt_num(values['avg_score_order_level'], 4)} nếu mỗi đơn lấy đánh giá mới nhất. Phần phân tích dùng "
        "cách thứ hai.",
    )


def check_category_definitions(conn, has_sources: bool) -> ReconCheck:
    sql = """WITH by_item AS (
    SELECT p.category, COUNT(DISTINCT f.order_id) AS orders_any_item
    FROM v_fact_order_items f
    JOIN v_dim_product p ON f.product_id = p.product_id
    WHERE f.is_delivered
    GROUP BY p.category
),
by_order AS (
    SELECT category, COUNT(*) AS orders_dominant
    FROM v_fact_orders
    WHERE is_delivered
    GROUP BY category
)
SELECT COUNT(*) AS categories,
       CAST(SUM((COALESCE(i.orders_any_item, 0) <> COALESCE(o.orders_dominant, 0))::INT) AS BIGINT)
           AS categories_differing,
       CAST(SUM(i.orders_any_item) AS BIGINT) AS sum_orders_any_item,
       CAST(SUM(o.orders_dominant) AS BIGINT) AS sum_orders_dominant,
       MAX(ABS(COALESCE(i.orders_any_item, 0) - COALESCE(o.orders_dominant, 0))) AS max_difference
FROM by_item i
FULL JOIN by_order o ON i.category = o.category"""
    values = _row(conn, sql)
    return ReconCheck(
        "DS-17",
        "D. Khác biệt đã biết",
        "Hai cách đếm số đơn theo danh mục",
        "Kho có hai khái niệm: danh mục của từng dòng hàng (dim_product) và danh mục đại diện của đơn "
        "(fact_orders.category). Chúng cho số đơn khác nhau.",
        sql,
        INFO,
        values,
        f"Trong {fmt_int(values['categories'])} danh mục có {fmt_int(values['categories_differing'])} danh mục mà hai "
        f"cách đếm lệch nhau (lệch lớn nhất {fmt_int(values['max_difference'])} đơn). Đếm theo dòng hàng cộng lại ra "
        f"{fmt_int(values['sum_orders_any_item'])} (một đơn tính cho mọi danh mục nó chứa); đếm theo danh mục đại "
        f"diện cộng lại đúng {fmt_int(values['sum_orders_dominant'])}. Hệ quả: khi lọc dashboard theo danh mục, "
        "thẻ KPI (đếm theo danh mục đại diện) và bảng danh mục (đếm theo dòng hàng) có thể hiện hai số đơn "
        "khác nhau cho cùng một danh mục. Doanh thu thì luôn tính theo dòng hàng.",
    )


CHECKS = (
    check_fact_grain,
    check_dimension_keys,
    check_orphans,
    check_row_counts,
    check_revenue,
    check_delivered_orders,
    check_late_orders,
    check_baseline,
    check_fanout_payments,
    check_fanout_reviews,
    check_non_additive_orders,
    check_ratio_metric,
    check_items_vs_payments,
    check_late_definition,
    check_missing_delivery_date,
    check_review_grain,
    check_category_definitions,
)


def run_reconciliation(conn, baseline: dict | None = BASELINE) -> ReconciliationResult:
    """Chạy toàn bộ kiểm tra đối soát trên kết nối đã có view `v_*` (và `src_*` nếu có CSV gốc)."""

    has_sources = set(SOURCE_VIEWS) <= available_views(conn)
    result = ReconciliationResult(has_sources=has_sources)
    for check in CHECKS:
        if check is check_baseline:
            result.checks.append(check_baseline(conn, has_sources, baseline))
        else:
            result.checks.append(check(conn, has_sources))
    return result
