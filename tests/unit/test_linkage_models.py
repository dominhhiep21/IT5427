"""Unit tests for the record-linkage data model (BR4.1, BR4.5, BR4.7, C5 payload)."""

from __future__ import annotations

import pytest

from src.linkage.models import (
    GEO_WEIGHT,
    MAX_PAIRS,
    ORDER_WEIGHT,
    THRESHOLD,
    BlockingRule,
    LinkageResult,
    MatchPair,
    SkippedPair,
    blocking_rule,
    normalize_city,
)


def test_normalize_city_strips_accents_and_collapses_whitespace():
    assert normalize_city("  São   Paulo ") == "sao paulo"
    assert normalize_city("SAO PAULO") == "sao paulo"
    assert normalize_city("Ribeirão\tPreto") == "ribeirao preto"


def test_normalize_city_handles_blank_and_none():
    assert normalize_city("") == ""
    assert normalize_city("   ") == ""
    assert normalize_city(None) == ""


def test_match_pair_rejects_reversed_record_order():
    with pytest.raises(ValueError):
        MatchPair(
            target_entity="customer",
            record_a="b",
            record_b="a",
            score=0.9,
            geo_ratio=1.0,
            order_ratio=0.9,
            payment_similarity=0.0,
            zip_prefix="01310",
            decision="Ghép",
        )


def test_match_pair_rejects_unknown_decision():
    with pytest.raises(ValueError):
        MatchPair(
            target_entity="customer",
            record_a="a",
            record_b="b",
            score=0.9,
            geo_ratio=1.0,
            order_ratio=0.9,
            payment_similarity=0.0,
            zip_prefix="01310",
            decision="Bỏ",
        )


def test_match_pair_writes_score_with_four_decimals():
    pair = MatchPair(
        target_entity="customer",
        record_a="a",
        record_b="b",
        score=0.91234567,
        geo_ratio=0.9876543,
        order_ratio=0.8666666,
        payment_similarity=0.5,
        zip_prefix="01310",
        decision="Ghép",
        is_correct=True,
    )

    payload = pair.to_dict()

    assert payload["score"] == 0.9123
    assert pair.score == 0.91234567
    assert payload["decision"] == "Ghép"
    assert payload["is_correct"] is True
    assert payload["zip_prefix"] == "01310"


def test_pair_id_is_stable_and_depends_on_target_and_records():
    def make(target: str = "customer", record_a: str = "a", record_b: str = "b") -> MatchPair:
        return MatchPair(
            target_entity=target,
            record_a=record_a,
            record_b=record_b,
            score=0.9,
            geo_ratio=1.0,
            order_ratio=0.8,
            payment_similarity=0.0,
            zip_prefix="01310",
            decision="Ghép",
        )

    assert make().pair_id == make().pair_id
    assert make().pair_id != make(target="seller").pair_id
    assert make().pair_id != make(record_b="c").pair_id
    assert make().to_dict()["pair_id"] == make().pair_id


def test_linkage_result_serialises_summary_and_empty_lists():
    result = LinkageResult(
        target_entity="customer",
        run_id="run-1",
        computed_at="2026-11-06T00:00:00+00:00",
    )

    payload = result.to_dict()

    assert payload["target_entity"] == "customer"
    assert payload["run_id"] == "run-1"
    assert payload["threshold"] == THRESHOLD
    assert payload["summary"] == {}
    assert payload["pairs"] == []
    assert payload["skipped"] == []
    assert "summary" in payload and "skipped" in payload


def test_skipped_pair_serialises_missing_fields_and_reason():
    skipped = SkippedPair(
        target_entity="customer",
        record_a="a",
        record_b="b",
        missing_fields=("orders",),
        reason="một trong hai khách không có đơn hàng",
    )

    payload = skipped.to_dict()

    assert payload["missing_fields"] == ["orders"]
    assert payload["reason"] == "một trong hai khách không có đơn hàng"
    assert payload["skip_id"]
    assert payload["record_a"] == "a" and payload["record_b"] == "b"


def test_blocking_rule_is_fixed_for_both_targets():
    customer = blocking_rule("customer")
    seller = blocking_rule("seller")

    assert isinstance(customer, BlockingRule)
    assert customer.threshold == THRESHOLD == 0.85
    assert customer.blocking_key_length == 5
    assert customer.blocking_field == "customer_zip_code_prefix"
    assert seller.blocking_field == "seller_zip_code_prefix"
    assert customer.match_fields == seller.match_fields
    assert "city" in customer.match_fields
    assert "product_id" in customer.match_fields
    assert "payment_value" in customer.match_fields
    assert GEO_WEIGHT + ORDER_WEIGHT == pytest.approx(1.0)
    assert MAX_PAIRS == 10_000

    with pytest.raises(ValueError):
        blocking_rule("product")
