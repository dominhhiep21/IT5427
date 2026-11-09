"""Bộ nạp và bộ kiểm cho tệp khai báo lược đồ trung gian."""

from __future__ import annotations

import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.common.exceptions import ConfigurationError, PipelineError, SchemaError
from src.common.logging import JsonLogger, NullLogger, normalise_error_code
from src.config import load_config
from src.ingest.schemas import TABLE_SPECS
from src.integration.models import MediatedFieldCatalogue, MediatedSchemaView, PartialInfo

IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
DATA_TYPES = frozenset({"string", "integer", "decimal", "timestamp"})
SCHEMA_KIND = "GAV"
SOURCE_TABLES = frozenset(spec.file_name.removesuffix(".csv") for spec in TABLE_SPECS.values())
REQUIRED_ENTITIES = ("don_hang", "mat_hang", "san_pham")
ENTITY_KEYS = frozenset({"name", "description", "source_tables", "fields"})
FIELD_KEYS = frozenset({"field_name", "source_table", "source_column", "data_type", "loaded"})

LoggerLike = JsonLogger | NullLogger

_CSV_DIR: Path | None = None


@dataclass(frozen=True)
class FieldMapping:
    """Một trường trung gian và cột nguồn mà nó lấy giá trị."""

    field_name: str
    source_table: str
    source_column: str
    data_type: str
    loaded: bool


@dataclass(frozen=True)
class EntityMapping:
    """Một thực thể trung gian cùng mọi ánh xạ trường đã khai cho nó."""

    name: str
    description: str
    source_tables: tuple[str, ...]
    fields: tuple[FieldMapping, ...]

    def field(self, field_name: str) -> FieldMapping:
        """Trả ánh xạ của một trường, hoặc ném SchemaError."""

        for item in self.fields:
            if item.field_name == field_name:
                return item
        raise SchemaError(f"Trường không có trong lược đồ: {field_name!r}")

    @property
    def loaded_fields(self) -> tuple[str, ...]:
        """Tên các trường mà lát cắt này thực sự nạp."""

        return tuple(item.field_name for item in self.fields if item.loaded)


@dataclass(frozen=True)
class MediatedSchema:
    """Toàn bộ tệp khai báo lược đồ trung gian."""

    schema_kind: str
    entities: tuple[EntityMapping, ...]

    def entity(self, name: str) -> EntityMapping:
        """Trả một thực thể, hoặc ném SchemaError."""

        for item in self.entities:
            if item.name == name:
                return item
        raise SchemaError(f"Thực thể không có trong lược đồ: {name!r}")


def _failed(error: PipelineError, code: str) -> PipelineError:
    """Gắn mã lỗi đóng vào ngoại lệ do mô-đun này ném."""

    error.error_code = code  # type: ignore[attr-defined]
    return error


def checked_identifier(name: str, allowed: frozenset[str], kind: str) -> str:
    """Chỉ trả một định danh khi cả hình dạng và thành viên đều hợp lệ."""

    if not isinstance(name, str) or not IDENTIFIER.fullmatch(name) or name not in allowed:
        raise _failed(SchemaError(f"{kind} không hợp lệ: {name!r}"), "identifier_invalid")
    return name


def _checked_name(name: object, kind: str) -> str:
    """Kiểm hình dạng của một tên; thành viên do nơi gọi kiểm riêng."""

    if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
        raise _failed(SchemaError(f"{kind} không hợp lệ: {name!r}"), "identifier_invalid")
    return name


def loaded_columns(entity: EntityMapping) -> tuple[str, ...]:
    """Cột nguồn cần đọc cho một thực thể: chỉ các trường được đánh dấu nạp."""

    return tuple(item.source_column for item in entity.fields if item.loaded)


def _source_path(csv_dir: Path, source_table: str) -> Path:
    """Đường dẫn một tệp CSV nguồn, dựng từ tên bảng đã kiểm."""

    return Path(csv_dir) / f"{source_table}.csv"


def _default_csv_dir() -> Path:
    """Thư mục chứa CSV nguồn, lấy một lần từ `AppConfig`."""

    global _CSV_DIR
    if _CSV_DIR is None:
        _CSV_DIR = load_config().raw_csv_dir
    return _CSV_DIR


def _source_header(csv_dir: Path, source_table: str) -> tuple[str, ...]:
    """Chỉ đọc dòng tiêu đề của một tệp CSV nguồn, không đọc dữ liệu (ADR-U2-S3)."""

    path = _source_path(csv_dir, source_table)
    if not path.exists():
        raise _failed(
            ConfigurationError(f"Không tìm thấy tệp nguồn của lược đồ: {path}"),
            "file_not_found",
        )
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return tuple(next(csv.reader(handle), []))
    except PermissionError as exc:
        raise _failed(
            SchemaError(f"Không đọc được tiêu đề tệp nguồn {path.name}: {exc}"),
            "permission_denied",
        ) from exc
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise _failed(
            SchemaError(f"Không đọc được tiêu đề tệp nguồn {path.name}: {exc}"),
            "decode_error",
        ) from exc


