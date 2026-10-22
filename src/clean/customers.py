"""Cleaning for the customers table."""

from __future__ import annotations

import pandas as pd

from src.clean.common import normalize_state, normalize_text, to_integer


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["customer_zip_code_prefix"] = to_integer(out["customer_zip_code_prefix"])
    out["customer_city_normalized"] = normalize_text(out["customer_city"])
    out["customer_state"] = normalize_state(out["customer_state"])
    return out
