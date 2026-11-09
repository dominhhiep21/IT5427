"""Viết lại ba truy vấn mẫu sang SQL nguồn, chạy trên DuckDB và đối chiếu KPI (U3)."""

from __future__ import annotations

import csv
import time
import uuid
from collections.abc import Callable, Mapping
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from src.common.exceptions import (
    KpiMismatchError,
    PipelineError,
    QueryExecutionError,
    SchemaError,
)
from src.common.kpis import (
    CATEGORY_TEMPLATE,
    COUNT_KPI_ID,
    DELIVERED_STATUS,
    LATE_TEMPLATE,
    MONEY_UNIT,
    MONTH_TEMPLATE,
    PERCENT_UNIT,
    TEMPLATE_IDS,
    KpiLedgerEntry,
    kpi,
)
from src.common.logging import JsonLogger, NullLogger, normalise_error_code
from src.config import load_config
from src.integration.models import (
    STATUS_VALUES,
    KpiComparison,
    KpiDefinition,
    QueryRunResult,
    QueryTemplate,
    RewriteStep,
)
from src.integration.schema import SOURCE_TABLES

NULL_GROUP_KEY = "unknown"  # nhãn của nhóm thiếu giá trị, cùng quy ước src/clean/products.py
ALL_GROUPS = "__all__"

TOLERANCE_MONEY = 0.01
TOLERANCE_COUNT = 0.0
TOLERANCE_PERCENT = 0.01
SLOW_QUERY_MS = 2000

COUNT_MODE_GROUPS = "groups"
COUNT_MODE_ORDERS = "orders"

PARAM_KEYS = ("ngay_tu", "ngay_den", "trang_thai")
ALLOWED_PARAMS = frozenset(PARAM_KEYS)
DATE_KEYS = ("ngay_tu", "ngay_den")

ORDER_ITEMS = "olist_order_items_dataset"
ORDERS = "olist_orders_dataset"
CUSTOMERS = "olist_customers_dataset"
PRODUCTS = "olist_products_dataset"

DATE_COLUMNS: dict[str, tuple[str, ...]] = {
    ORDERS: (
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ),
    ORDER_ITEMS: ("shipping_limit_date",),
}

STATUS_PREDICATE = "(? = '' OR o.order_status = ?)"
DATE_PREDICATE = (
    "(? = '' OR o.order_purchase_timestamp >= TRY_CAST(? AS DATE)) "
    "AND (? = '' OR o.order_purchase_timestamp < TRY_CAST(? AS DATE) + INTERVAL 1 DAY)"
)
TOTAL_ORDERS_SQL = (
    f"SELECT COUNT(DISTINCT o.order_id) FROM {ORDERS} o WHERE {STATUS_PREDICATE} AND {DATE_PREDICATE}"
)

SOURCE_SQL: dict[str, str] = {
    CATEGORY_TEMPLATE: (
        "SELECT p.product_category_name AS nhom, "
        "SUM(COALESCE(i.price, 0) + COALESCE(i.freight_value, 0)) AS gia_tri, "
        "COUNT(*) AS so_dong "
        f"FROM {ORDERS} o "
        f"JOIN {ORDER_ITEMS} i ON i.order_id = o.order_id "
        f"JOIN {PRODUCTS} p ON p.product_id = i.product_id "
        f"WHERE {STATUS_PREDICATE} AND {DATE_PREDICATE} "
        "GROUP BY p.product_category_name "
        "ORDER BY gia_tri DESC"
    ),
    MONTH_TEMPLATE: (
        "SELECT strftime(o.order_purchase_timestamp, '%Y-%m') AS thang, "
        "SUM(COALESCE(i.price, 0) + COALESCE(i.freight_value, 0)) AS gia_tri, "
        "COUNT(*) AS so_dong "
        f"FROM {ORDERS} o "
        f"JOIN {ORDER_ITEMS} i ON i.order_id = o.order_id "
        f"WHERE {STATUS_PREDICATE} AND {DATE_PREDICATE} "
        "GROUP BY thang "
        "ORDER BY thang"
    ),
    LATE_TEMPLATE: (
        "SELECT c.customer_state AS nhom, "
        "ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date > "
        "o.order_estimated_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) AS ty_le, "
        "COUNT(*) AS so_dong, "
        "SUM(CASE WHEN o.order_delivered_customer_date > "
        "o.order_estimated_delivery_date THEN 1 ELSE 0 END) AS so_tre "
        f"FROM {ORDERS} o "
        f"JOIN {CUSTOMERS} c ON c.customer_id = o.customer_id "
        f"WHERE o.order_status = '{DELIVERED_STATUS}' AND {STATUS_PREDICATE} AND {DATE_PREDICATE} "
        "GROUP BY c.customer_state "
        "ORDER BY ty_le DESC"
    ),
}

