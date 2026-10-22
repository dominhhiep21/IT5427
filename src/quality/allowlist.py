"""Known anomaly counts for the full Olist batch."""

EXPECTED_ANOMALIES: dict[str, int] = {
    "orders_without_items": 775,
    "orders_without_payment": 1,
    "customer_zips_missing_geo": 278,
    "seller_zips_missing_geo": 7,
    "products_missing_category": 610,
    "orders_multiple_reviews": 547,
    "geo_exact_duplicates": 261_831,
    "geo_outside_bbox": 42,
    "geo_zips_without_coord": 5,
    "price_outliers": 8_427,
}
