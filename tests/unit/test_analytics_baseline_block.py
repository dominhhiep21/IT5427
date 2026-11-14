"""Baseline, hai cờ và mốc sàn: hành vi của khối mô hình v3 (BR2.6, NFR5)."""

from __future__ import annotations

import pytest

from src.analytics.model import (
    AUC_TARGET,
    MODEL_AUC_FLOOR,
    ModelError,
    beats_floor,
    build_model_block,
    validate_cohort_counts,
)

SPLIT = {
    "train_start": "2018-01-01",
    "train_end": "2018-02-01",
    "test_start": "2018-02-02",
    "test_end": "2018-03-01",
    "train_n": 10,
    "test_n": 5,
}
COHORTS = {
    "cohort_rows": 110195,
    "cohort_orders": 96476,
    "late_rows": 8713,
    "excluded_missing_carrier": 2,
}


def _block(auc: float, baseline: float, flagged: int = 2):
    return build_model_block(
        SPLIT, auc, 0.4, 0.5, 0.4, flagged, auc_tree=0.61, baseline_auc=baseline, cohort_counts=COHORTS
    )


def test_cohort_counts_gate_accepts_the_baseline() -> None:
    assert validate_cohort_counts(COHORTS) is None


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("cohort_rows", 1),
        ("cohort_orders", 1),
        ("late_rows", 1),
        ("excluded_missing_carrier", 0),
    ],
)
def test_cohort_counts_gate_names_the_counter_that_drifted(key: str, value: int) -> None:
    drifted = dict(COHORTS, **{key: value})
    with pytest.raises(ModelError) as error:
        validate_cohort_counts(drifted)
    assert key in str(error.value)


def test_cohort_counts_gate_refuses_a_missing_counter() -> None:
    broken = dict(COHORTS)
    broken.pop("cohort_orders")
    with pytest.raises(ModelError) as error:
        validate_cohort_counts(broken)
    assert "cohort_orders" in str(error.value)


def test_counts_have_nine_keys() -> None:
    block = _block(0.68, 0.55)
    assert set(block.counts) == {
        "flagged",
        "not_flagged",
        "total",
        "threshold_method",
        "auc_below_target",
        "cohort_rows",
        "cohort_orders",
        "late_rows",
        "excluded_missing_carrier",
    }


def test_counts_add_up_and_match_the_test_split() -> None:
    block = _block(0.68, 0.55)
    assert block.counts["flagged"] + block.counts["not_flagged"] == block.counts["total"]
    assert block.counts["total"] == SPLIT["test_n"]


def test_beats_baseline_is_the_comparison_on_rounded_values() -> None:
    above = _block(0.68, 0.55)
    assert above.beats_baseline is (above.auc > above.baseline_auc)
    below = _block(0.50, 0.62)
    assert below.beats_baseline is False


def test_auc_below_target_uses_the_rounded_value() -> None:
    just_below = _block(AUC_TARGET - 0.00001, 0.5)
    assert just_below.counts["auc_below_target"] is False
    clearly_below = _block(0.60, 0.5)
    assert clearly_below.counts["auc_below_target"] is True


def test_block_carries_eleven_fields() -> None:
    block = _block(0.68, 0.55)
    payload = block.to_dict()
    assert set(payload) == {
        "target",
        "split",
        "auc",
        "threshold",
        "precision",
        "recall",
        "counts",
        "unit",
        "auc_tree",
        "baseline_auc",
        "beats_baseline",
    }
    assert payload["unit"] == "dòng hàng"


def test_beats_floor_both_branches() -> None:
    assert beats_floor(0.70, 0.62) is True
    assert beats_floor(0.60, 0.62) is False
    assert beats_floor(MODEL_AUC_FLOOR, 0.10) is True


def test_floor_outside_the_interval_is_an_error() -> None:
    with pytest.raises(ModelError):
        beats_floor(0.7, 0.5, floor=1.5)
