"""Chia tập theo `order_id`: không đơn nào nằm hai phía, cỡ mẫu đếm theo dòng (BR2.2)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics.model import ModelError, split_frame, split_summary


def _frame(rows: int = 6) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1", "o1", "o2", "o3", "o4", "o5"][:rows],
            "order_item_id": [1, 2, 1, 1, 1, 1][:rows],
            "date_key": [
                "2018-03-30",
                "2018-03-30",
                "2018-03-31",
                "2018-04-01",
                "2018-04-02",
                "2018-04-03",
            ][:rows],
            "is_late": [False, True, False, True, False, True][:rows],
        }
    )


def test_every_row_of_one_order_lands_on_the_same_side() -> None:
    train, test = split_frame(_frame())
    assert set(train["order_id"]) & set(test["order_id"]) == set()
    assert {"o1", "o2"} <= set(train["order_id"])
    assert {"o3", "o4", "o5"} <= set(test["order_id"])


def test_the_intersection_of_order_ids_is_empty() -> None:
    train, test = split_frame(_frame())
    assert train["order_id"].nunique() + test["order_id"].nunique() == 5


def test_an_order_on_the_cut_date_belongs_to_the_test_side() -> None:
    _, test = split_frame(_frame())
    assert "o3" in set(test["order_id"])


def test_rows_are_split_with_their_order_not_by_row() -> None:
    train, _ = split_frame(_frame())
    assert len(train) == 3
    assert int(train["order_id"].value_counts()["o1"]) == 2


def test_empty_side_is_an_error() -> None:
    frame = _frame()
    frame["date_key"] = "2018-01-01"
    with pytest.raises(ModelError):
        split_frame(frame)


def test_split_summary_counts_rows_and_dates() -> None:
    train, test = split_frame(_frame())
    summary = split_summary(train, test, expected_total=len(train) + len(test))
    assert summary["train_n"] == 3
    assert summary["test_n"] == 3
    assert summary["train_end"] < summary["test_start"]


def test_frame_without_order_id_splits_by_row_explicitly() -> None:
    frame = _frame().drop(columns=["order_id"])
    train, test = split_frame(frame)
    assert len(train) + len(test) == len(frame)
    assert train["date_key"].max() < test["date_key"].min()
