"""Ngưỡng chọn trên lưới, làm tròn bốn chữ số, ngưỡng là nguồn duy nhất (BR2.5)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics.model import (
    MODEL_DIGITS,
    THRESHOLD_GRID,
    THRESHOLD_METHOD,
    ModelError,
    build_model_block,
    choose_threshold,
)


def _scores() -> tuple[pd.Series, pd.Series]:
    labels = pd.Series([False, False, True, True, False, True])
    scores = pd.Series([0.10, 0.30, 0.55, 0.75, 0.45, 0.90])
    return labels, scores


def test_threshold_comes_from_the_grid() -> None:
    labels, scores = _scores()
    point = choose_threshold(labels, scores)
    assert point.threshold in THRESHOLD_GRID


def test_threshold_is_strictly_inside_the_open_unit_interval() -> None:
    labels, scores = _scores()
    point = choose_threshold(labels, scores)
    assert 0 < point.threshold < 1


def test_precision_and_recall_are_proportions() -> None:
    labels, scores = _scores()
    point = choose_threshold(labels, scores)
    assert 0 <= point.precision <= 1
    assert 0 <= point.recall <= 1


def test_threshold_outside_the_interval_is_an_error() -> None:
    split = {
        "train_start": "2018-01-01",
        "train_end": "2018-02-01",
        "test_start": "2018-02-02",
        "test_end": "2018-03-01",
        "train_n": 10,
        "test_n": 4,
    }
    with pytest.raises(ModelError):
        build_model_block(split, 0.6, 1.5, 0.5, 0.4, flagged=2)


def test_block_rounds_to_four_digits_and_records_the_method() -> None:
    split = {
        "train_start": "2018-01-01",
        "train_end": "2018-02-01",
        "test_start": "2018-02-02",
        "test_end": "2018-03-01",
        "train_n": 10,
        "test_n": 4,
    }
    block = build_model_block(split, 0.123456789, 0.4, 0.5, 0.25, flagged=2)
    assert block.auc == round(0.123456789, MODEL_DIGITS)
    assert block.counts["threshold_method"] == THRESHOLD_METHOD


def test_counts_add_up_to_the_test_split() -> None:
    split = {
        "train_start": "2018-01-01",
        "train_end": "2018-02-01",
        "test_start": "2018-02-02",
        "test_end": "2018-03-01",
        "train_n": 10,
        "test_n": 4,
    }
    block = build_model_block(split, 0.6, 0.4, 0.5, 0.5, flagged=3)
    assert block.counts["flagged"] + block.counts["not_flagged"] == block.counts["total"]
    assert block.counts["total"] == split["test_n"]
