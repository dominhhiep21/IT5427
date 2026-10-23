"""Formatting helpers for the dashboard."""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd


def _brazilian_number(value: float, decimals: int = 2) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_brl(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "R$ 0,00"
    return f"R$ {_brazilian_number(float(value), 2)}"


def format_number(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "0"
    return _brazilian_number(float(value), decimals)


def format_percent(value: float | int | None, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "0,00%"
    return f"{_brazilian_number(float(value), decimals)}%"


def format_date(value: str | date | datetime | pd.Timestamp | None) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return ""
    return timestamp.strftime("%d/%m/%Y")
