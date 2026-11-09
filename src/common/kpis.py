"""Sổ KPI dùng chung: ba truy vấn mẫu, định nghĩa doanh thu và đơn vị (BR3.2, BR3.9)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from src.common.exceptions import SchemaError

# Một định nghĩa doanh thu duy nhất cho mọi KPI doanh thu (BR3.2, Q1 = A).
REVENUE_DEFINITION = "price + freight_value của đơn delivered"
DELIVERED_STATUS = "delivered"

MONEY_UNIT = "BRL"
PERCENT_UNIT = "percent"
COUNT_UNIT = "count"
UNITS = frozenset({MONEY_UNIT, PERCENT_UNIT, COUNT_UNIT})

CATEGORY_TEMPLATE = "doanh_thu_theo_danh_muc"
MONTH_TEMPLATE = "doanh_thu_theo_thang"
LATE_TEMPLATE = "ty_le_giao_tre_theo_bang"
TEMPLATE_IDS = (CATEGORY_TEMPLATE, MONTH_TEMPLATE, LATE_TEMPLATE)

# Mã KPI cho dòng đếm: số nhóm của mẫu doanh thu, số đơn đã giao của mẫu giao trễ.
COUNT_KPI_ID = "so_dong"


@dataclass(frozen=True)
class KpiLedgerEntry:
    """Một dòng của sổ KPI: mã, nhãn, công thức, định nghĩa doanh thu, đơn vị."""

    kpi_id: str
    title: str
    formula: str
    revenue_definition: str
    unit: str
    reference_value: float | None = None


KPI_LEDGER: dict[str, KpiLedgerEntry] = {
    CATEGORY_TEMPLATE: KpiLedgerEntry(
        kpi_id=CATEGORY_TEMPLATE,
        title="Doanh thu theo danh mục",
        formula=(
            "tổng price + freight_value của các dòng hàng thuộc đơn delivered, "
            "nhóm theo tên danh mục sản phẩm, sắp giảm dần"
        ),
        revenue_definition=REVENUE_DEFINITION,
        unit=MONEY_UNIT,
    ),
    MONTH_TEMPLATE: KpiLedgerEntry(
        kpi_id=MONTH_TEMPLATE,
        title="Doanh thu theo tháng",
        formula=(
            "tổng price + freight_value của các dòng hàng thuộc đơn delivered, "
            "nhóm theo tháng của ngày đặt, sắp tăng dần"
        ),
        revenue_definition=REVENUE_DEFINITION,
        unit=MONEY_UNIT,
    ),
    LATE_TEMPLATE: KpiLedgerEntry(
        kpi_id=LATE_TEMPLATE,
        title="Tỷ lệ giao trễ theo bang",
        formula=(
            "100 * số đơn delivered có ngày giao thực tế muộn hơn ngày dự kiến / "
            "số đơn delivered, nhóm theo bang giao, làm tròn 2 chữ số"
        ),
        revenue_definition="",
        unit=PERCENT_UNIT,
    ),
    COUNT_KPI_ID: KpiLedgerEntry(
        kpi_id=COUNT_KPI_ID,
        title="Số dòng kết quả",
        formula="đếm số nhóm của mẫu doanh thu, hoặc số đơn delivered của mẫu giao trễ",
        revenue_definition="",
        unit=COUNT_UNIT,
    ),
}


def validate_ledger(entries: Mapping[str, KpiLedgerEntry]) -> None:
    """Từ chối sổ KPI trùng mã, sai đơn vị, hoặc KPI doanh thu thiếu định nghĩa (BR3.2)."""

    seen: dict[str, KpiLedgerEntry] = {}
    for key, entry in entries.items():
        if entry.kpi_id in seen:
            raise SchemaError(f"Sổ KPI khai trùng mã {entry.kpi_id!r}.")
        seen[entry.kpi_id] = entry
        if entry.unit not in UNITS:
            raise SchemaError(f"Đơn vị của KPI {entry.kpi_id!r} không hợp lệ: {entry.unit!r}")
        if entry.unit == MONEY_UNIT and not entry.revenue_definition:
            raise SchemaError(
                f"KPI doanh thu {entry.kpi_id!r} thiếu định nghĩa doanh thu (phải là {REVENUE_DEFINITION!r})."
            )
        if key != entry.kpi_id:
            raise SchemaError(f"Sổ KPI khai {key!r} nhưng mã bên trong là {entry.kpi_id!r}.")


def kpi(kpi_id: str) -> KpiLedgerEntry:
    """Tra một dòng của sổ KPI, hoặc ném SchemaError khi mã lạ."""

    entry = KPI_LEDGER.get(kpi_id)
    if entry is None:
        raise SchemaError(f"KPI không có trong sổ: {kpi_id!r}")
    return entry


validate_ledger(KPI_LEDGER)
