"""Hàm baseline một đặc trưng: miền giá trị, tính tất định và ba nhánh ModelError."""

from __future__ import annotations

import random

import pandas as pd
import pytest

from src.analytics.model import SPLIT_DATE, ModelError, measure_state_baseline


def _frame(rows: int = 220, *, single_class: bool = False) -> pd.DataFrame:
    rng = random.Random(7)
    dates = pd.date_range("2017-09-01", periods=rows, freq="D").strftime("%Y-%m-%d")
    states = ["SP", "RJ", "MG"] * (rows // 3) + ["SP"] * (rows % 3)
    if single_class:
        labels = [False] * rows
    else:
        labels = [bool(rng.randint(0, 1)) for _ in range(rows)]
    return pd.DataFrame(
        {
            "date_key": dates,
            "customer_state": states[:rows],
            "is_late": labels,
            "item_total": [float(rng.randint(1, 500)) for _ in range(rows)],
            "payment_type": ["credit_card"] * rows,
        }
    )


def test_returns_auc_in_open_unit_interval() -> None:
    auc = measure_state_baseline(_frame(), cut_date=SPLIT_DATE)
    assert 0.0 < auc < 1.0


def test_is_deterministic_across_calls() -> None:
    frame = _frame()
    assert measure_state_baseline(frame, cut_date=SPLIT_DATE) == measure_state_baseline(
        frame, cut_date=SPLIT_DATE
    )


def test_wrong_cut_date_raises_model_error() -> None:
    with pytest.raises(ModelError):
        measure_state_baseline(_frame(), cut_date="2019-01-01")


def test_empty_test_side_raises_model_error() -> None:
    frame = _frame()
    frame["date_key"] = "2017-01-01"
    with pytest.raises(ModelError):
        measure_state_baseline(frame, cut_date=SPLIT_DATE)


def test_single_class_test_side_raises_model_error() -> None:
    frame = _frame(single_class=True)
    with pytest.raises(ModelError):
        measure_state_baseline(frame, cut_date=SPLIT_DATE)


def test_missing_feature_column_raises_model_error() -> None:
    frame = _frame().drop(columns=["customer_state"])
    with pytest.raises(ModelError):
        measure_state_baseline(frame, cut_date=SPLIT_DATE)


def test_unknown_state_in_test_does_not_add_a_column() -> None:
    frame = _frame()
    frame.loc[frame.index[-1], "customer_state"] = "ZZ"
    auc = measure_state_baseline(frame, cut_date=SPLIT_DATE)
    assert 0.0 < auc < 1.0


def test_extra_numeric_column_does_not_change_the_result() -> None:
    """C1 — baseline chỉ dùng MỘT đặc trưng; cột khác phải bị bỏ qua hoàn toàn."""

    frame = _frame()
    baseline = measure_state_baseline(frame, cut_date=SPLIT_DATE)

    scrambled = frame.copy()
    scrambled["item_total"] = list(reversed(scrambled["item_total"].tolist()))
    dropped = frame.drop(columns=["item_total"])

    assert measure_state_baseline(scrambled, cut_date=SPLIT_DATE) == baseline
    assert measure_state_baseline(dropped, cut_date=SPLIT_DATE) == baseline
