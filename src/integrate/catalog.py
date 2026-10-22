"""Create DuckDB views over Parquet marts."""

from __future__ import annotations

from src.integrate.connections import ConnectionFactory

VIEW_TABLES = (
    "dim_customer",
    "dim_product",
    "dim_seller",
    "dim_geography",
    "dim_date",
    "fact_order_items",
    "fact_orders",
    "fact_payments",
    "fact_reviews",
    "agg_sales_daily",
    "agg_delivery_daily",
)


class DuckDbCatalog:
    def __init__(self, config) -> None:
        self.config = config

    def _view_sql(self, table: str) -> str:
        path = (self.config.marts_dir / f"{table}.parquet").as_posix()
        if not (self.config.marts_dir / f"{table}.parquet").exists():
            raise FileNotFoundError(f"Mart not found: {path}")
        escaped = path.replace("'", "''")
        return (
            f"CREATE OR REPLACE VIEW v_{table} AS "
            f"SELECT * FROM read_parquet('{escaped}')"
        )

    def create(self) -> None:
        conn = ConnectionFactory(self.config).write()
        try:
            for table in VIEW_TABLES:
                conn.execute(self._view_sql(table))
        finally:
            conn.close()

    def list_views(self) -> list[str]:
        conn = ConnectionFactory(self.config).read_only()
        try:
            rows = conn.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'main' AND table_type = 'VIEW' "
                "ORDER BY table_name"
            ).fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()
