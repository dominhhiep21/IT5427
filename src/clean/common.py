"""Shared cleaning helpers."""

from __future__ import annotations

import pandas as pd


def normalize_text(series: pd.Series) -> pd.Series:
    """Trim, collapse whitespace, lowercase and apply Unicode NFC."""

    return (
        series.astype("string")
        .str.normalize("NFC")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )


def normalize_state(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.upper()


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def to_integer(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("Int64")


def parse_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def invalid_parse_mask(original: pd.Series, parsed: pd.Series) -> pd.Series:
    return original.notna() & parsed.isna()


def iqr_bounds(series: pd.Series, multiplier: float = 1.5) -> tuple[float, float]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    return float(q1 - multiplier * iqr), float(q3 + multiplier * iqr)


def null_counts(df: pd.DataFrame) -> dict[str, int]:
    counts = df.isna().sum()
    return {str(column): int(value) for column, value in counts.items() if value > 0}


def flag_counts(df: pd.DataFrame, columns: tuple[str, ...]) -> dict[str, int]:
    return {
        column: int(df[column].fillna(False).astype(bool).sum())
        for column in columns
        if column in df.columns
    }
