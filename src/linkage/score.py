"""Block, score and summarise candidate pairs (L2 of `logical-components.md`)."""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher

from src.linkage.index import EvidenceIndex
from src.linkage.models import (
    CUSTOMER,
    MATCHED,
    MAX_PAIRS,
    MISSING_CITY_REASON,
    MISSING_ORDERS_REASON,
    NO_MATCHED_REASON,
    OUTPUT_DECIMALS,
    REVIEW,
    SCORE_DECIMALS,
    SELLER_NO_MARKER_REASON,
    GEO_WEIGHT,
    ORDER_WEIGHT,
    THRESHOLD,
    BlockingRule,
    MatchPair,
    SkippedPair,
)

EQUALITY_TOLERANCE = 1e-9


@dataclass
class ScoringOutcome:
    """Every pair that reached the threshold, plus the counts the summary needs."""

    pairs: list[MatchPair] = field(default_factory=list)
    skipped: list[SkippedPair] = field(default_factory=list)
    pairs_scored: int = 0
    pairs_matched: int = 0
    pairs_review: int = 0
    pairs_skipped: int = 0


def string_ratio(left: str, right: str) -> float:
    """BR4.3: character-match ratio of two normalised strings, 0.0 when either is empty."""

    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    return SequenceMatcher(None, left, right).ratio()


def city_similarity(left: str, right: str) -> float:
    """Geographic evidence: how alike the two normalised city names are."""

    return string_ratio(left, right)


def _jaccard(left: frozenset, right: frozenset) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def order_similarity(left: frozenset[str], right: frozenset[str]) -> float:
    """BR4.4: Jaccard similarity of the two product-id sets."""

    return _jaccard(left, right)


def payment_similarity(left: frozenset[float], right: frozenset[float]) -> float:
    """BR4.4: share of orders whose amount appears in the other side; never enters the score."""

    if not left and not right:
        return 0.0
    shared = len(left & right)
    return shared / max(len(left), len(right), 1)


def decide(score: float) -> str | None:
    """BR4.6: `Ghép` above the threshold, `Xem lại` exactly on it, nothing below."""

    if score > THRESHOLD:
        return MATCHED
    if abs(score - THRESHOLD) <= EQUALITY_TOLERANCE:
        return REVIEW
    return None


def combined_score(geo_ratio: float, order_ratio: float) -> float:
    """BR4.5: weighted sum, kept to six decimals so the threshold comparison is stable."""

    return round(GEO_WEIGHT * geo_ratio + ORDER_WEIGHT * order_ratio, SCORE_DECIMALS)


def _missing_fields(left, right) -> tuple[str, ...]:
    missing: list[str] = []
    if not left.city or not right.city:
        missing.append("city")
    if not left.products or not right.products:
        missing.append("orders")
    return tuple(missing)


def _skip_reason(missing: tuple[str, ...]) -> str:
    reasons = []
    if "city" in missing:
        reasons.append(MISSING_CITY_REASON)
    if "orders" in missing:
        reasons.append(MISSING_ORDERS_REASON)
    return "; ".join(reasons)


def _is_correct(target_entity: str, left, right) -> bool | None:
    if target_entity != CUSTOMER:
        return None
    if not left.unique_id or not right.unique_id:
        return False
    return left.unique_id == right.unique_id


def blocking_groups(index: EvidenceIndex) -> dict[str, list[str]]:
    """BR4.1: records grouped by their whole zip prefix; a record without one forms no pair."""

    groups: dict[str, list[str]] = {}
    for record_id, evidence in index.records.items():
        if not evidence.zip_prefix:
            continue
        groups.setdefault(evidence.zip_prefix, []).append(record_id)
    for record_ids in groups.values():
        record_ids.sort()
    return groups


def score_pairs(index: EvidenceIndex, rule: BlockingRule) -> ScoringOutcome:
    """Score every candidate pair inside each blocking group and keep those over the threshold."""

    outcome = ScoringOutcome()
    for zip_value, record_ids in blocking_groups(index).items():
        for position, record_a in enumerate(record_ids):
            left = index.records[record_a]
            for record_b in record_ids[position + 1 :]:
                right = index.records[record_b]
                missing = _missing_fields(left, right)
                if missing:
                    outcome.skipped.append(
                        SkippedPair(
                            target_entity=rule.target_entity,
                            record_a=record_a,
                            record_b=record_b,
                            missing_fields=missing,
                            reason=_skip_reason(missing),
                        )
                    )
                    outcome.pairs_skipped += 1
                    continue

                geo_ratio = city_similarity(left.city, right.city)
                order_ratio = order_similarity(left.products, right.products)
                score = combined_score(geo_ratio, order_ratio)
                outcome.pairs_scored += 1
                decision = decide(score)
                if decision is None:
                    continue
                outcome.pairs.append(
                    MatchPair(
                        target_entity=rule.target_entity,
                        record_a=record_a,
                        record_b=record_b,
                        score=score,
                        geo_ratio=geo_ratio,
                        order_ratio=order_ratio,
                        payment_similarity=payment_similarity(left.payments, right.payments),
                        zip_prefix=zip_value,
                        decision=decision,
                        is_correct=_is_correct(rule.target_entity, left, right),
                    )
                )
                if decision == MATCHED:
                    outcome.pairs_matched += 1
                else:
                    outcome.pairs_review += 1

    return outcome


def cap(pairs: list[MatchPair], limit: int = MAX_PAIRS) -> tuple[list[MatchPair], int, bool]:
    """BR4.10: keep the `limit` highest scores (ties by `pair_id`), report the real total."""

    ordered = sorted(pairs, key=lambda pair: (-pair.score, pair.pair_id))
    total = len(ordered)
    truncated = total > limit
    return ordered[:limit], total, truncated


def summarise(outcome: ScoringOutcome, index: EvidenceIndex, limit: int = MAX_PAIRS) -> dict:
    """BR4.8, BR4.9, BR4.10: every count the result file carries, computed before capping."""

    _, total, truncated = cap(outcome.pairs, limit)
    if index.target_entity == CUSTOMER:
        correct = sum(1 for pair in outcome.pairs if pair.decision == MATCHED and pair.is_correct)
        correct_rate = (
            round(correct / outcome.pairs_matched, OUTPUT_DECIMALS) if outcome.pairs_matched else None
        )
        correct_rate_sample: int | None = correct
        correct_rate_reason = None if outcome.pairs_matched else NO_MATCHED_REASON
        duplicate_groups_reason = None
    else:
        correct_rate = None
        correct_rate_sample = None
        correct_rate_reason = SELLER_NO_MARKER_REASON
        duplicate_groups_reason = SELLER_NO_MARKER_REASON

    return {
        "pairs_scored": outcome.pairs_scored,
        "pairs_matched": outcome.pairs_matched,
        "pairs_review": outcome.pairs_review,
        "pairs_skipped": outcome.pairs_skipped,
        "pairs_total": total,
        "pairs_truncated": truncated,
        "records_scored": index.records_scored,
        "records_missing_match_fields": index.records_missing_match_fields,
        "duplicate_groups": index.duplicate_groups,
        "duplicate_groups_reason": duplicate_groups_reason,
        "correct_rate": correct_rate,
        "correct_rate_sample": correct_rate_sample,
        "correct_rate_reason": correct_rate_reason,
    }
