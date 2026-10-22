"""Customer and seller normalization tests."""

from __future__ import annotations

from src.clean.customers import clean_customers
from src.clean.sellers import clean_sellers


def test_customer_city_and_state_normalized(small_customers):
    cleaned = clean_customers(small_customers)
    first = cleaned.iloc[0]
    assert first["customer_city_normalized"] == "sao paulo"
    assert first["customer_state"] == "SP"
    assert first["customer_zip_code_prefix"] == 100


def test_seller_city_and_state_normalized(small_sellers):
    cleaned = clean_sellers(small_sellers)
    first = cleaned.iloc[0]
    assert first["seller_city_normalized"] == "sao paulo"
    assert first["seller_state"] == "SP"
