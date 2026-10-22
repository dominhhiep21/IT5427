"""Cleaning for the sellers table."""

from __future__ import annotations

import pandas as pd

from src.clean.common import normalize_state, normalize_text, to_integer


def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["seller_zip_code_prefix"] = to_integer(out["seller_zip_code_prefix"])
    out["seller_city_normalized"] = normalize_text(out["seller_city"])
    out["seller_state"] = normalize_state(out["seller_state"])
    return out
