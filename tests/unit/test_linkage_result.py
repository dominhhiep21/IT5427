"""Unit tests for writing the C5 result file and for the pipeline call site (SR-U4-4..SR-U4-6)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.common.exceptions import SchemaError
from src.common.io import AtomicWriter
from src.common.logging import ERROR_CODES, JsonLogger, new_run_context
from src.linkage.models import MAX_PAIRS, LinkageResult, LinkageResultError, MatchPair, SkippedPair
from src.linkage.result import generate_linkage, write_result
from src.linkage.score import cap
from src.pipeline import stages

CUSTOMERS_HEADER = "customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state"
ORDERS_HEADER = (
    "order_id,customer_id,order_status,order_purchase_timestamp,"
    "order_approved_at,order_delivered_carrier_date,"
    "order_delivered_customer_date,order_estimated_delivery_date"
)
ITEMS_HEADER = "order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value"
PAYMENTS_HEADER = "order_id,payment_sequential,payment_type,payment_installments,payment_value"
SELLERS_HEADER = "seller_id,seller_zip_code_prefix,seller_city,seller_state"


def _write(config, name: str, header: str, rows: list[str]) -> None:
    text = header + "\n" + "".join(f"{row}\n" for row in rows)
    (Path(config.raw_csv_dir) / name).write_text(text, encoding="utf-8")


def _make_pair(position: int, score: float = 0.9) -> MatchPair:
    return MatchPair(
        target_entity="customer",
        record_a=f"{position:06d}a",
        record_b=f"{position:06d}b",
        score=score,
        geo_ratio=1.0,
        order_ratio=0.8333,
        payment_similarity=0.5,
        zip_prefix="01310",
        decision="Ghép",
        is_correct=True,
    )


def _summary(**overrides) -> dict:
    base = {
        "pairs_scored": 3,
        "pairs_matched": 2,
        "pairs_review": 0,
        "pairs_skipped": 0,
        "pairs_total": 2,
        "pairs_truncated": False,
        "records_scored": 4,
        "records_missing_match_fields": 0,
        "duplicate_groups": 1,
        "duplicate_groups_reason": None,
        "correct_rate": 1.0,
        "correct_rate_sample": 2,
        "correct_rate_reason": None,
    }
    base.update(overrides)
    return base


def _result(pairs: list[MatchPair], skipped: list[SkippedPair] | None = None, **summary) -> LinkageResult:
    return LinkageResult(
        target_entity="customer",
        run_id="run-1",
        computed_at="2026-11-06T00:00:00+00:00",
        pairs=pairs,
        skipped=skipped or [],
        summary=_summary(**summary),
    )


def test_write_result_writes_the_contract_file(config):
    result = _result([_make_pair(1), _make_pair(2)])

    path = write_result(config, result)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.name == "linkage-customer.json"
    assert path.parent == config.integration_dir
    assert payload["target_entity"] == "customer"
    assert payload["run_id"] == "run-1"
    assert payload["threshold"] == 0.85
    assert payload["summary"]["pairs_matched"] == 2
    assert len(payload["pairs"]) == 2
    assert payload["pairs"][0]["score"] == 0.9


def test_write_result_caps_the_list_and_keeps_the_file_under_five_megabytes(config):
    pairs = [_make_pair(position) for position in range(MAX_PAIRS + 1)]
    capped, total, truncated = cap(pairs)
    result = _result(capped, pairs_total=total, pairs_truncated=truncated)

    path = write_result(config, result)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert total == MAX_PAIRS + 1
    assert truncated is True
    assert len(payload["pairs"]) == MAX_PAIRS == min(payload["summary"]["pairs_total"], MAX_PAIRS)
    assert path.stat().st_size <= 5 * 1024 * 1024


def test_result_file_never_contains_a_customer_unique_id(config):
    """SR-U4-6: the ground-truth key is used for `is_correct` but never written out."""

    from src.linkage.index import Evidence, EvidenceIndex
    from src.linkage.models import blocking_rule
    from src.linkage.score import cap, score_pairs, summarise

    evidence = [
        Evidence(
            record_id="cust-a",
            city="sao paulo",
            zip_prefix="01001",
            products=frozenset({"p1", "p2"}),
            payments=frozenset({100.0}),
            order_count=1,
            unique_id="known-unique-id-0001",
        ),
        Evidence(
            record_id="cust-b",
            city="sao paulo",
            zip_prefix="01001",
            products=frozenset({"p1", "p2"}),
            payments=frozenset({100.0}),
            order_count=1,
            unique_id="known-unique-id-0001",
        ),
    ]
    index = EvidenceIndex(
        target_entity="customer",
        records={item.record_id: item for item in evidence},
        duplicate_groups=1,
        records_missing_match_fields=0,
    )
    outcome = score_pairs(index, blocking_rule("customer"))
    pairs, _, _ = cap(outcome.pairs)

    result = LinkageResult(
        target_entity="customer",
        run_id="run-1",
        computed_at="2026-11-06T00:00:00+00:00",
        pairs=pairs,
        skipped=outcome.skipped,
        summary=summarise(outcome, index),
    )
    path = write_result(config, result)
    text = path.read_text(encoding="utf-8")

    assert pairs, "fixture must produce a matched pair"
    assert pairs[0].is_correct is True, "the ground-truth key must drive is_correct"
    assert "customer_unique_id" not in text
    assert "known-unique-id-0001" not in text


def test_write_result_keeps_an_empty_skipped_list(config):
    result = _result([_make_pair(1)], pairs_total=1, pairs_matched=1)

    path = write_result(config, result)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert "skipped" in payload
    assert payload["skipped"] == []


def test_write_result_keeps_a_skipped_pair_with_its_reason(config):
    skipped = [
        SkippedPair(
            target_entity="customer",
            record_a="c1",
            record_b="c2",
            missing_fields=("orders",),
            reason="một trong hai không có đơn hàng",
        )
    ]
    result = _result([_make_pair(1)], skipped=skipped, pairs_total=1, pairs_matched=1, pairs_skipped=1)

    path = write_result(config, result)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert len(payload["skipped"]) == payload["summary"]["pairs_skipped"] == 1
    assert payload["skipped"][0]["missing_fields"] == ["orders"]


def test_read_back_mismatch_raises(config, monkeypatch):
    result = _result([_make_pair(1)])
    monkeypatch.setattr(
        "src.linkage.result._read_payload",
        lambda path: {"summary": {"pairs_total": 5, "pairs_skipped": 0}, "pairs": [], "skipped": []},
    )

    with pytest.raises(LinkageResultError) as caught:
        write_result(config, result)

    assert "kiểm lại" in str(caught.value) or "lệch" in str(caught.value)


def _tiny_sources(config) -> None:
    _write(
        config,
        "olist_customers_dataset.csv",
        CUSTOMERS_HEADER,
        [
            "c1,u1,01310,São Paulo,SP",
            "c2,u1,01310,Sao Paulo,SP",
            "c3,u2,20000,Rio de Janeiro,RJ",
        ],
    )
    _write(
        config,
        "olist_sellers_dataset.csv",
        SELLERS_HEADER,
        [
            "s1,01310,São Paulo,SP",
            "s2,01310,Sao Paulo,SP",
        ],
    )
    _write(
        config,
        "olist_orders_dataset.csv",
        ORDERS_HEADER,
        [
            "o1,c1,delivered,2017-01-01 10:00:00,,,,",
            "o2,c2,delivered,2017-02-01 10:00:00,,,,",
            "o3,c3,delivered,2017-03-01 10:00:00,,,,",
        ],
    )
    _write(
        config,
        "olist_order_items_dataset.csv",
        ITEMS_HEADER,
        [
            "o1,1,p1,s1,2017-01-05,10.0,1.0",
            "o1,2,p2,s1,2017-01-05,10.0,1.0",
            "o2,1,p1,s1,2017-02-05,10.0,1.0",
            "o2,2,p2,s2,2017-02-05,10.0,1.0",
            "o3,1,p9,s2,2017-03-05,10.0,1.0",
        ],
    )
    _write(
        config,
        "olist_order_payments_dataset.csv",
        PAYMENTS_HEADER,
        [
            "o1,1,credit_card,1,20.0",
            "o2,1,credit_card,1,20.0",
            "o3,1,boleto,1,10.0",
        ],
    )


def _events(logger) -> list[dict]:
    if not logger.run.log_path.exists():
        return []
    return [
        json.loads(line)
        for line in logger.run.log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_generate_linkage_writes_the_file_and_logs_started_and_completed(config):
    _tiny_sources(config)
    run = new_run_context("linkage", config.logs_dir, config.temp_dir)
    logger = JsonLogger(run, console=False)
    writer = AtomicWriter(run, config.parquet_compression)

    result = generate_linkage(config, "customer", run, writer, logger)

    path = config.integration_dir / "linkage-customer.json"
    assert path.exists()
    assert result.summary["pairs_scored"] >= 1
    events = _events(logger)
    assert [event["event"] for event in events] == [
        "integration.linkage.started",
        "integration.linkage.completed",
    ]
    completed = events[-1]
    assert completed["target_entity"] == "customer"
    assert completed["pairs_scored"] == result.summary["pairs_scored"]
    assert completed["pairs_truncated"] is False
    assert completed["elapsed_ms"] >= 0


def test_linkage_events_never_carry_record_values(config):
    _tiny_sources(config)
    run = new_run_context("linkage", config.logs_dir, config.temp_dir)
    logger = JsonLogger(run, console=False)
    writer = AtomicWriter(run, config.parquet_compression)

    generate_linkage(config, "customer", run, writer, logger)

    events = _events(logger)
    forbidden = {
        "c1",
        "c2",
        "c3",
        "s1",
        "s2",
        "u1",
        "u2",
        "01310",
        "20000",
        "sao paulo",
        "São Paulo",
        "rio de janeiro",
        "Rio de Janeiro",
    }
    assert set(events[0]) == {"timestamp", "level", "run_id", "stage", "event", "target_entity"}
    assert set(events[1]) == {
        "timestamp",
        "level",
        "run_id",
        "stage",
        "event",
        "target_entity",
        "pairs_scored",
        "pairs_matched",
        "pairs_review",
        "pairs_skipped",
        "pairs_truncated",
        "elapsed_ms",
    }
    for event in events:
        for value in event.values():
            if isinstance(value, str):
                assert value not in forbidden


def test_generate_linkage_logs_a_closed_error_code_and_reraise(config, monkeypatch):
    _tiny_sources(config)
    run = new_run_context("linkage", config.logs_dir, config.temp_dir)
    logger = JsonLogger(run, console=False)
    writer = AtomicWriter(run, config.parquet_compression)

    def broken(config_arg, target):
        raise SchemaError("customers: thiếu cột customer_city")

    monkeypatch.setattr("src.linkage.result.build_index", broken)
    with pytest.raises(SchemaError):
        generate_linkage(config, "seller", run, writer, logger)

    events = _events(logger)
    assert events[0]["event"] == "integration.linkage.started"
    failed = events[-1]
    assert failed["event"] == "integration.linkage.failed"
    assert failed["error_code"] in ERROR_CODES
    assert failed["target_entity"] == "seller"
    assert not (config.integration_dir / "linkage-seller.json").exists()


def test_pipeline_runs_linkage_for_each_target_and_keeps_going_after_a_failure(monkeypatch):
    calls: list[str] = []

    def fake_generate(config, target, run, writer, logger):
        calls.append(target)
        if target == "customer":
            raise SchemaError("customers: thiếu cột")
        return "seller-result"

    monkeypatch.setattr(stages, "generate_linkage", fake_generate)

    with pytest.raises(SchemaError):
        stages._run_linkage(None, None, None, None)

    assert calls == ["customer", "seller"]
