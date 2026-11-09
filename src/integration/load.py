"""Load the mediated `don_hang` entity from the source CSV files."""

from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from pathlib import Path

import pandas as pd

from src.common.exceptions import SchemaError
from src.common.logging import NullLogger, UNKNOWN_ERROR_CODE, normalise_error_code
from src.integration.models import DonHang, InvalidRecord, LoadResult
from src.integration.schema import (
    EntityMapping,
    checked_identifier,
    load_schema,
)

ENTITY_NAME = "don_hang"
KEY_FIELD = "ma_don"
RETRY_DELAY_SECONDS = 0.1
MAX_ATTEMPTS = 2

_CACHE: dict[tuple, LoadResult] = {}


def clear_cache() -> None:
    """Drop the process-level load cache."""

    _CACHE.clear()


def _read_csv(path: Path, **kwargs: object) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", **kwargs)


def _source_path(config, table: str) -> Path:
    return Path(config.raw_csv_dir) / f"{table}.csv"


def _error_code(exc: BaseException) -> str:
    """Map a read failure onto the closed `error_code` set (security-design §4)."""

    if isinstance(exc, FileNotFoundError):
        return "file_not_found"
    if isinstance(exc, PermissionError):
        return "permission_denied"
    if isinstance(exc, UnicodeDecodeError):
        return "decode_error"
    # Lỗi đọc khác (đĩa hỏng, đường dẫn quá dài…) không thuộc tập đóng.
    return UNKNOWN_ERROR_CODE


def _read_with_retry(path: Path, entity: str, logger, **kwargs: object) -> pd.DataFrame:
    """Read one CSV, retrying a transient read failure exactly once."""

    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger.info(
            "integration.load.started",
            file=path.name,
            entity=entity,
            attempt=attempt,
        )
        try:
            return _read_csv(path, **kwargs)
        except (OSError, UnicodeDecodeError) as exc:
            code = _error_code(exc)
            if attempt == MAX_ATTEMPTS:
                logger.error(
                    "integration.load.failed",
                    normalise_error_code(code),
                    file=path.name,
                    field="",
                    column="",
                )
                raise SchemaError(f"không đọc được {path.name}: {exc}") from exc
            logger.warning(
                "integration.load.retried",
                file=path.name,
                attempt=attempt,
                error_code=code,
            )
            time.sleep(RETRY_DELAY_SECONDS)
    raise SchemaError(f"không đọc được {path.name}")


def _headers(path: Path, entity: str, logger) -> tuple[str, ...]:
    frame = _read_with_retry(path, entity, logger, nrows=0)
    return tuple(str(column) for column in frame.columns)


def _verify_columns(config, entity: EntityMapping, headers: dict[str, tuple[str, ...]], logger) -> None:
    """BR1.3: every declared mapping must point at a column that exists."""

    for field in entity.fields:
        available = headers[field.source_table]
        try:
            checked_identifier(field.source_column, frozenset(available), "cột nguồn")
        except SchemaError:
            logger.error(
                "integration.load.failed",
                "column_missing",
                file=_source_path(config, field.source_table).name,
                field=field.field_name,
                column=field.source_column,
            )
            raise SchemaError(
                f"Trường {field.field_name!r} ánh xạ tới cột "
                f"{field.source_column!r} không có trong {field.source_table}.csv."
            ) from None


def _loaded_by_table(entity: EntityMapping) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for field in entity.fields:
        if field.loaded:
            grouped.setdefault(field.source_table, []).append(field.source_column)
    return grouped


def _mediated_rows(frame: pd.DataFrame, entity: EntityMapping, table: str) -> list[dict[str, object]]:
    fields = [item for item in entity.fields if item.loaded and item.source_table == table]
    rows: list[dict[str, object]] = []
    for record in frame.to_dict("records"):
        rows.append({item.field_name: record.get(item.source_column) for item in fields})
    return rows


def clean_rows(
    rows: Iterable[Mapping[str, object]] | pd.DataFrame,
) -> tuple[list[DonHang], int, dict[str, int]]:
    """BR1.1 + BR1.2: keep valid orders, count every dropped record by reason."""

    records = rows.to_dict("records") if isinstance(rows, pd.DataFrame) else rows
    orders: list[DonHang] = []
    reasons: dict[str, int] = {}
    dropped = 0
    seen: set[str] = set()
    for row in records:
        ma_don = str(row.get("ma_don") or "").strip()
        if ma_don and ma_don in seen:
            dropped += 1
            reasons["trung_ma_don"] = reasons.get("trung_ma_don", 0) + 1
            continue
        try:
            order = DonHang.from_row(row)
        except InvalidRecord as exc:
            dropped += 1
            reasons[exc.reason] = reasons.get(exc.reason, 0) + 1
            continue
        seen.add(order.ma_don)
        orders.append(order)
    return orders, dropped, reasons


def _cache_key(config, entity: EntityMapping, schema_path: Path) -> tuple | None:
    stamps: list[tuple[str, int]] = []
    for table in entity.source_tables:
        path = _source_path(config, table)
        try:
            stamps.append((str(path), path.stat().st_mtime_ns))
        except OSError:
            return None
    try:
        stamps.append((str(schema_path), schema_path.stat().st_mtime_ns))
    except OSError:
        return None
    return tuple(stamps)


def _key_table(entity: EntityMapping, grouped: dict[str, list[str]]) -> tuple[str, list[str]]:
    """Bảng khoá của thực thể; trường nạp từ bảng khác không thuộc lát cắt này."""

    key_table = entity.field(KEY_FIELD).source_table
    columns = grouped.get(key_table)
    if not columns:
        raise SchemaError(f"Bảng khoá {key_table!r} của thực thể {entity.name!r} không có trường nạp nào.")
    return key_table, columns


def load_don_hang(config, logger=None) -> LoadResult:
    """Load the mediated `don_hang` entity, reusing the process-level cache."""

    logger = logger or NullLogger()
    schema_path = Path(config.mediated_schema_path)
    entity = load_schema(schema_path).entity(ENTITY_NAME)

    key = _cache_key(config, entity, schema_path)
    if key is not None:
        cached = _CACHE.get(key)
        if cached is not None:
            return cached

    started = time.perf_counter()
    headers = {
        table: _headers(_source_path(config, table), ENTITY_NAME, logger) for table in entity.source_tables
    }
    _verify_columns(config, entity, headers, logger)

    grouped = _loaded_by_table(entity)
    table, columns = _key_table(entity, grouped)
    skipped = sorted(name for name in grouped if name != table)
    if skipped:
        logger.info(
            "integration.load.skipped",
            entity=ENTITY_NAME,
            tables=skipped,
            reason="lát cắt chỉ nạp bảng khoá của thực thể",
        )
    frame = _read_with_retry(
        _source_path(config, table),
        ENTITY_NAME,
        logger,
        usecols=list(columns),
        dtype=str,
    )
    orders, dropped, reasons = clean_rows(_mediated_rows(frame, entity, table))
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    result = LoadResult(
        orders=orders,
        rows_in=len(frame),
        rows_dropped=dropped,
        drop_reasons=reasons,
        elapsed_ms=elapsed_ms,
    )
    logger.info(
        "integration.load.completed",
        entity=ENTITY_NAME,
        rows_in=result.rows_in,
        rows_loaded=len(orders),
        rows_dropped=dropped,
        drop_reasons=reasons,
        elapsed_ms=elapsed_ms,
    )
    if key is not None:
        _CACHE.clear()
        _CACHE[key] = result
    return result
