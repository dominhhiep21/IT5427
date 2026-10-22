"""Reusable data-quality checks."""

from __future__ import annotations

import pandas as pd

from src.common.types import CheckResult


def _result(
    check_id: str,
    name: str,
    actual: object,
    expected: object,
    details: str = "",
) -> CheckResult:
    return CheckResult(
        check_id=check_id,
        name=name,
        passed=actual == expected,
        expected=expected,
        actual=actual,
        details=details,
    )


def check_unique(
    df: pd.DataFrame,
    columns: tuple[str, ...] | list[str],
    check_id: str,
    name: str | None = None,
) -> CheckResult:
    duplicates = int(df.duplicated(subset=list(columns), keep=False).sum())
    return _result(
        check_id,
        name or f"unique {columns}",
        duplicates,
        0,
        f"duplicate rows: {duplicates}",
    )


def check_foreign_key(
    child: pd.DataFrame,
    child_column: str,
    parent: pd.DataFrame,
    parent_column: str,
    check_id: str,
    name: str | None = None,
) -> CheckResult:
    valid = set(parent[parent_column].dropna().tolist())
    missing_mask = child[child_column].isna() | ~child[child_column].isin(valid)
    missing = int(missing_mask.sum())
    return _result(
        check_id,
        name or f"{child_column} -> {parent_column}",
        missing,
        0,
        f"orphan/null rows: {missing}",
    )


def check_row_count(
    df: pd.DataFrame,
    expected: int,
    check_id: str,
    name: str | None = None,
) -> CheckResult:
    return _result(check_id, name or "row count", len(df), expected)


def check_between(
    df: pd.DataFrame,
    column: str,
    low: float,
    high: float,
    check_id: str,
    name: str | None = None,
) -> CheckResult:
    values = pd.to_numeric(df[column], errors="coerce")
    invalid = int((values.notna() & ((values < low) | (values > high))).sum())
    return _result(
        check_id,
        name or f"{column} between {low} and {high}",
        invalid,
        0,
    )


def check_min(
    df: pd.DataFrame,
    column: str,
    minimum: float,
    check_id: str,
    name: str | None = None,
) -> CheckResult:
    values = pd.to_numeric(df[column], errors="coerce")
    invalid = int((values.notna() & (values < minimum)).sum())
    return _result(
        check_id,
        name or f"{column} >= {minimum}",
        invalid,
        0,
    )


def check_allowed_values(
    df: pd.DataFrame,
    column: str,
    allowed: set[str],
    check_id: str,
    name: str | None = None,
) -> CheckResult:
    values = df[column].astype("string")
    invalid = int((values.notna() & ~values.isin(allowed)).sum())
    return _result(
        check_id,
        name or f"{column} in allowed values",
        invalid,
        0,
    )
