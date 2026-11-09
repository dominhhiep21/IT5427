"""Unit tests for blocking, scoring and summarising candidate pairs (BR4.1–BR4.10)."""

from __future__ import annotations

import time

import pytest

from src.linkage.index import Evidence, EvidenceIndex
from src.linkage.models import MAX_PAIRS, THRESHOLD, MatchPair, blocking_rule
from src.linkage.score import (
    cap,
    city_similarity,
    decide,
    order_similarity,
    payment_similarity,
    score_pairs,
    summarise,
)


def _evidence(
    record_id: str,
    city: str = "sao paulo",
    zip_code: str = "01310",
    products: tuple[str, ...] = ("p1", "p2", "p3", "p4"),
    payments: tuple[float, ...] = (),
    unique_id: str | None = "u1",
    order_count: int | None = None,
) -> Evidence:
    return Evidence(
        record_id=record_id,
        city=city,
        zip_prefix=zip_code,
        products=frozenset(products),
        payments=frozenset(payments),
        order_count=len(products) if order_count is None else order_count,
        unique_id=unique_id,
    )


def _index(target: str, *records: Evidence) -> EvidenceIndex:
    return EvidenceIndex(
        target_entity=target,
        records={record.record_id: record for record in records},
        duplicate_groups=0,
        records_missing_match_fields=0,
    )


def test_blocking_only_pairs_records_in_the_same_five_digit_group():
    index = _index(
        "customer",
        _evidence("c1", zip_code="01310"),
        _evidence("c2", zip_code="01310"),
        _evidence("c3", zip_code="20000"),
        _evidence("c4", zip_code="20001"),
    )

    outcome = score_pairs(index, blocking_rule("customer"))

    assert outcome.pairs_scored == 1
    assert {(pair.record_a, pair.record_b) for pair in outcome.pairs} <= {("c1", "c2")}
    assert all("c3" not in (pair.record_a, pair.record_b) for pair in outcome.pairs)
    assert all("c4" not in (pair.record_a, pair.record_b) for pair in outcome.pairs)


def test_records_without_a_zip_prefix_never_form_a_pair():
    index = _index(
        "customer",
        _evidence("c1", zip_code=""),
        _evidence("c2", zip_code=""),
    )

    outcome = score_pairs(index, blocking_rule("customer"))

    assert outcome.pairs_scored == 0
    assert outcome.skipped == []


def test_pairs_are_generated_once_in_string_order():
    index = _index(
        "customer",
        _evidence("b"),
        _evidence("a"),
    )

    outcome = score_pairs(index, blocking_rule("customer"))

    assert len(outcome.pairs) == 1
    assert outcome.pairs[0].record_a == "a"
    assert outcome.pairs[0].record_b == "b"


def test_pair_without_orders_is_skipped_with_a_reason():
    index = _index(
        "customer",
        _evidence("c1", products=("p1",)),
        _evidence("c2", products=()),
    )

    outcome = score_pairs(index, blocking_rule("customer"))

    assert outcome.pairs == []
    assert outcome.pairs_scored == 0
    assert outcome.pairs_skipped == 1
    skipped = outcome.skipped[0]
    assert skipped.missing_fields == ("orders",)
    assert skipped.reason
    assert (skipped.record_a, skipped.record_b) == ("c1", "c2")


def test_pair_without_city_is_skipped_with_missing_city():
    index = _index(
        "customer",
        _evidence("c1", city="sao paulo"),
        _evidence("c2", city=""),
    )

    outcome = score_pairs(index, blocking_rule("customer"))

    assert outcome.pairs_skipped == 1
    assert outcome.skipped[0].missing_fields == ("city",)
    assert outcome.pairs_scored == 0


