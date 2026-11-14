"""Read-only analytics queries over the DuckDB star schema."""

from __future__ import annotations

import pandas as pd

from src.common.types import KpiFilters
from src.integrate.connections import ConnectionFactory

# Ba truy vấn của tầng `stats`; mọi tên bảng đều là view trong `VIEW_TABLES` (SEC-2).
LATE_RATES_BY_STATE_SQL = """
    SELECT c.state AS state,
           CAST(COUNT(*) AS BIGINT) AS delivered_orders,
           CAST(SUM(CASE WHEN o.is_late THEN 1 ELSE 0 END) AS BIGINT) AS late_orders
    FROM v_fact_orders o
    JOIN v_dim_customer c ON o.customer_id = c.customer_id
    JOIN v_dim_date d ON o.date_key = d.date_key
"""

LATE_RATES_BY_REGION_SQL = """
    SELECT c.region AS region,
           o.is_late AS is_late,
           CAST(COUNT(*) AS BIGINT) AS delivered_orders
    FROM v_fact_orders o
    JOIN v_dim_customer c ON o.customer_id = c.customer_id
    JOIN v_dim_date d ON o.date_key = d.date_key
"""

PRICE_FREIGHT_PAIRS_SQL = """
    SELECT CAST(f.price AS DOUBLE) AS price,
           CAST(f.freight_value AS DOUBLE) AS freight_value
    FROM v_fact_order_items f
    JOIN v_dim_customer c ON f.customer_id = c.customer_id
    JOIN v_dim_date d ON f.date_key = d.date_key
"""

# Khung huấn luyện ở grain DÒNG HÀNG: một dòng mỗi cặp (order_id, order_item_id) của đơn
# đã giao và có carrier date. Bốn bộ đếm đến từ CÙNG câu lệnh này (BR2.1): ba số đếm từ khung
# trả về, số thứ tư là cột hằng của CTE `excluded` — không có truy vấn thứ hai.
# Hai cột ngày tính theo độ phân giải NGÀY vì mart chỉ giữ `date_key` (mất phần giờ của mốc mua).
TRAINING_FRAME_SQL = """
    WITH order_items AS (
        SELECT f.order_id AS order_id,
               CAST(COUNT(*) AS BIGINT) AS item_count,
               CAST(SUM(f.item_total) AS DOUBLE) AS item_total,
               CAST(MAX(f.price) AS DOUBLE) AS item_price_max
        FROM v_fact_order_items f
        GROUP BY f.order_id
    ),
    order_payments AS (
        SELECT p.order_id AS order_id,
               MAX(p.payment_installments) AS payment_installments,
               MAX(CASE WHEN p.payment_sequential = 1 THEN p.payment_type END) AS payment_type
        FROM v_fact_payments p
        GROUP BY p.order_id
    ),
    excluded AS (
        SELECT CAST(COUNT(DISTINCT order_id) AS BIGINT) AS excluded_missing_carrier
        FROM v_fact_orders
        WHERE is_delivered AND order_delivered_carrier_date IS NULL
    ),
    selected AS (
        SELECT o.order_id AS order_id,
               f.order_item_id AS order_item_id,
               o.date_key AS date_key,
               o.is_delivered AS is_delivered,
               o.is_late AS is_late,
               o.has_items AS has_items,
               o.has_payment AS has_payment,
               f.seller_state AS seller_state,
               c.state AS customer_state,
               c.region AS customer_region,
               d.month AS purchase_month,
               d.weekday AS purchase_weekday,
               i.item_count AS item_count,
               i.item_total AS item_total,
               i.item_price_max AS item_price_max,
               p.payment_type AS payment_type,
               p.payment_installments AS payment_installments,
               CAST(date_diff('day', CAST(o.date_key AS DATE), CAST(o.order_approved_at AS DATE)) AS BIGINT)
                   AS approval_days,
               CAST(date_diff('day', CAST(o.order_approved_at AS DATE), CAST(o.order_delivered_carrier_date AS DATE)) AS BIGINT)
                   AS handling_days
        FROM v_fact_order_items f
        JOIN v_fact_orders o ON f.order_id = o.order_id
        JOIN v_dim_customer c ON f.customer_id = c.customer_id
        JOIN v_dim_date d ON f.date_key = d.date_key
        LEFT JOIN order_items i ON f.order_id = i.order_id
        LEFT JOIN order_payments p ON f.order_id = p.order_id
        WHERE o.is_delivered AND o.order_delivered_carrier_date IS NOT NULL
    )
    SELECT s.*, e.excluded_missing_carrier AS excluded_missing_carrier
    FROM selected s
    CROSS JOIN excluded e
"""

