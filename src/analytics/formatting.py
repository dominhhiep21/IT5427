"""Định dạng số kiểu Việt Nam và bảng Markdown cho báo cáo phân tích."""

from __future__ import annotations

import math
import numbers

import numpy as np
import pandas as pd


def _swap_separators(text: str) -> str:
    """1,234,567.89 -> 1.234.567,89."""

    return text.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def _is_missing(value) -> bool:
    if value is None or value is pd.NA or value is pd.NaT:
        return True
    return isinstance(value, float) and math.isnan(value)


def fmt_int(value) -> str:
    if _is_missing(value):
        return "–"
    return _swap_separators(f"{int(round(float(value))):,}")


def fmt_num(value, digits: int = 2) -> str:
    if _is_missing(value):
        return "–"
    return _swap_separators(f"{float(value):,.{digits}f}")


def fmt_money(value) -> str:
    return "–" if _is_missing(value) else f"{fmt_num(value, 2)} BRL"


def fmt_pct(value, digits: int = 2) -> str:
    return "–" if _is_missing(value) else f"{fmt_num(value, digits)}%"


def fmt_signed_pct(value, digits: int = 2) -> str:
    if _is_missing(value):
        return "–"
    sign = "+" if float(value) > 0 else ""
    return f"{sign}{fmt_num(value, digits)}%"


def fmt_p_value(value: float) -> str:
    return "< 0,001" if value < 0.001 else fmt_num(value, 3)


def _cell(value, column: str) -> str:
    if _is_missing(value):
        return "–"
    if isinstance(value, (bool, np.bool_)):
        return "có" if value else "không"
    if isinstance(value, str):
        return value.replace("|", "\\|")
    if isinstance(value, numbers.Integral) and not column.endswith("_pct"):
        return fmt_int(value)
    return fmt_num(value, 2)


def to_markdown(
    frame: pd.DataFrame,
    headers: dict[str, str] | None = None,
    limit: int | None = None,
) -> str:
    """Bảng Markdown: cột chữ căn trái, cột số căn phải; `headers` đổi tên và chọn cột."""

    columns = list(headers) if headers else list(frame.columns)
    labels = [headers[column] if headers else column for column in columns]
    rows = frame[columns] if limit is None else frame[columns].head(limit)

    numeric = [pd.api.types.is_numeric_dtype(frame[column]) for column in columns]
    lines = [
        "| " + " | ".join(labels) + " |",
        "| " + " | ".join("---:" if is_number else "---" for is_number in numeric) + " |",
    ]
    for record in rows.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(_cell(value, column) for value, column in zip(record, columns)) + " |")
    return "\n".join(lines)
