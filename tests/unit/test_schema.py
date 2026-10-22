"""Schema contract tests."""

from __future__ import annotations

import pytest

from src.common.exceptions import SchemaError
from src.common.io import validate_columns
from src.ingest.schemas import TABLE_SPECS


def test_orders_schema_matches(small_orders):
    validate_columns(small_orders, TABLE_SPECS["orders"])


def test_missing_column_raises(small_orders):
    broken = small_orders.drop(columns=["order_status"])
    with pytest.raises(SchemaError):
        validate_columns(broken, TABLE_SPECS["orders"])


def test_wrong_order_raises(small_orders):
    broken = small_orders[list(reversed(small_orders.columns))]
    with pytest.raises(SchemaError):
        validate_columns(broken, TABLE_SPECS["orders"])
