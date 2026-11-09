"""Các dataclass do tầng tích hợp trung gian trả về."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from src.common.exceptions import SchemaError

if TYPE_CHECKING:
    from src.integration.schema import EntityMapping, FieldMapping

STATUS_VALUES = frozenset(
    {
        "created",
        "approved",
        "invoiced",
        "processing",
        "shipped",
        "delivered",
        "unavailable",
        "canceled",
    }
)


class InvalidRecord(ValueError):
    """A source row cannot become a mediated record."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def _timestamp(value: object) -> datetime | None:
    text = _text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


@dataclass(frozen=True)
class DonHang:
    """One order row of the mediated schema."""

    ma_don: str
    ngay_dat: datetime
    trang_thai: str
    ma_khach: str
    bang_giao: str | None = None

    @classmethod
    def from_row(cls, row: Mapping[str, object]) -> DonHang:
        """Build a validated order from one mediated row."""

        ma_don = _text(row.get("ma_don"))
        if not ma_don:
            raise InvalidRecord("ma_don_rong", "Đơn hàng thiếu mã đơn.")
        ngay_dat = _timestamp(row.get("ngay_dat"))
        if ngay_dat is None:
            raise InvalidRecord("ngay_dat_rong", f"Đơn {ma_don} thiếu ngày đặt hợp lệ.")
        if ngay_dat > datetime.now():
            raise InvalidRecord(
                "ngay_dat_tuong_lai",
                f"Đơn {ma_don} có ngày đặt ở tương lai: {ngay_dat.isoformat()}.",
            )
        trang_thai = _text(row.get("trang_thai"))
        if trang_thai not in STATUS_VALUES:
            raise InvalidRecord(
                "trang_thai_ngoai_mien",
                f"Đơn {ma_don} có trạng thái ngoài miền: {trang_thai!r}.",
            )
        return cls(
            ma_don=ma_don,
            ngay_dat=ngay_dat,
            trang_thai=trang_thai,
            ma_khach=_text(row.get("ma_khach")),
            bang_giao=_text(row.get("bang_giao")) or None,
        )


@dataclass
class LoadResult:
    """Outcome of loading one mediated entity from its source CSVs."""

    orders: list[DonHang]
    rows_in: int
    rows_dropped: int
    drop_reasons: dict[str, int]
    elapsed_ms: int


@dataclass(frozen=True)
class RewriteStep:
    """One step of the mediated-to-source rewrite plan."""

    step: int
    mediated_entity: str
    source_table: str
    join_condition: str = ""


@dataclass(frozen=True)
class KpiDefinition:
    """Display definition of a KPI carried by a query result."""

    kpi_id: str
    title: str
    formula: str
    revenue_definition: str
    unit: str


@dataclass(frozen=True)
class QueryTemplate:
    """Một truy vấn mẫu: mẫu SQL nguồn khai tay, kế hoạch viết lại và KPI nó hiện thực."""

    template_id: str
    title: str
    mediated_query_text: str
    source_sql: str
    plan: tuple[RewriteStep, ...]
    kpi: KpiDefinition


@dataclass(frozen=True)
class KpiComparison:
    """Expected-versus-actual comparison for one group of one KPI."""

    kpi_id: str
    group_key: str
    expected_value: float
    actual_value: float
    delta: float
    tolerance: float
    matches: bool


@dataclass
class QueryRunResult:
    """Result of one mediated query rewritten onto the source tables."""

    plan_id: str
    template_id: str
    template_title: str
    mediated_query_text: str
    rewrite_plan: list[RewriteStep]
    source_sql: str
    rows: list[dict[str, object]]
    row_count: int
    elapsed_ms: int
    total_orders: int | None
    months: list[str] | None
    partial: list[str] | None
    kpi_definitions: list[KpiDefinition] = field(default_factory=list)
    kpi_comparison: list[KpiComparison] = field(default_factory=list)


@dataclass(frozen=True)
class PartialInfo:
    """Kênh "một phần" của C1: thực thể còn thiếu và lý do, đúng hình dạng entities.md."""

    missing: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class MediatedSchemaView:
    """Payload hợp đồng C1/C6: lược đồ đã kiểm, kèm thời lượng nạp và kênh một phần."""

    schema_kind: str
    entities: tuple[EntityMapping, ...]
    mappings: dict[str, tuple[FieldMapping, ...]]
    elapsed_ms: int
    partial: PartialInfo | None = None

    def entity(self, name: str) -> EntityMapping:
        """Trả một thực thể, hoặc ném SchemaError."""

        for item in self.entities:
            if item.name == name:
                return item
        raise SchemaError(f"Thực thể không có trong lược đồ: {name!r}")


@dataclass(frozen=True)
class MediatedFieldCatalogue:
    """Payload hợp đồng C2: danh mục "entity.field" theo thứ tự khai báo."""

    fields_by_entity: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class SourceProfile:
    """Hồ sơ một nguồn ứng viên, đủ tám dữ kiện khai trong tệp cấu hình (BR5.1)."""

    source_name: str
    label: str
    tables: tuple[str, ...]
    covered_fields: tuple[str, ...]
    coverage: str
    has_data: bool
    cost_level: int
    latency_ms: int
    is_simulated: bool


@dataclass(frozen=True)
class SourceChoice:
    """Một dòng quyết định cho cặp (truy vấn, nguồn); lý do luôn bằng chữ (BR5.5, BR5.8)."""

    query_id: str
    source_name: str
    is_selected: bool
    reason: str
    missing_fields: tuple[str, ...] = ()
    tables: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceCatalogue:
    """Payload C7: hồ sơ các nguồn, quyết định đã tính và ánh xạ truy vấn → trường cần."""

    sources: tuple[SourceProfile, ...]
    choices: tuple[SourceChoice, ...]
    query_fields: dict[str, tuple[str, ...]]
    partial_reason: str | None = None
    pending_query_id: str | None = None


@dataclass(frozen=True)
class SourceSelection:
    """Payload C3: nguồn đã chọn cho một truy vấn, kèm bản C7 đã cập nhật."""

    query_id: str
    selected_sources: tuple[SourceChoice, ...]
    rejected_sources: tuple[SourceChoice, ...]
    catalogue: SourceCatalogue
    missing_fields: tuple[str, ...] = ()