def _read_headers(schema: MediatedSchema, csv_dir: Path) -> dict[str, tuple[str, ...]]:
    """Đọc mỗi tiêu đề nguồn đúng một lần cho cả lượt nạp."""

    headers: dict[str, tuple[str, ...]] = {}
    for entity in schema.entities:
        for table in entity.source_tables:
            if table not in headers:
                headers[table] = _source_header(csv_dir, table)
    return headers


def _check_columns(entity: EntityMapping, headers: dict[str, tuple[str, ...]]) -> None:
    """Kiểm mọi cột nguồn đã khai có thật trong tiêu đề của chính bảng đó (BR2.2)."""

    for item in entity.fields:
        if item.source_column not in headers[item.source_table]:
            raise _failed(
                SchemaError(
                    f"Cột nguồn {item.source_column!r} của trường {item.field_name!r} "
                    f"không có trong tiêu đề {item.source_table}.csv."
                ),
                "column_missing",
            )


def _partial_info(schema: MediatedSchema) -> PartialInfo | None:
    """Nêu các thực thể bắt buộc mà tệp khai báo bỏ sót, hoặc None khi đủ ba (BR2.1)."""

    declared = {entity.name for entity in schema.entities}
    missing = tuple(name for name in REQUIRED_ENTITIES if name not in declared)
    if not missing:
        return None
    return PartialInfo(
        missing=missing,
        reason="Thực thể chưa được khai trong tệp lược đồ: " + ", ".join(missing) + ".",
    )


def _unique_entity_names(entities: tuple[EntityMapping, ...], file_name: str) -> None:
    """Từ chối tệp khai báo lặp tên thực thể (entities.md — unique)."""

    seen: set[str] = set()
    for entity in entities:
        if entity.name in seen:
            raise SchemaError(f"Tệp lược đồ {file_name} khai trùng tên thực thể {entity.name!r}.")
        seen.add(entity.name)


def _unique_field_names(entity_name: str, fields: tuple[FieldMapping, ...]) -> None:
    """Từ chối hai trường trong một thực thể trùng tên (BR2.6)."""

    seen: set[str] = set()
    for item in fields:
        if item.field_name in seen:
            raise SchemaError(f"Thực thể {entity_name!r} khai trùng tên trường {item.field_name!r}.")
        seen.add(item.field_name)


def _mapping_list(raw: dict, key: str, context: str) -> list:
    value = raw.get(key)
    if not isinstance(value, list) or not value:
        raise SchemaError(f"{context} thiếu danh sách {key!r}.")
    return value


def _reject_unknown_keys(raw: dict, allowed: frozenset[str], context: str) -> None:
    """Từ chối khoá không nhận biết, để lỗi gõ không âm thầm thành giá trị mặc định (BR2.8)."""

    unknown = sorted(str(key) for key in raw if key not in allowed)
    if unknown:
        raise SchemaError(f"{context} có khoá không nhận biết: {', '.join(unknown)}.")


def _unique_source_tables(name: str, source_tables: tuple[str, ...]) -> None:
    """Từ chối một thực thể khai hai lần cùng bảng nguồn (entities.md)."""

    duplicates = sorted({table for table in source_tables if source_tables.count(table) > 1})
    if duplicates:
        raise SchemaError(f"Thực thể {name!r} khai trùng bảng nguồn: {', '.join(duplicates)}.")


def _parse_data_type(field_name: str, raw: dict) -> str:
    """Chỉ nhận kiểu thuộc tập đóng, không tự hạ kiểu (BR2.5)."""

    data_type = raw.get("data_type")
    if data_type not in DATA_TYPES:
        raise SchemaError(f"Kiểu dữ liệu của trường {field_name!r} không hợp lệ: {data_type!r}")
    return data_type


def _parse_loaded(field_name: str, raw: dict) -> bool:
    """Đọc cờ `loaded` tuỳ chọn, mặc định true khi vắng mặt (TS-U2-7)."""

    loaded = raw.get("loaded", True)
    if not isinstance(loaded, bool):
        raise SchemaError(f"Cờ loaded của trường {field_name!r} phải là true/false.")
    return loaded


