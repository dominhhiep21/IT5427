"""Cleaning for order reviews."""

from __future__ import annotations

import pandas as pd

from src.clean.common import parse_datetime, to_integer


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["review_score"] = to_integer(out["review_score"])
    out["review_creation_date"] = parse_datetime(out["review_creation_date"])
    out["review_answer_timestamp"] = parse_datetime(out["review_answer_timestamp"])
    counts = out["order_id"].value_counts()
    out["multiple_reviews_per_order"] = out["order_id"].map(counts).fillna(0) > 1
    return out
