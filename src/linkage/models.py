"""Data model for record linkage: blocking rule, scored pair, skipped pair, result payload."""

from __future__ import annotations

import hashlib
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from src.common.exceptions import PipelineError

THRESHOLD = 0.85
"""BR4.6: decision threshold, fixed in code and never a configuration parameter."""

GEO_WEIGHT = 0.40
ORDER_WEIGHT = 0.60
"""BR4.5: the score leans on purchase behaviour because geography cannot separate two people."""

MAX_PAIRS = 10_000
"""BR4.10: result ceiling; `pairs_total` keeps the real count."""

BLOCKING_KEY_LENGTH = 5
"""BR4.1: the whole five-digit zip prefix; three digits would give 14.801.253 pairs."""

MATCHED = "Ghép"
REVIEW = "Xem lại"
DECISIONS = (MATCHED, REVIEW)
SKIPPED = "Bỏ qua"

CUSTOMER = "customer"
SELLER = "seller"
TARGET_ENTITIES = (CUSTOMER, SELLER)

MATCH_FIELDS = ("city", "product_id", "payment_value")
OUTPUT_DECIMALS = 4
SCORE_DECIMALS = 6

MISSING_CITY_REASON = "thiếu thành phố"
MISSING_ORDERS_REASON = "thiếu sản phẩm từ đơn hàng"
SELLER_NO_MARKER_REASON = "người bán không có khoá mốc trong nguồn, không đo được tỉ lệ ghép đúng"
NO_MATCHED_REASON = "không có cặp Ghép nào nên chưa đo được tỉ lệ ghép đúng"


class LinkageResultError(PipelineError):
    """A written linkage result does not read back as what was written."""


def clean_text(value: object) -> str:
    """Return a stripped string, mapping NaN/None onto the empty string."""

    if value is None:
        return ""
    if isinstance(value, float) and value != value:  # NaN
        return ""
    return str(value).strip()


def normalize_city(value: object) -> str:
    """BR4.2: drop accents, lowercase and collapse whitespace so 'São Paulo' meets 'Sao Paulo'."""

    text = clean_text(value)
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(stripped.lower().split())


def zip_prefix(value: object) -> str:
    """Return the whole five-digit zip prefix, keeping a leading zero and rejecting anything else."""

    text = clean_text(value)
    if not text:
        return ""
    if text.endswith(".0"):
        text = text[:-2]
    if not text.isdigit():
        return ""
    return text.zfill(BLOCKING_KEY_LENGTH)


def _digest(*parts: str) -> str:
    joined = "|".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def pair_id_for(target_entity: str, record_a: str, record_b: str) -> str:
    """Stable id for one pair, so a rerun on the same data yields the same `pair_id`."""

    return _digest(target_entity, record_a, record_b)


@dataclass(frozen=True)
class BlockingRule:
    """BR4.1: which records may be compared with which, before any scoring happens."""

    rule_id: str
    target_entity: str
    blocking_field: str
    blocking_key_length: int
    match_fields: tuple[str, ...]
    threshold: float


def blocking_rule(target_entity: str) -> BlockingRule:
    """Return the fixed blocking rule for `customer` or `seller`."""

    if target_entity == CUSTOMER:
        field_name = "customer_zip_code_prefix"
    elif target_entity == SELLER:
        field_name = "seller_zip_code_prefix"
    else:
        raise ValueError(f"target_entity không hợp lệ: {target_entity!r}")
    return BlockingRule(
        rule_id=f"BR4.1-{target_entity}",
        target_entity=target_entity,
        blocking_field=field_name,
        blocking_key_length=BLOCKING_KEY_LENGTH,
        match_fields=MATCH_FIELDS,
        threshold=THRESHOLD,
    )


@dataclass(frozen=True)
class MatchPair:
    """BR4.7 + BR4.6: one scored pair of distinct records, ordered, with its decision."""

    target_entity: str
    record_a: str
    record_b: str
    score: float
    geo_ratio: float
    order_ratio: float
    payment_similarity: float
    zip_prefix: str
    decision: str
    is_correct: bool | None = None

    def __post_init__(self) -> None:
        if self.record_a >= self.record_b:
            raise ValueError(
                f"cặp phải theo thứ tự record_a < record_b: {self.record_a!r} >= {self.record_b!r}"
            )
        if self.decision not in DECISIONS:
            raise ValueError(f"quyết định không hợp lệ: {self.decision!r}")

    @property
    def pair_id(self) -> str:
        return pair_id_for(self.target_entity, self.record_a, self.record_b)

    def to_dict(self) -> dict[str, Any]:
        """C5 payload for one pair; the score is written with four decimals (BR4.5)."""

        return {
            "pair_id": self.pair_id,
            "target_entity": self.target_entity,
            "record_a": self.record_a,
            "record_b": self.record_b,
            "score": round(self.score, OUTPUT_DECIMALS),
            "geo_ratio": round(self.geo_ratio, OUTPUT_DECIMALS),
            "order_ratio": round(self.order_ratio, OUTPUT_DECIMALS),
            "payment_similarity": round(self.payment_similarity, OUTPUT_DECIMALS),
            "zip_prefix": self.zip_prefix,
            "decision": self.decision,
            "is_correct": self.is_correct,
        }


@dataclass(frozen=True)
class SkippedPair:
    """A candidate pair that could not be scored because a match field is missing."""

    target_entity: str
    record_a: str
    record_b: str
    missing_fields: tuple[str, ...]
    reason: str

    @property
    def skip_id(self) -> str:
        return "skip-" + _digest(self.target_entity, self.record_a, self.record_b)

    def to_dict(self) -> dict[str, Any]:
        return {
            "skip_id": self.skip_id,
            "target_entity": self.target_entity,
            "record_a": self.record_a,
            "record_b": self.record_b,
            "missing_fields": list(self.missing_fields),
            "reason": self.reason,
        }


@dataclass
class LinkageResult:
    """The whole result for one target entity, shaped exactly like the C5 file payload."""

    target_entity: str
    run_id: str
    computed_at: str
    pairs: list[MatchPair] = field(default_factory=list)
    skipped: list[SkippedPair] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    threshold: float = THRESHOLD

    def to_dict(self) -> dict[str, Any]:
        """C5 payload; `summary`, `pairs` and `skipped` are always present, possibly empty."""

        return {
            "target_entity": self.target_entity,
            "run_id": self.run_id,
            "computed_at": self.computed_at,
            "threshold": self.threshold,
            "summary": dict(self.summary),
            "pairs": [pair.to_dict() for pair in self.pairs],
            "skipped": [pair.to_dict() for pair in self.skipped],
        }
