"""Chấm một dòng hàng từ trạng thái đã lưu: xác suất, ngưỡng, ba đóng góp gộp theo trường."""

from __future__ import annotations

from dataclasses import replace

import pandas as pd
import pytest

from src.analytics.model import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    ModelError,
    encode_features,
    build_feature_frame,
    score_item,
)
from src.analytics.persistence import fit_persistable

THRESHOLD = 0.4


def _training_frame(rows: int = 40) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "item_count": [1.0 + i % 3 for i in range(rows)],
            "item_total": [10.0 + i for i in range(rows)],
            "item_price_max": [5.0 + i % 9 for i in range(rows)],
            "payment_installments": [1.0 + i % 4 for i in range(rows)],
            "handling_days": [float(i % 5) for i in range(rows)],
            "approval_days": [float(i % 3) for i in range(rows)],
            "payment_type": ["credit_card", "boleto"] * (rows // 2),
            "customer_state": ["SP", "RJ"] * (rows // 2),
            "customer_region": ["Sudeste"] * rows,
            "purchase_month": [str(1 + i % 12) for i in range(rows)],
            "purchase_weekday": [str(i % 7) for i in range(rows)],
            "seller_state": ["SP", "RJ"] * (rows // 2),
            "has_items": [True] * rows,
            "has_payment": [True] * rows,
        }
    )


@pytest.fixture()
def fitted():
    frame = _training_frame()
    labels = pd.Series([bool(i % 3) for i in range(len(frame))])
    train_matrix, _ = encode_features(build_feature_frame(frame), build_feature_frame(frame))
    scaler_means = train_matrix[list(NUMERIC_FEATURES)].mean().to_numpy()
    scaler_scales = train_matrix[list(NUMERIC_FEATURES)].std(ddof=0).replace(0, 1).to_numpy()
    categories = {
        column: sorted({"unknown"} | set(frame[column].astype(str))) for column in CATEGORICAL_FEATURES
    }
    return fit_persistable(
        train_matrix,
        labels,
        categories=categories,
        scaler_means=scaler_means,
        scaler_scales=scaler_scales,
    )


def _item(**overrides):
    base = {
        "seller_state": "SP",
        "customer_state": "SP",
        "order_date": "2018-05-10",
        "item_price": 50.0,
        "handling_days": 2.0,
        "approval_days": 1.0,
        "item_count": 1,
        "payment_type": "credit_card",
        "installments": 1,
        "has_items": True,
        "has_payment": True,
    }
    base.update(overrides)
    return base


def test_probability_is_a_proportion(fitted) -> None:
    outcome = score_item(fitted, _item(), threshold=THRESHOLD)
    assert 0.0 <= outcome.probability <= 1.0


def test_verdict_follows_the_reported_threshold(fitted) -> None:
    outcome = score_item(fitted, _item(), threshold=THRESHOLD)
    expected = "at_or_above_threshold" if outcome.probability >= THRESHOLD else "below_threshold"
    assert outcome.verdict == expected


def test_exactly_three_contributions(fitted) -> None:
    outcome = score_item(fitted, _item(), threshold=THRESHOLD)
    assert len(outcome.contributions) == 3


def test_no_two_contributions_share_a_field(fitted) -> None:
    outcome = score_item(fitted, _item(), threshold=THRESHOLD)
    fields = [item.field for item in outcome.contributions]
    assert len(set(fields)) == len(fields)


def test_contributions_are_grouped_by_field_not_by_one_hot_column(fitted) -> None:
    outcome = score_item(fitted, _item(), threshold=THRESHOLD)
    assert all("=" not in item.field for item in outcome.contributions)


def test_same_input_gives_the_same_probability(fitted) -> None:
    first = score_item(fitted, _item(), threshold=THRESHOLD)
    second = score_item(fitted, _item(), threshold=THRESHOLD)
    assert first.probability == second.probability
    assert first.contributions == second.contributions


def test_missing_field_names_the_field(fitted) -> None:
    broken = _item()
    broken.pop("customer_state")
    with pytest.raises(ModelError) as error:
        score_item(fitted, broken, threshold=THRESHOLD)
    assert "customer_state" in str(error.value)


def test_flags_are_part_of_the_matrix(fitted) -> None:
    outcome = score_item(fitted, _item(has_items=False), threshold=THRESHOLD)
    assert 0.0 <= outcome.probability <= 1.0
    assert all(item.field not in {"has_items="} for item in outcome.contributions)


def test_customer_region_comes_from_the_fitted_state_map(fitted) -> None:
    model = replace(fitted, state_regions={"SP": "Sudeste"})
    outcome = score_item(model, _item(customer_state="SP"), threshold=THRESHOLD)
    assert outcome.contributions
    outcome_unknown = score_item(model, _item(customer_state="ZZ"), threshold=THRESHOLD)
    assert outcome_unknown.probability != outcome.probability


def test_item_total_is_price_times_count() -> None:
    from src.analytics.model import _serve_features

    frame = _serve_features(
        {
            "seller_state": "SP",
            "customer_state": "SP",
            "order_date": "2018-05-10",
            "item_price": 10.0,
            "handling_days": 1.0,
            "approval_days": 1.0,
            "item_count": 3,
            "payment_type": "credit_card",
            "installments": 1,
            "has_items": True,
            "has_payment": True,
        },
        {"SP": "Sudeste"},
    )
    assert float(frame.iloc[0]["item_total"]) == 30.0
    assert frame.iloc[0]["customer_region"] == "Sudeste"


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("item_price", -5.0, "item_price"),
        ("item_count", 0, "item_count"),
        ("handling_days", -3.0, "handling_days"),
        ("approval_days", -1.0, "approval_days"),
        ("approval_days", 999.0, "approval_days"),
        ("installments", 0, "installments"),
        ("customer_state", "SÃO PAULO", "customer_state"),
        ("seller_state", "S", "seller_state"),
    ],
)
def test_out_of_domain_input_names_the_field(fitted, field: str, value: object, expected: str) -> None:
    with pytest.raises(ModelError) as error:
        score_item(fitted, _item(**{field: value}), threshold=THRESHOLD)
    assert expected in str(error.value)


def test_whole_save_load_score_path_uses_the_saved_region_map(fitted, tmp_path) -> None:  # noqa: ANN001
    from src.analytics.persistence import load_model, save_model

    model = replace(fitted, state_regions={"SP": "Sudeste"})
    save_model(model, tmp_path)
    loaded = load_model(tmp_path)
    assert loaded is not None
    direct = score_item(model, _item(customer_state="SP"), threshold=THRESHOLD)
    served = score_item(loaded, _item(customer_state="SP"), threshold=THRESHOLD)
    assert served.probability == direct.probability
