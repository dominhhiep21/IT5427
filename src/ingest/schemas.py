"""Schema contracts for the nine Olist CSV files."""

from __future__ import annotations

from src.common.types import TableSpec

TABLE_SPECS: dict[str, TableSpec] = {
    "orders": TableSpec(
        name="orders",
        file_name="olist_orders_dataset.csv",
        columns=(
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
        key_columns=("order_id",),
        expected_rows=99_441,
    ),
    "customers": TableSpec(
        name="customers",
        file_name="olist_customers_dataset.csv",
        columns=(
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
        key_columns=("customer_id",),
        expected_rows=99_441,
    ),
    "order_items": TableSpec(
        name="order_items",
        file_name="olist_order_items_dataset.csv",
        columns=(
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ),
        key_columns=("order_id", "order_item_id"),
        expected_rows=112_650,
    ),
    "payments": TableSpec(
        name="payments",
        file_name="olist_order_payments_dataset.csv",
        columns=(
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ),
        key_columns=("order_id", "payment_sequential"),
        expected_rows=103_886,
    ),
    "reviews": TableSpec(
        name="reviews",
        file_name="olist_order_reviews_dataset.csv",
        columns=(
            "review_id",
            "order_id",
            "review_score",
            "review_comment_title",
            "review_comment_message",
            "review_creation_date",
            "review_answer_timestamp",
        ),
        key_columns=("review_id", "order_id"),
        expected_rows=99_224,
    ),
    "products": TableSpec(
        name="products",
        file_name="olist_products_dataset.csv",
        columns=(
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
        key_columns=("product_id",),
        expected_rows=32_951,
    ),
    "sellers": TableSpec(
        name="sellers",
        file_name="olist_sellers_dataset.csv",
        columns=(
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ),
        key_columns=("seller_id",),
        expected_rows=3_095,
    ),
    "geolocation": TableSpec(
        name="geolocation",
        file_name="olist_geolocation_dataset.csv",
        columns=(
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ),
        key_columns=(),
        expected_rows=1_000_163,
    ),
    "translation": TableSpec(
        name="translation",
        file_name="product_category_name_translation.csv",
        columns=(
            "product_category_name",
            "product_category_name_english",
        ),
        key_columns=("product_category_name",),
        expected_rows=71,
    ),
}
