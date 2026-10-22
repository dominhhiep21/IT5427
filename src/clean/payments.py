"""Cleaning for order payments."""

from __future__ import annotations

import pandas as pd

from src.clean.common import to_integer, to_numeric


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["payment_sequential"] = to_integer(out["payment_sequential"])
    out["payment_installments"] = to_integer(out["payment_installments"])
    out["payment_value"] = to_numeric(out["payment_value"])
    out["payment_type"] = out["payment_type"].astype("string").str.strip()
    return out
