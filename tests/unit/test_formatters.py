"""Dashboard formatting tests."""

from __future__ import annotations

from src.dashboard.formatting import (
    format_brl,
    format_date,
    format_number,
    format_percent,
)


def test_brl_uses_brazilian_separators():
    assert format_brl(1234.5) == "R$ 1.234,50"


def test_number_and_percent():
    assert format_number(1234567) == "1.234.567"
    assert format_percent(8.111) == "8,11%"


def test_date():
    assert format_date("2018-10-17") == "17/10/2018"
    assert format_date(None) == ""