def test_score_is_the_weighted_sum_of_both_evidence_signals():
    index = _index(
        "customer",
        _evidence("c1", products=("p1", "p2", "p3", "p4")),
        _evidence("c2", products=("p1", "p2", "p3", "p4", "p5")),
    )

    pair = score_pairs(index, blocking_rule("customer")).pairs[0]

    assert pair.geo_ratio == pytest.approx(1.0)
    assert pair.order_ratio == pytest.approx(0.8)
    assert pair.score == pytest.approx(0.4 * 1.0 + 0.6 * 0.8)
    assert pair.score == pytest.approx(0.88)
    assert pair.decision == "Ghép"


def test_similarity_helpers_are_pure_over_strings_and_sets():
    assert city_similarity("sao paulo", "sao paulo") == 1.0
    assert city_similarity("sao paulo", "") == 0.0
    assert city_similarity("abc", "abd") == pytest.approx(2 / 3)
    assert city_similarity("sao paulo", "sao paulo sp") == pytest.approx(2 * 9 / (9 + 12))
    assert order_similarity(frozenset({"a"}), frozenset()) == 0.0
    assert order_similarity(frozenset({"a", "b"}), frozenset({"b", "c"})) == pytest.approx(1 / 3)
    assert payment_similarity(frozenset({10.0, 20.0}), frozenset({10.0})) == pytest.approx(0.5)
    assert payment_similarity(frozenset(), frozenset()) == 0.0


def test_above_threshold_is_matched_and_exactly_on_threshold_is_review():
    index = _index(
        "customer",
        _evidence("c1", products=("p1", "p2", "p3", "p4")),
        _evidence("c2", products=("p1", "p2", "p3", "p4", "p5")),
        _evidence("c3", products=("p1", "p2", "p3")),
        _evidence("c4", products=("p1", "p2")),
    )

    outcome = score_pairs(index, blocking_rule("customer"))
    by_pair = {(pair.record_a, pair.record_b): pair for pair in outcome.pairs}

    assert by_pair[("c1", "c2")].score == pytest.approx(0.88)
    assert by_pair[("c1", "c2")].decision == "Ghép"
    assert by_pair[("c1", "c3")].decision == "Xem lại"
    assert by_pair[("c1", "c3")].score == pytest.approx(0.85)
    assert ("c1", "c4") not in by_pair
    assert ("c3", "c4") not in by_pair


def test_decide_uses_the_threshold_and_the_one_e_nine_tolerance():
    assert decide(0.86) == "Ghép"
    assert decide(0.85) == "Xem lại"
    assert decide(0.85 + 1e-10) == "Ghép"
    assert decide(0.8499) is None
    assert decide(0.0) is None


def test_below_threshold_pairs_are_scored_but_not_written():
    index = _index(
        "customer",
        _evidence("c1", products=("p1", "p2")),
        _evidence("c2", products=("p1", "p2")),
        _evidence("c3", city="rio de janeiro", products=("x1",)),
    )

    outcome = score_pairs(index, blocking_rule("customer"))

    assert outcome.pairs_scored == 3
    assert {(pair.record_a, pair.record_b) for pair in outcome.pairs} == {("c1", "c2")}


def test_counters_and_summary_for_customers():
    index = _index(
        "customer",
        _evidence("c1", products=("p1", "p2", "p3", "p4"), unique_id="u1"),
        _evidence("c2", products=("p1", "p2", "p3", "p4", "p5"), unique_id="u1"),
        _evidence("c3", products=("p1", "p2", "p3"), unique_id="u2"),
        _evidence("c4", city="rio de janeiro", products=("x1",), unique_id="u3"),
        _evidence("c5", city="", products=("x2",), unique_id="u4"),
    )

    outcome = score_pairs(index, blocking_rule("customer"))
    summary = summarise(outcome, index)

    assert outcome.pairs_matched == 1
    assert outcome.pairs_review == 1
    assert outcome.pairs_skipped == 4
    assert outcome.pairs_scored == 6
    assert summary["pairs_scored"] == 6
    assert summary["pairs_matched"] == 1
    assert summary["pairs_review"] == 1
    assert summary["pairs_skipped"] == 4
    assert summary["pairs_total"] == 2
    assert summary["pairs_truncated"] is False
    assert summary["correct_rate"] == pytest.approx(1.0)
    assert summary["correct_rate_sample"] == 1
    assert summary["correct_rate_reason"] is None
    assert summary["duplicate_groups"] == index.duplicate_groups
    assert summary["records_scored"] == index.records_scored


