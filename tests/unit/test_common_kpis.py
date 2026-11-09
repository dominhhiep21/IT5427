"""Unit test cho sổ KPI dùng chung ở `src/common/kpis.py` (BR3.2, BR3.9)."""

from __future__ import annotations

import pytest

from src.common.exceptions import SchemaError
from src.common.kpis import (
    COUNT_UNIT,
    KPI_LEDGER,
    MONEY_UNIT,
    PERCENT_UNIT,
    REVENUE_DEFINITION,
    TEMPLATE_IDS,
    KpiLedgerEntry,
    kpi,
    validate_ledger,
)

TEMPLATES = ("doanh_thu_theo_danh_muc", "doanh_thu_theo_thang", "ty_le_giao_tre_theo_bang")
REVENUE_TEMPLATES = ("doanh_thu_theo_danh_muc", "doanh_thu_theo_thang")


def test_ledger_holds_three_templates_and_the_count_entry():
    assert TEMPLATE_IDS == TEMPLATES
    assert set(KPI_LEDGER) == set(TEMPLATES) | {"so_dong"}


def test_revenue_kpis_carry_the_single_revenue_definition():
    for template_id in REVENUE_TEMPLATES:
        entry = KPI_LEDGER[template_id]

        assert entry.unit == MONEY_UNIT
        assert entry.revenue_definition == REVENUE_DEFINITION
        assert "freight_value" in entry.revenue_definition
        assert "delivered" in entry.revenue_definition


def test_units_are_closed_and_money_uses_brl():
    assert KPI_LEDGER["ty_le_giao_tre_theo_bang"].unit == PERCENT_UNIT
    assert KPI_LEDGER["so_dong"].unit == COUNT_UNIT
    assert {entry.unit for entry in KPI_LEDGER.values()} <= {MONEY_UNIT, PERCENT_UNIT, COUNT_UNIT}


def test_every_entry_states_a_title_and_a_formula():
    for entry in KPI_LEDGER.values():
        assert entry.kpi_id
        assert entry.title
        assert entry.formula


def test_kpi_lookup_by_id_returns_the_ledger_entry():
    entry = kpi("ty_le_giao_tre_theo_bang")

    assert entry.kpi_id == "ty_le_giao_tre_theo_bang"
    assert entry.reference_value is None


def test_kpi_lookup_of_an_unknown_id_raises():
    with pytest.raises(SchemaError) as caught:
        kpi("doanh_thu_theo_nam")

    assert "doanh_thu_theo_nam" in str(caught.value)


def test_validate_rejects_a_money_kpi_without_revenue_definition():
    broken = KpiLedgerEntry(
        kpi_id="doanh_thu_theo_nam",
        title="Doanh thu theo năm",
        formula="tổng price + freight_value của đơn delivered",
        revenue_definition="",
        unit=MONEY_UNIT,
    )

    with pytest.raises(SchemaError) as caught:
        validate_ledger({**KPI_LEDGER, "doanh_thu_theo_nam": broken})

    assert "doanh_thu_theo_nam" in str(caught.value)


def test_validate_rejects_a_duplicate_kpi_id():
    duplicated = dict(KPI_LEDGER)
    duplicated["ban_sao"] = KpiLedgerEntry(
        kpi_id="doanh_thu_theo_thang",
        title="Bản sao",
        formula="trùng mã",
        revenue_definition=REVENUE_DEFINITION,
        unit=MONEY_UNIT,
    )

    with pytest.raises(SchemaError):
        validate_ledger(duplicated)


def test_validate_rejects_an_unknown_unit():
    broken = KpiLedgerEntry(
        kpi_id="so_dong",
        title="Số dòng",
        formula="đếm số dòng",
        revenue_definition="",
        unit="dong",
    )

    with pytest.raises(SchemaError) as caught:
        validate_ledger({"so_dong": broken})

    assert "dong" in str(caught.value)


def test_validate_accepts_the_shipped_ledger():
    validate_ledger(KPI_LEDGER)