MEDIATED_QUERY_TEXT: dict[str, str] = {
    CATEGORY_TEMPLATE: (
        "SELECT san_pham.ten_danh_muc AS nhom, SUM(mat_hang.gia + mat_hang.gia_van_chuyen) "
        "AS gia_tri, COUNT(*) AS so_dong FROM don_hang JOIN mat_hang "
        "ON don_hang.ma_don = mat_hang.ma_don JOIN san_pham "
        "ON mat_hang.ma_san_pham = san_pham.ma_san_pham "
        "WHERE don_hang.trang_thai = 'delivered' GROUP BY nhom ORDER BY gia_tri DESC"
    ),
    MONTH_TEMPLATE: (
        "SELECT thang(don_hang.ngay_dat) AS thang, SUM(mat_hang.gia + mat_hang.gia_van_chuyen) "
        "AS gia_tri, COUNT(*) AS so_dong FROM don_hang "
        "JOIN mat_hang ON don_hang.ma_don = mat_hang.ma_don "
        "WHERE don_hang.trang_thai = 'delivered' GROUP BY thang ORDER BY thang"
    ),
    LATE_TEMPLATE: (
        "SELECT don_hang.bang_giao AS nhom, "
        "100.0 * dem(don_hang.ngay_giao_thuc_te > don_hang.ngay_giao_du_kien) / COUNT(*) AS ty_le, "
        "COUNT(*) AS so_dong, dem(don_hang.ngay_giao_thuc_te > don_hang.ngay_giao_du_kien) AS so_tre "
        "FROM don_hang WHERE don_hang.trang_thai = 'delivered' GROUP BY nhom ORDER BY ty_le DESC"
    ),
}

PLANS: dict[str, tuple[RewriteStep, ...]] = {
    CATEGORY_TEMPLATE: (
        RewriteStep(1, "don_hang", ORDERS),
        RewriteStep(2, "mat_hang", ORDER_ITEMS, "don_hang.ma_don = mat_hang.ma_don"),
        RewriteStep(3, "san_pham", PRODUCTS, "mat_hang.ma_san_pham = san_pham.ma_san_pham"),
    ),
    MONTH_TEMPLATE: (
        RewriteStep(1, "don_hang", ORDERS),
        RewriteStep(2, "mat_hang", ORDER_ITEMS, "don_hang.ma_don = mat_hang.ma_don"),
    ),
    LATE_TEMPLATE: (
        RewriteStep(1, "don_hang", ORDERS),
        RewriteStep(2, "don_hang", CUSTOMERS, "don_hang.ma_khach = customers.customer_id"),
    ),
}

TEMPLATE_TABLES: dict[str, tuple[str, ...]] = {
    CATEGORY_TEMPLATE: (ORDERS, ORDER_ITEMS, PRODUCTS),
    MONTH_TEMPLATE: (ORDERS, ORDER_ITEMS),
    LATE_TEMPLATE: (ORDERS, CUSTOMERS),
}