def test_summary_leaves_correct_rate_empty_for_sellers():
    index = _index(
        "seller",
        _evidence("s1", products=("p1", "p2", "p3", "p4"), unique_id=None),
        _evidence("s2", products=("p1", "p2", "p3", "p4", "p5"), unique_id=None),
    )

    summary = summarise(score_pairs(index, blocking_rule("seller")), index)

    assert summary["correct_rate"] is None
    assert summary["correct_rate_sample"] is None
    assert summary["correct_rate_reason"]
    assert summary["duplicate_groups"] == 0
    assert summary["duplicate_groups_reason"]


def test_summary_reports_no_correct_rate_without_a_matched_pair():
    index = _index(
        "customer",
        _evidence("c1", products=("p1", "p2", "p3", "p4")),
        _evidence("c2", products=("p1", "p2", "p3")),
    )

    summary = summarise(score_pairs(index, blocking_rule("customer")), index)

    assert summary["pairs_matched"] == 0
    assert summary["pairs_review"] == 1
    assert summary["correct_rate"] is None
    assert summary["correct_rate_sample"] == 0
    assert summary["correct_rate_reason"]


def test_cap_keeps_the_highest_scores_and_reports_the_real_total():
    index = _index(
        "customer",
        _evidence("c1", products=("p1", "p2", "p3", "p4")),
        _evidence("c2", products=("p1", "p2", "p3", "p4", "p5")),
        _evidence("c3", products=("p1", "p2", "p3", "p4", "p6")),
        _evidence("c4", products=("p1", "p2", "p3", "p4", "p7")),
    )

    outcome = score_pairs(index, blocking_rule("customer"))
    pairs, total, truncated = cap(outcome.pairs, limit=1)
    summary = summarise(outcome, index, limit=1)

    assert total == len(outcome.pairs) > 1
    assert truncated is True
    assert len(pairs) == 1
    assert pairs[0].score == max(pair.score for pair in outcome.pairs)
    assert summary["pairs_total"] == total
    assert summary["pairs_truncated"] is True
    assert summary["pairs_matched"] == outcome.pairs_matched
    assert MAX_PAIRS == 10_000
    assert THRESHOLD == 0.85


def test_cap_orders_by_pair_id_when_scores_are_equal():
    pairs = [
        MatchPair(
            target_entity="customer",
            record_a=f"r{position}",
            record_b="z",
            score=0.9,
            geo_ratio=1.0,
            order_ratio=0.8333,
            payment_similarity=0.0,
            zip_prefix="01310",
            decision="Ghép",
        )
        for position in (3, 1, 2)
    ]

    kept, _, _ = cap(pairs, limit=3)

    assert [pair.pair_id for pair in kept] == sorted(pair.pair_id for pair in pairs)
    assert [pair.pair_id for pair in cap(pairs, limit=3)[0]] == [pair.pair_id for pair in kept]


def test_scoring_two_hundred_thousand_pairs_stays_under_sixty_seconds():
    cities = [f"cidade {position}" for position in range(20)]
    records = [
        _evidence(
            f"r{position:04d}",
            city=cities[position % len(cities)],
            products=(f"p{position % 50}", f"p{(position + 1) % 50}", f"p{(position + 2) % 50}"),
            unique_id=f"u{position}",
        )
        for position in range(700)
    ]
    index = _index("customer", *records)

    started = time.perf_counter()
    outcome = score_pairs(index, blocking_rule("customer"))
    elapsed = time.perf_counter() - started

    assert outcome.pairs_scored > 200_000
    assert elapsed < 60.0