def _parse_field(raw: object, source_tables: tuple[str, ...]) -> FieldMapping:
    if not isinstance(raw, dict):
        raise SchemaError("Mỗi trường của lược đồ phải là một ánh xạ.")
    field_name = _checked_name(raw.get("field_name"), "tên trường")
    _reject_unknown_keys(raw, FIELD_KEYS, f"Trường {field_name!r}")
    source_table = checked_identifier(raw.get("source_table"), SOURCE_TABLES, "bảng nguồn")
    if source_table not in source_tables:
        raise SchemaError(
            f"Bảng nguồn {source_table!r} của trường {field_name!r} không nằm trong source_tables của thực thể."
        )
    return FieldMapping(
        field_name=field_name,
        source_table=source_table,
        source_column=_checked_name(raw.get("source_column"), "cột nguồn"),
        data_type=_parse_data_type(field_name, raw),
        loaded=_parse_loaded(field_name, raw),
    )


def _parse_entity(raw: object) -> EntityMapping:
    if not isinstance(raw, dict):
        raise SchemaError("Mỗi thực thể của lược đồ phải là một ánh xạ.")
    name = _checked_name(raw.get("name"), "tên thực thể")
    _reject_unknown_keys(raw, ENTITY_KEYS, f"Thực thể {name!r}")
    tables = _mapping_list(raw, "source_tables", f"Thực thể {name!r}")
    source_tables = tuple(checked_identifier(item, SOURCE_TABLES, "bảng nguồn") for item in tables)
    _unique_source_tables(name, source_tables)
    fields = tuple(
        _parse_field(item, source_tables) for item in _mapping_list(raw, "fields", f"Thực thể {name!r}")
    )
    _unique_field_names(name, fields)
    return EntityMapping(
        name=name,
        description=str(raw.get("description", "")),
        source_tables=source_tables,
        fields=fields,
    )


def _parse_schema(path: Path) -> MediatedSchema:
    """L1 và L2: phân tích tệp khai báo rồi kiểm cấu trúc và định danh."""

    path = Path(path)
    if not path.exists():
        raise _failed(ConfigurationError(f"Không tìm thấy tệp lược đồ: {path}"), "file_not_found")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise _failed(
            SchemaError(f"Không đọc được tệp lược đồ {path.name}: {exc}"),
            "decode_error",
        ) from exc
    if not isinstance(raw, dict):
        raise SchemaError(f"Tệp lược đồ {path.name} phải là một ánh xạ YAML.")
    if raw.get("schema_kind") != SCHEMA_KIND:
        raise SchemaError(
            f"schema_kind của {path.name} phải là {SCHEMA_KIND!r}, nhận {raw.get('schema_kind')!r}."
        )
    entities = tuple(_parse_entity(item) for item in _mapping_list(raw, "entities", path.name))
    _unique_entity_names(entities, path.name)
    return MediatedSchema(schema_kind=SCHEMA_KIND, entities=entities)


def load_schema(
    path: Path,
    csv_dir: Path | None = None,
    logger: LoggerLike | None = None,
) -> MediatedSchemaView:
    """Nạp, kiểm rồi chiếu lược đồ trung gian thành view C1."""

    started = time.perf_counter()
    logger = logger if logger is not None else NullLogger()
    try:
        schema = _parse_schema(Path(path))
        directory = Path(csv_dir) if csv_dir is not None else _default_csv_dir()
        headers = _read_headers(schema, directory)
        for entity in schema.entities:
            _check_columns(entity, headers)
    except (SchemaError, ConfigurationError) as exc:
        logger.error(
            "integration.schema.failed",
            normalise_error_code(getattr(exc, "error_code", "")),
            message=str(exc)[:200],
        )
        raise
    partial = _partial_info(schema)
    elapsed_ms = max(1, round((time.perf_counter() - started) * 1000))
    view = MediatedSchemaView(
        schema_kind=schema.schema_kind,
        entities=schema.entities,
        mappings={entity.name: entity.fields for entity in schema.entities},
        elapsed_ms=elapsed_ms,
        partial=partial,
    )
    if partial is not None:
        logger.warning(
            "integration.schema.partial",
            missing_entities=list(partial.missing),
            reason=partial.reason,
        )
    logger.info(
        "integration.schema.loaded",
        entity_count=len(view.entities),
        field_count=sum(len(entity.fields) for entity in view.entities),
        partial_entities=list(partial.missing) if partial is not None else [],
        elapsed_ms=elapsed_ms,
    )
    return view


def build_field_catalogue(view: MediatedSchemaView) -> MediatedFieldCatalogue:
    """Dựng danh mục trường C2 từ một view đã kiểm (BR2.7)."""

    return MediatedFieldCatalogue(
        fields_by_entity={
            entity.name: tuple(f"{entity.name}.{item.field_name}" for item in entity.fields)
            for entity in view.entities
        }
    )
