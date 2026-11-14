"""Hợp đồng 14 đặc trưng: tên, thứ tự, nhóm, danh sách cấm, thứ tự mã hoá (BR2.3)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics.model import (
    CATEGORICAL_FEATURES,
    FEATURES,
    FLAG_FEATURES,
    FORBIDDEN_COLUMNS,
    NUMERIC_FEATURES,
    ModelError,
    build_feature_frame,
    encode_features,
    validate_features,
)


def _frame(rows: int = 6) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "item_count": [1.0 + i for i in range(rows)],
            "item_total": [10.0 + i for i in range(rows)],
            "item_price_max": [5.0 + i for i in range(rows)],
            "payment_installments": [1.0 + i % 3 for i in range(rows)],
            "handling_days": [float(i) for i in range(rows)],
            "approval_days": [float(i % 2) for i in range(rows)],
            "payment_type": ["credit_card", "boleto"] * (rows // 2),
            "customer_state": ["SP", "RJ", "MG"] * (rows // 3) + ["SP"] * (rows % 3),
            "customer_region": ["Sudeste", "Nordeste"] * (rows // 2),
            "purchase_month": [str(1 + i % 12) for i in range(rows)],
            "purchase_weekday": [str(i % 7) for i in range(rows)],
            "seller_state": ["SP", "RJ"] * (rows // 2),
            "has_items": [True] * rows,
            "has_payment": [True] * rows,
            "order_id": [f"o{i}" for i in range(rows)],
            "order_item_id": [1] * rows,
            "date_key": ["2018-01-01"] * rows,
        }
    )


def test_the_contract_has_fourteen_names_in_order() -> None:
    assert len(FEATURES) == 14
    assert FEATURES[:11] == (
        "item_count",
        "item_total",
        "item_price_max",
        "payment_type",
        "payment_installments",
        "customer_state",
        "customer_region",
        "purchase_month",
        "purchase_weekday",
        "has_items",
        "has_payment",
    )
    assert FEATURES[11:] == ("seller_state", "handling_days", "approval_days")


def test_the_groups_add_up_to_the_contract() -> None:
    assert len(CATEGORICAL_FEATURES) == 6
    assert len(NUMERIC_FEATURES) == 6
    assert len(FLAG_FEATURES) == 2
    assert set(FEATURES) == set(CATEGORICAL_FEATURES) | set(NUMERIC_FEATURES) | set(FLAG_FEATURES)


def test_both_raw_milestones_are_forbidden() -> None:
    assert "order_approved_at" in FORBIDDEN_COLUMNS
    assert "order_delivered_carrier_date" in FORBIDDEN_COLUMNS
    assert set(FEATURES) & set(FORBIDDEN_COLUMNS) == set()


def test_validate_features_accepts_the_contract() -> None:
    assert validate_features() is None


def test_validate_features_refuses_a_reordered_list() -> None:
    with pytest.raises(ModelError):
        validate_features(tuple(reversed(FEATURES)))


def test_feature_frame_carries_exactly_the_contract_columns() -> None:
    matrix = build_feature_frame(_frame())
    assert list(matrix.columns) == list(FEATURES)


def test_missing_contract_column_is_an_error() -> None:
    broken = _frame().drop(columns=["seller_state"])
    with pytest.raises(ModelError):
        build_feature_frame(broken)


def test_encoded_order_is_numeric_then_flags_then_one_hot() -> None:
    frame = _frame()
    train_matrix, _ = encode_features(build_feature_frame(frame), build_feature_frame(frame))

    head = list(train_matrix.columns)
    assert head[: len(NUMERIC_FEATURES)] == list(NUMERIC_FEATURES)
    assert head[len(NUMERIC_FEATURES) : len(NUMERIC_FEATURES) + 2] == list(FLAG_FEATURES)
    assert len(head) > len(FEATURES)


def test_feature_names_are_the_expanded_matrix_columns_not_the_contract() -> None:
    frame = _frame()
    train_matrix, _ = encode_features(build_feature_frame(frame), build_feature_frame(frame))

    feature_names = list(train_matrix.columns)
    assert len(feature_names) > 14
    assert feature_names != list(FEATURES)
    assert any(name.startswith("seller_state=") for name in feature_names)