TEMPLATE_COLUMNS: dict[str, dict[str, tuple[str, ...]]] = {
    CATEGORY_TEMPLATE: {
        ORDERS: ("order_id", "order_status", "order_purchase_timestamp"),
        ORDER_ITEMS: ("order_id", "product_id", "price", "freight_value"),
        PRODUCTS: ("product_id", "product_category_name"),
    },
    MONTH_TEMPLATE: {
        ORDERS: ("order_id", "order_status", "order_purchase_timestamp"),
        ORDER_ITEMS: ("order_id", "price", "freight_value"),
    },
    LATE_TEMPLATE: {
        ORDERS: (
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
        CUSTOMERS: ("customer_id", "customer_state"),
    },
}

TEMPLATE_MEDIATED_FIELDS: dict[str, tuple[str, ...]] = {
    CATEGORY_TEMPLATE: (
        "don_hang.ma_don",
        "don_hang.trang_thai",
        "mat_hang.ma_don",
        "mat_hang.gia",
        "mat_hang.gia_van_chuyen",
        "mat_hang.ma_san_pham",
        "san_pham.ma_san_pham",
        "san_pham.ten_danh_muc",
    ),
    MONTH_TEMPLATE: (
        "don_hang.ma_don",
        "don_hang.ngay_dat",
        "don_hang.trang_thai",
        "mat_hang.ma_don",
        "mat_hang.gia",
        "mat_hang.gia_van_chuyen",
    ),
    LATE_TEMPLATE: (
        "don_hang.ma_don",
        "don_hang.ngay_giao_thuc_te",
        "don_hang.ngay_giao_du_kien",
        "don_hang.trang_thai",
        "don_hang.bang_giao",
    ),
}

COUNT_MODE: dict[str, str] = {
    CATEGORY_TEMPLATE: COUNT_MODE_GROUPS,
    MONTH_TEMPLATE: COUNT_MODE_GROUPS,
    LATE_TEMPLATE: COUNT_MODE_ORDERS,
}

GROUP_COLUMN: dict[str, str] = {
    CATEGORY_TEMPLATE: "nhom",
    MONTH_TEMPLATE: "thang",
}

LoggerLike = JsonLogger | NullLogger
Reference = Callable[[str, Mapping[str, str]], Mapping[str, tuple[float | None, float | None]]]

_LATEST: dict[str, QueryRunResult] = {}
_CSV_DIR: Path | None = None


def _failed(error: PipelineError, code: str) -> PipelineError:
    """Gắn mã lỗi thuộc tập đóng vào ngoại lệ do mô-đun này ném."""

    error.error_code = code  # type: ignore[attr-defined]
    return error


def _definition(entry: KpiLedgerEntry) -> KpiDefinition:
    """Chiếu một dòng sổ KPI sang kiểu payload của C4."""

    return KpiDefinition(
        kpi_id=entry.kpi_id,
        title=entry.title,
        formula=entry.formula,
        revenue_definition=entry.revenue_definition,
        unit=entry.unit,
    )


def _template(template_id: str) -> QueryTemplate:
    """Dựng mẫu của một mã đã biết; ba mẫu là hằng trong mã (ADR-U3-S1)."""

    return QueryTemplate(
        template_id=template_id,
        title=kpi(template_id).title,
        mediated_query_text=MEDIATED_QUERY_TEXT[template_id],
        source_sql=SOURCE_SQL[template_id],
        plan=PLANS[template_id],
        kpi=_definition(kpi(template_id)),
    )


def get_template(template_id: str) -> QueryTemplate:
    """Trả một truy vấn mẫu, hoặc ném SchemaError khi mã lạ (BR3.1)."""

    if template_id not in TEMPLATE_IDS:
        raise SchemaError(f"Truy vấn mẫu không có trong bộ ba đã chốt: {template_id!r}")
    return _template(template_id)


def rewrite_plan(template_id: str) -> list[RewriteStep]:
    """Kế hoạch viết lại từng bước của một mẫu (BR3.3)."""

    return list(get_template(template_id).plan)


def template_tables(template_id: str) -> tuple[str, ...]:
    """Các bảng nguồn mà một mẫu đọc; mọi tên phải thuộc chín bảng nguồn (BR3.5)."""

    get_template(template_id)
    return TEMPLATE_TABLES[template_id]


def _checked_template_tables() -> None:
    """Mẫu chỉ được đọc bảng nguồn có thật; sai là lỗi khởi tạo, không phải lỗi lúc chạy."""

    for template_id in TEMPLATE_IDS:
        unknown = tuple(name for name in TEMPLATE_TABLES[template_id] if name not in SOURCE_TABLES)
        if unknown:
            raise SchemaError(f"Mẫu {template_id!r} đọc bảng ngoài danh sách bảng nguồn: {', '.join(unknown)}.")


_checked_template_tables()


def template_mediated_fields(template_id: str) -> tuple[str, ...]:
    """Các trường trung gian mà một mẫu cần; tập này thuộc `query_fields` của U5."""

    get_template(template_id)
    return TEMPLATE_MEDIATED_FIELDS[template_id]


def reset_latest() -> None:
    """Xoá kết quả gần nhất đã nhớ trong tiến trình."""

    _LATEST.clear()


def latest_sql(template_id: str) -> str | None:
    """SQL của lần chạy gần nhất của một mẫu, hoặc None khi chưa chạy (FR2.4)."""

    get_template(template_id)
    result = _LATEST.get(template_id)
    return None if result is None else result.source_sql


def _default_csv_dir() -> Path:
    """Thư mục CSV nguồn, lấy một lần từ `AppConfig`."""

    global _CSV_DIR
    if _CSV_DIR is None:
        _CSV_DIR = load_config().raw_csv_dir
    return _CSV_DIR


def _checked_date(value: object, key: str) -> str:
    """Chỉ nhận ngày ISO hoặc rỗng; sai kiểu hoặc sai định dạng là lỗi tham số (BR3.12)."""

    if value is None or value == "":
        return ""
    if not isinstance(value, str):
        raise SchemaError(f"Tham số {key!r} phải là chuỗi ngày ISO 'YYYY-MM-DD'.")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise SchemaError(f"Tham số {key!r} không phải ngày ISO hợp lệ: {value!r}") from exc
    return value


def _checked_status(value: object, template_id: str) -> str:
    """Trạng thái mặc định 'delivered' cho mẫu doanh thu và rỗng cho mẫu giao trễ."""

    if value is None:
        return "" if template_id == LATE_TEMPLATE else DELIVERED_STATUS
    if not isinstance(value, str):
        raise SchemaError("Tham số 'trang_thai' phải là chuỗi.")
    if value and value not in STATUS_VALUES:
        raise SchemaError(f"Tham số 'trang_thai' ngoài miền trạng thái: {value!r}")
    return value


def _checked_params(template_id: str, params: object) -> dict[str, str]:
    """Dựng bộ tham số duy nhất dùng cho cả SQL và lời gọi `src/analytics` (BR3.12)."""

    if params is None:
        raw: dict = {}
    elif isinstance(params, Mapping):
        raw = dict(params)
    else:
        raise SchemaError("Tham số của một lần chạy phải là một ánh xạ khoá → giá trị.")
    unknown = sorted(str(key) for key in raw if key not in ALLOWED_PARAMS)
    if unknown:
        raise SchemaError(f"Tham số không nhận biết: {', '.join(unknown)}.")
    ngay_tu = _checked_date(raw.get("ngay_tu"), "ngay_tu")
    ngay_den = _checked_date(raw.get("ngay_den"), "ngay_den")
    if ngay_tu and ngay_den and ngay_den < ngay_tu:
        raise SchemaError(f"Khoảng ngày ngược: ngay_den {ngay_den!r} trước ngay_tu {ngay_tu!r}.")
    return {
        "ngay_tu": ngay_tu,
        "ngay_den": ngay_den,
        "trang_thai": _checked_status(raw.get("trang_thai"), template_id),
    }


def _checked_selection(selection: object, template_id: str) -> str:
    """Kiểm C3 do U6 truyền vào và trả tên nguồn đã chọn (ADR-U3-S4).

    C3 không chỉ để lấy tên: khi nguồn thắng **có khai** danh sách bảng, nó phải khai đủ bảng
    mà mẫu truy vấn cần đọc. Một kết quả chọn nguồn không khai bảng nào (ví dụ bộ dựng thử trong
    test) thì bỏ qua phép kiểm này thay vì báo lỗi sai.
    """

    if selection is None:
        raise SchemaError("Thiếu kết quả chọn nguồn (C3); U3 không tự chọn nguồn.")
    selected = getattr(selection, "selected_sources", None)
    if not selected:
        raise SchemaError(f"Kết quả chọn nguồn của {template_id!r} chưa có nguồn nào được chọn (C3).")
    query_id = getattr(selection, "query_id", None)
    if query_id != template_id:
        raise SchemaError(f"Kết quả chọn nguồn là của truy vấn {query_id!r}, không phải {template_id!r}.")
    needed = set(template_tables(template_id))
    offered = {str(name) for name in getattr(selected[0], "tables", ())}
    missing = sorted(needed - offered)
    if offered and missing:
        raise SchemaError(
            f"Nguồn {getattr(selected[0], 'source_name', '')!r} được chọn cho {template_id!r} "
            f"nhưng không khai bảng {', '.join(missing)} mà truy vấn cần (C3)."
        )
    return str(getattr(selected[0], "source_name", ""))


def _header(path: Path) -> tuple[str, ...]:
    """Chỉ đọc dòng tiêu đề của một tệp CSV nguồn (ADR-U3-S2)."""

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return tuple(next(csv.reader(handle), []))
    except PermissionError as exc:
        raise _failed(
            QueryExecutionError(f"Không đọc được tiêu đề {path.name}: {exc}"), "permission_denied"
        ) from exc
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise _failed(
            QueryExecutionError(f"Không đọc được tiêu đề {path.name}: {exc}"), "decode_error"
        ) from exc


def _read_table(path: Path, table: str, columns: tuple[str, ...]) -> pd.DataFrame:
    """Đọc đúng các cột mẫu cần, ép kiểu ngày để so sánh được (ADR-U3-S5)."""

    parse: list[str] = [name for name in DATE_COLUMNS.get(table, ()) if name in columns]
    try:
        return pd.read_csv(
            path,
            encoding="utf-8-sig",
            usecols=list(columns),
            parse_dates=parse,
        )
    except FileNotFoundError as exc:
        raise _failed(QueryExecutionError(f"Không tìm thấy tệp nguồn: {path.name}"), "file_not_found") from exc
    except PermissionError as exc:
        raise _failed(
            QueryExecutionError(f"Không đọc được tệp nguồn {path.name}: {exc}"), "permission_denied"
        ) from exc
    except UnicodeDecodeError as exc:
        raise _failed(
            QueryExecutionError(f"Tệp nguồn {path.name} không đọc được: {exc}"), "decode_error"
        ) from exc
    except (OSError, ValueError) as exc:
        raise _failed(QueryExecutionError(f"Tệp nguồn {path.name} không đọc được: {exc}"), "unknown") from exc


def _load_frames(template_id: str, directory: Path, logger: LoggerLike) -> dict[str, pd.DataFrame]:
    """Nạp các bảng nguồn mẫu cần, kiểm tiêu đề trước khi trả khung (BR3.5)."""

    frames: dict[str, pd.DataFrame] = {}
    for table in TEMPLATE_TABLES[template_id]:
        path = Path(directory) / f"{table}.csv"
        if not path.exists():
            logger.error(
                "integration.query.failed",
                "file_not_found",
                template_id=template_id,
                file=path.name,
                message="tệp nguồn không có mặt",
            )
            raise _failed(
                QueryExecutionError(f"Không tìm thấy tệp nguồn cho mẫu: {path.name}"), "file_not_found"
            )
        header = _header(path)
        missing = [name for name in TEMPLATE_COLUMNS[template_id][table] if name not in header]
        if missing:
            logger.error(
                "integration.query.failed",
                "column_missing",
                template_id=template_id,
                file=path.name,
                column=missing[0],
                message="cột mẫu cần không có trong tiêu đề",
            )
            raise _failed(
                SchemaError(
                    f"Mẫu {template_id!r} cần cột {missing[0]!r} nhưng không có trong tiêu đề {path.name}."
                ),
                "column_missing",
            )
        try:
            frames[table] = _read_table(path, table, TEMPLATE_COLUMNS[template_id][table])
        except PipelineError as exc:
            logger.error(
                "integration.query.failed",
                normalise_error_code(getattr(exc, "error_code", "")),
                template_id=template_id,
                file=path.name,
                message=str(exc)[:200],
            )
            raise
    return frames


def _sql_params(values: Mapping[str, str]) -> list[str]:
    """Sáu giá trị cho sáu placeholder `?` của mọi mẫu, đúng thứ tự trong SQL (SR-U3-3)."""

    status = values["trang_thai"]
    ngay_tu = values["ngay_tu"]
    ngay_den = values["ngay_den"]
    return [status, status, ngay_tu, ngay_tu, ngay_den, ngay_den]


def _group_label(value: object) -> str:
    """Nhãn nhóm dùng chung cho hai bên; giá trị rỗng thành một nhãn cố định."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return NULL_GROUP_KEY
    text = str(value).strip()
    return text or NULL_GROUP_KEY


def _rows(template_id: str, records: list[tuple]) -> list[dict[str, object]]:
    """Chuyển kết quả DuckDB thành payload C4, làm tròn hai chữ số như `src/analytics`."""

    if COUNT_MODE[template_id] == COUNT_MODE_ORDERS:
        return [
            {
                "nhom": _group_label(row[0]),
                "ty_le": round(float(row[1] or 0.0), 2),
                "so_dong": int(row[2] or 0),
                "so_tre": int(row[3] or 0),
            }
            for row in records
        ]
    column = GROUP_COLUMN[template_id]
    return [
        {
            column: _group_label(row[0]),
            "gia_tri": round(float(row[1] or 0.0), 2),
            "so_dong": int(row[2] or 0),
        }
        for row in records
    ]


def _actual_groups(template_id: str, rows: list[dict[str, object]]) -> dict[str, tuple[float, float | None]]:
    """Gom kết quả của mẫu thành (giá trị, số đếm) theo nhóm, kèm dòng `__all__`."""

    groups: dict[str, tuple[float, float | None]] = {}
    if COUNT_MODE[template_id] == COUNT_MODE_ORDERS:
        delivered = sum(int(row["so_dong"]) for row in rows)  # type: ignore[arg-type]
        late = sum(int(row["so_tre"]) for row in rows)  # type: ignore[arg-type]
        for row in rows:
            groups[str(row["nhom"])] = (float(row["ty_le"]), float(row["so_dong"]))  # type: ignore[arg-type]
        rate = round(100.0 * late / delivered, 2) if delivered else 0.0
        groups[ALL_GROUPS] = (rate, float(delivered))
        return groups
    column = GROUP_COLUMN[template_id]
    total = 0.0
    for row in rows:
        value = float(row["gia_tri"])  # type: ignore[arg-type]
        total += value
        groups[str(row[column])] = (value, None)
    groups[ALL_GROUPS] = (round(total, 2), float(len(rows)))
    return groups


def _tolerance(unit: str) -> float:
    """Dung sai là hằng trong mã, không phải tham số (ADR-U3-S3)."""

    if unit == MONEY_UNIT:
        return TOLERANCE_MONEY
    if unit == PERCENT_UNIT:
        return TOLERANCE_PERCENT
    return TOLERANCE_COUNT


def _comparison(
    kpi_id: str,
    group_key: str,
    expected: float,
    actual: float,
    tolerance: float,
) -> KpiComparison:
    """Một dòng đối chiếu; `matches` đúng khi và chỉ khi |delta| <= tolerance."""

    delta = round(expected - actual, 2)
    return KpiComparison(
        kpi_id=kpi_id,
        group_key=group_key,
        expected_value=expected,
        actual_value=actual,
        delta=delta,
        tolerance=tolerance,
        matches=abs(delta) <= tolerance,
    )


def _compare(
    template_id: str,
    rows: list[dict[str, object]],
    expected: Mapping[str, tuple[float | None, float | None]],
) -> tuple[list[KpiComparison], list[str], tuple[tuple[str, str, float], ...]]:
    """So từng nhóm và dòng `__all__`; trả (đối chiếu, partial, nhóm lệch) (BR3.6)."""

    actual = _actual_groups(template_id, rows)
    unit = kpi(template_id).unit
    tolerance = _tolerance(unit)
    mode = COUNT_MODE[template_id]
    keys = list(actual) + [key for key in expected if key not in actual]
    comparisons: list[KpiComparison] = []
    partial: list[str] = []
    failures: list[tuple[str, str, float]] = []
    for key in keys:
        expected_value, expected_count = expected.get(key, (None, None))
        if key in expected and expected_value is None:
            partial.append(f"nhóm {key}: nguồn tham chiếu không trả giá trị")
            continue
        actual_value, actual_count = actual.get(key, (None, None))
        comparison = _comparison(
            template_id,
            key,
            round(float(expected_value), 2) if expected_value is not None else 0.0,
            round(float(actual_value), 2) if actual_value is not None else 0.0,
            tolerance,
        )
        comparisons.append(comparison)
        if not comparison.matches:
            failures.append((comparison.kpi_id, key, comparison.delta))
        count_pair = _count_pair(mode, key, expected, expected_count, actual_count)
        if count_pair is None:
            continue
        count_comparison = _comparison(COUNT_KPI_ID, key, count_pair[0], count_pair[1], TOLERANCE_COUNT)
        comparisons.append(count_comparison)
        if not count_comparison.matches:
            failures.append((count_comparison.kpi_id, key, count_comparison.delta))
    return comparisons, partial, tuple(failures)


def _count_pair(
    mode: str,
    key: str,
    expected: Mapping[str, tuple[float | None, float | None]],
    expected_count: float | None,
    actual_count: float | None,
) -> tuple[float, float] | None:
    """Cặp số đếm của một nhóm, hoặc None khi mẫu chỉ so số đếm ở dòng `__all__`."""

    if mode == COUNT_MODE_ORDERS:
        return float(expected_count or 0.0), float(actual_count or 0.0)
    if key != ALL_GROUPS:
        return None
    reference_groups = len([group for group in expected if group != ALL_GROUPS])
    expected_total = float(expected_count) if expected_count is not None else float(reference_groups)
    return expected_total, float(actual_count or 0.0)


def _analytics_label(value: object) -> str:
    """Nhãn nhóm của `src/analytics`, cùng quy ước với phía SQL."""

    return _group_label(value)


def analytics_reference(
    template_id: str, params: Mapping[str, str]
) -> dict[str, tuple[float | None, float | None]]:
    """Giá trị tham chiếu của `src/analytics` cho cùng KPI và cùng bộ tham số (BR3.6)."""

    from src.analytics.service import AnalyticsService
    from src.common.types import KpiFilters

    filters = KpiFilters(
        start_date=params["ngay_tu"] or None,
        end_date=params["ngay_den"] or None,
        order_status=params["trang_thai"],
    )
    service = AnalyticsService(load_config())
    groups: dict[str, tuple[float | None, float | None]] = {}
    if template_id == CATEGORY_TEMPLATE:
        frame = service.revenue_by_dimension(filters, "category")
        for record in frame.itertuples(index=False):
            groups[_analytics_label(record.dimension)] = (round(float(record.revenue), 2), None)
        groups[ALL_GROUPS] = (round(float(frame["revenue"].sum()), 2), float(len(frame)))
        return groups
    if template_id == MONTH_TEMPLATE:
        frame = service.revenue_by_period(filters, "month")
        for record in frame.itertuples(index=False):
            month = f"{int(record.year):04d}-{int(record.month):02d}"
            groups[month] = (round(float(record.revenue), 2), None)
        groups[ALL_GROUPS] = (round(float(frame["revenue"].sum()), 2), float(len(frame)))
        return groups
    frame = service.delivery_kpis(filters, "state")
    for record in frame.itertuples(index=False):
        groups[_analytics_label(record.dimension)] = (
            round(float(record.late_rate_pct), 2),
            float(record.delivered_orders),
        )
    delivered = float(frame["delivered_orders"].sum())
    late = float(frame["late_orders"].sum())
    groups[ALL_GROUPS] = (round(100.0 * late / delivered, 2) if delivered else 0.0, delivered)
    return groups


def run_template(
    template_id: str,
    params: Mapping[str, object] | None = None,
    selection: object = None,
    logger: LoggerLike | None = None,
    *,
    reference: Reference | None = None,
    csv_dir: Path | None = None,
) -> QueryRunResult:
    """Chạy một truy vấn mẫu, đối chiếu KPI và trả payload C4 (W1)."""

    template = get_template(template_id)
    logger = logger or NullLogger()
    values = _checked_params(template_id, params)
    source_name = _checked_selection(selection, template_id)
    directory = Path(csv_dir) if csv_dir is not None else _default_csv_dir()
    sql = SOURCE_SQL[template_id]
    plan_id = f"plan-{uuid.uuid4().hex[:12]}"

    load_started = time.perf_counter()
    frames = _load_frames(template_id, directory, logger)
    load_ms = int((time.perf_counter() - load_started) * 1000)

    logger.info(
        "integration.query.started",
        plan_id=plan_id,
        template_id=template_id,
        source_name=source_name,
        load_ms=load_ms,
    )
    started = time.perf_counter()
    try:
        connection = duckdb.connect()
        try:
            for table, frame in frames.items():
                connection.register(table, frame)
            records = connection.execute(sql, _sql_params(values)).fetchall()
            total_orders = _total_orders(connection, template_id, values)
        finally:
            connection.close()
    except duckdb.Error as exc:
        logger.error(
            "integration.query.failed",
            "sql_error",
            plan_id=plan_id,
            template_id=template_id,
            message=str(exc)[:200],
        )
        raise _failed(
            QueryExecutionError(f"Truy vấn nguồn của mẫu {template_id!r} lỗi: {exc}"), "sql_error"
        ) from exc
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    rows = _rows(template_id, records)
    provided = reference if reference is not None else analytics_reference
    try:
        expected = provided(template_id, dict(values))
    except Exception as exc:  # noqa: BLE001 - lỗi nguồn tham chiếu phải lan nguyên vẹn (ADR-U3-S4)
        logger.error(
            "integration.query.failed",
            normalise_error_code(getattr(exc, "error_code", "")),
            plan_id=plan_id,
            template_id=template_id,
            message=str(exc)[:200],
        )
        raise
    comparisons, partial, failures = _compare(template_id, rows, expected)
    if failures:
        logger.error(
            "integration.query.failed",
            "result_unreadable",
            plan_id=plan_id,
            template_id=template_id,
            mismatch_count=len(failures),
            message="KPI lệch so với nguồn tham chiếu",
        )
        listed = ", ".join(f"{kpi_id}/{group} lệch {delta:+.2f}" for kpi_id, group, delta in failures)
        raise KpiMismatchError(
            f"Truy vấn {template_id!r} lệch KPI so với nguồn tham chiếu: {listed}.",
            failures,
        )

    result = QueryRunResult(
        plan_id=plan_id,
        template_id=template_id,
        template_title=template.title,
        mediated_query_text=template.mediated_query_text,
        rewrite_plan=list(template.plan),
        source_sql=sql,
        rows=rows,
        row_count=len(rows),
        elapsed_ms=elapsed_ms,
        total_orders=total_orders,
        months=_months(template_id, rows),
        partial=partial,
        kpi_definitions=[_definition(kpi(template_id)), _definition(kpi(COUNT_KPI_ID))],
        kpi_comparison=comparisons,
    )
    _LATEST[template_id] = result
    logger.info(
        "integration.query.completed",
        plan_id=plan_id,
        template_id=template_id,
        row_count=result.row_count,
        elapsed_ms=elapsed_ms,
        load_ms=load_ms,
    )
    if elapsed_ms > SLOW_QUERY_MS:
        logger.warning("integration.query.slow", plan_id=plan_id, elapsed_ms=elapsed_ms)
    return result


def _total_orders(connection, template_id: str, values: Mapping[str, str]) -> int | None:
    """Số đơn delivered phân biệt của hai mẫu doanh thu; None ở mẫu giao trễ (BR3.10)."""

    if template_id == LATE_TEMPLATE:
        return None
    row = connection.execute(TOTAL_ORDERS_SQL, _sql_params(values)).fetchone()
    return int(row[0] or 0) if row else 0


def _months(template_id: str, rows: list[dict[str, object]]) -> list[str] | None:
    """Các tháng 'YYYY-MM' của mẫu doanh thu theo tháng, tăng dần (BR3.10)."""

    if template_id != MONTH_TEMPLATE:
        return None
    return sorted({str(row["thang"]) for row in rows})