# Chặn số dòng của truy vấn nặng nhất trong ba truy vấn trên (PD-2).
MAX_CORRELATION_ROWS = 200_000


class AnalyticsService:
    def __init__(self, config) -> None:
        self.config = config

    def _connect(self):
        return ConnectionFactory(self.config).read_only()

    def _where(
        self,
        filters: KpiFilters,
        *,
        alias_fact: str = "f",
        alias_customer: str = "c",
        alias_date: str = "d",
        alias_category: str | None = "p",
        status_column: str | None = None,
    ) -> tuple[str, list]:
        clauses: list[str] = []
        params: list = []
        if filters.start_date:
            clauses.append(f"{alias_date}.date_key >= ?")
            params.append(filters.start_date)
        if filters.end_date:
            clauses.append(f"{alias_date}.date_key <= ?")
            params.append(filters.end_date)
        if filters.state:
            clauses.append(f"{alias_customer}.state = ?")
            params.append(filters.state)
        if filters.region:
            clauses.append(f"{alias_customer}.region = ?")
            params.append(filters.region)
        if filters.category:
            if alias_category is None:
                raise ValueError("Category filter requires a category alias")
            clauses.append(f"{alias_category}.category = ?")
            params.append(filters.category)
        if status_column and filters.order_status not in (None, "", "all"):
            clauses.append(f"{status_column} = ?")
            params.append(filters.order_status)
        where = " AND " + " AND ".join(clauses) if clauses else ""
        return where, params

    def kpi_summary(self, filters: KpiFilters) -> dict:
        revenue_sql = """
            SELECT COALESCE(SUM(f.item_total), 0) AS revenue
            FROM v_fact_order_items f
            JOIN v_dim_customer c ON f.customer_id = c.customer_id
            JOIN v_dim_product p ON f.product_id = p.product_id
            JOIN v_dim_date d ON f.date_key = d.date_key
        """
        revenue_where, revenue_params = self._where(filters, status_column="f.order_status")
        orders_sql = """
            SELECT COUNT(*) AS orders
            FROM v_fact_orders o
            JOIN v_dim_customer c ON o.customer_id = c.customer_id
            JOIN v_dim_date d ON o.date_key = d.date_key
        """
        orders_where, orders_params = self._where(
            filters,
            alias_fact="o",
            alias_category="o",
            status_column="o.order_status",
        )
        late_sql = """
            SELECT COUNT(*) AS delivered_orders,
                   COALESCE(SUM(CASE WHEN o.is_late THEN 1 ELSE 0 END), 0) AS late_orders
            FROM v_fact_orders o
            JOIN v_dim_customer c ON o.customer_id = c.customer_id
            JOIN v_dim_date d ON o.date_key = d.date_key
        """
        late_where, late_params = self._where(
            filters,
            alias_fact="o",
            alias_category="o",
            status_column="o.order_status",
        )
        late_where = (late_where + " AND o.is_delivered") if late_where else " WHERE o.is_delivered"

        review_sql = """
            SELECT AVG(r.review_score) AS avg_review_score
            FROM v_fact_reviews r
            JOIN v_fact_orders o ON r.order_id = o.order_id
            JOIN v_dim_customer c ON o.customer_id = c.customer_id
            JOIN v_dim_date d ON o.date_key = d.date_key
        """
        review_where, review_params = self._where(
            filters,
            alias_fact="o",
            alias_category="o",
            status_column="o.order_status",
        )

        conn = self._connect()
        try:
            revenue_row = conn.execute(revenue_sql + revenue_where, revenue_params).fetchone()
            orders_row = conn.execute(orders_sql + orders_where, orders_params).fetchone()
            late_row = conn.execute(late_sql + late_where, late_params).fetchone()
            review_row = conn.execute(review_sql + review_where, review_params).fetchone()
        finally:
            conn.close()

        revenue = float(revenue_row[0] or 0)
        orders = int(orders_row[0] or 0)
        delivered_orders = int(late_row[0] or 0)
        late_orders = int(late_row[1] or 0)
        return {
            "revenue": round(revenue, 2),
            "orders": orders,
            "aov": round(revenue / orders, 2) if orders else 0.0,
            "delivered_orders": delivered_orders,
            "late_orders": late_orders,
            "late_rate_pct": round(late_orders / delivered_orders * 100, 2) if delivered_orders else 0.0,
            "avg_review_score": round(float(review_row[0]), 2)
            if review_row and review_row[0] is not None
            else None,
        }

    def revenue_by_period(self, filters: KpiFilters, granularity: str = "month") -> pd.DataFrame:
        if granularity not in {"month", "quarter", "year"}:
            raise ValueError("granularity must be month, quarter or year")
        period = {
            "month": "d.year, d.month",
            "quarter": "d.year, d.quarter",
            "year": "d.year",
        }[granularity]
        group = {
            "month": "d.year, d.month, d.is_sparse_period",
            "quarter": "d.year, d.quarter, d.is_sparse_period",
            "year": "d.year, d.is_sparse_period",
        }[granularity]
        where, params = self._where(filters, status_column="f.order_status")
        sql = f"""
            SELECT {period}, d.is_sparse_period,
                   ROUND(SUM(f.item_total), 2) AS revenue,
                   COUNT(DISTINCT f.order_id) AS orders
            FROM v_fact_order_items f
            JOIN v_dim_customer c ON f.customer_id = c.customer_id
            JOIN v_dim_product p ON f.product_id = p.product_id
            JOIN v_dim_date d ON f.date_key = d.date_key
            {where}
            GROUP BY {group}
            ORDER BY {period}
        """
        conn = self._connect()
        try:
            frame = conn.execute(sql, params).fetchdf()
        finally:
            conn.close()
        frame["aov"] = (frame["revenue"] / frame["orders"]).round(2)
        return frame

    def revenue_by_dimension(self, filters: KpiFilters, dimension: str = "category") -> pd.DataFrame:
        if dimension not in {"category", "region", "state"}:
            raise ValueError("dimension must be category, region or state")
        column = {
            "category": "p.category",
            "region": "c.region",
            "state": "c.state",
        }[dimension]
        where, params = self._where(filters, status_column="f.order_status")
        sql = f"""
            SELECT {column} AS dimension,
                   ROUND(SUM(f.item_total), 2) AS revenue,
                   COUNT(DISTINCT f.order_id) AS orders,
                   ROUND(SUM(f.freight_value), 2) AS freight
            FROM v_fact_order_items f
            JOIN v_dim_customer c ON f.customer_id = c.customer_id
            JOIN v_dim_product p ON f.product_id = p.product_id
            JOIN v_dim_date d ON f.date_key = d.date_key
            {where}
            GROUP BY {column}
            ORDER BY revenue DESC, dimension ASC
        """
        conn = self._connect()
        try:
            frame = conn.execute(sql, params).fetchdf()
        finally:
            conn.close()
        frame["aov"] = (frame["revenue"] / frame["orders"]).round(2)
        frame["freight_share_pct"] = (frame["freight"] / frame["revenue"] * 100).fillna(0).round(2)
        return frame

    def top_entities(self, filters: KpiFilters, entity: str = "product", limit: int = 10) -> pd.DataFrame:
        if entity not in {"product", "seller"}:
            raise ValueError("entity must be product or seller")
        if entity == "product":
            id_column = "f.product_id"
            join = "JOIN v_dim_product p ON f.product_id = p.product_id"
            label = "p.category AS category"
            group = "f.product_id, p.category"
        else:
            id_column = "f.seller_id"
            join = "JOIN v_dim_product p ON f.product_id = p.product_id"
            label = "CAST(NULL AS VARCHAR) AS category"
            group = "f.seller_id"
        where, params = self._where(filters, status_column="f.order_status")
        sql = f"""
            SELECT {id_column} AS entity_id, {label},
                   ROUND(SUM(f.item_total), 2) AS revenue,
                   COUNT(DISTINCT f.order_id) AS orders
            FROM v_fact_order_items f
            JOIN v_dim_customer c ON f.customer_id = c.customer_id
            JOIN v_dim_date d ON f.date_key = d.date_key
            {join}
            {where}
            GROUP BY {group}
            ORDER BY revenue DESC, entity_id ASC
            LIMIT ?
        """
        conn = self._connect()
        try:
            return conn.execute(sql, params + [limit]).fetchdf()
        finally:
            conn.close()

    def delivery_kpis(self, filters: KpiFilters, group_by: str = "state") -> pd.DataFrame:
        if group_by not in {"state", "category", "month"}:
            raise ValueError("group_by must be state, category or month")
        column = {
            "state": "c.state",
            "category": "o.category",
            "month": "d.year || '-' || LPAD(CAST(d.month AS VARCHAR), 2, '0')",
        }[group_by]
        where, params = self._where(
            filters,
            alias_fact="o",
            alias_category="o",
            status_column="o.order_status",
        )
        where = (where + " AND o.is_delivered") if where else " WHERE o.is_delivered"
        sql = f"""
            SELECT {column} AS dimension,
                   COUNT(*) AS delivered_orders,
                   SUM(CASE WHEN o.is_late THEN 1 ELSE 0 END) AS late_orders,
                   ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days
            FROM v_fact_orders o
            JOIN v_dim_customer c ON o.customer_id = c.customer_id
            JOIN v_dim_date d ON o.date_key = d.date_key
            {where}
            GROUP BY {column}
            ORDER BY dimension
        """
        conn = self._connect()
        try:
            frame = conn.execute(sql, params).fetchdf()
        finally:
            conn.close()
        frame["late_rate_pct"] = (frame["late_orders"] / frame["delivered_orders"] * 100).round(2)
        return frame

    def late_rates_by_state(self, filters: KpiFilters) -> pd.DataFrame:
        """Tỉ lệ trễ theo từng bang kèm số đơn đã giao, gộp sẵn ở SQL (BR1.2, PD-2)."""

        where, params = self._where(
            filters,
            alias_fact="o",
            alias_category="o",
            status_column="o.order_status",
        )
        where = (where + " AND o.is_delivered") if where else " WHERE o.is_delivered"
        sql = LATE_RATES_BY_STATE_SQL + where + " GROUP BY c.state ORDER BY c.state"
        conn = self._connect()
        try:
            return conn.execute(sql, params).fetchdf()
        finally:
            conn.close()

    def late_rates_by_region(self, filters: KpiFilters) -> pd.DataFrame:
        """Bảng đếm vùng × trễ trên đơn đã giao, không kéo dòng thô về Python (BR1.4, PD-2)."""

        where, params = self._where(
            filters,
            alias_fact="o",
            alias_category="o",
            status_column="o.order_status",
        )
        where = (where + " AND o.is_delivered") if where else " WHERE o.is_delivered"
        sql = LATE_RATES_BY_REGION_SQL + where + " GROUP BY c.region, o.is_late ORDER BY c.region, o.is_late"
        conn = self._connect()
        try:
            return conn.execute(sql, params).fetchdf()
        finally:
            conn.close()

    def price_freight_pairs(self, filters: KpiFilters, limit: int = MAX_CORRELATION_ROWS) -> pd.DataFrame:
        """Cặp giá hàng / phí vận chuyển ở grain dòng hàng, có chặn số dòng (BR1.3, PD-2)."""

        where, params = self._where(filters, status_column="f.order_status")
        extra = "f.is_delivered AND f.price IS NOT NULL AND f.freight_value IS NOT NULL"
        where = (where + " AND " + extra) if where else " WHERE " + extra
        sql = PRICE_FREIGHT_PAIRS_SQL + where + " ORDER BY f.order_id, f.order_item_id LIMIT ?"
        conn = self._connect()
        try:
            return conn.execute(sql, params + [limit]).fetchdf()
        finally:
            conn.close()

    def training_frame(self) -> tuple[pd.DataFrame, dict[str, int]]:
        """Khung grain dòng hàng cho bước mô hình, kèm bốn bộ đếm quần thể (BR2.1)."""

        conn = self._connect()
        try:
            raw = conn.execute(TRAINING_FRAME_SQL).fetchdf()
        finally:
            conn.close()
        if raw[["order_id", "order_item_id"]].duplicated().any():
            raise ValueError("Bảng huấn luyện nhân dòng: mỗi cặp (order_id, order_item_id) phải đúng một dòng")
        counts = {
            "cohort_rows": len(raw),
            "cohort_orders": int(raw["order_id"].nunique()),
            "late_rows": int(raw["is_late"].fillna(value=False).astype(bool).sum()),
            "excluded_missing_carrier": int(raw["excluded_missing_carrier"].iloc[0]) if len(raw) else 0,
        }
        frame = raw.drop(columns=["excluded_missing_carrier"])
        return frame, counts
