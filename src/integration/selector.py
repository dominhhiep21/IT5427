"""Bộ nạp hồ sơ nguồn và bộ chọn nguồn cho một truy vấn (U5 — C3/C7)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import yaml

from src.common.exceptions import (
    ConfigurationError,
    NoSourceAvailableError,
    PipelineError,
    SchemaError,
)
from src.common.logging import JsonLogger, NullLogger, normalise_error_code
from src.integration.models import (
    MediatedFieldCatalogue,
    SourceCatalogue,
    SourceChoice,
    SourceProfile,
    SourceSelection,
)
from src.integration.schema import SOURCE_TABLES

CONFIG_LABEL = "config/integration-sources.yaml"
SOURCE_NAMES = ("olist_csv", "ibge_cache", "partner_simulated")
QUERY_IDS = ("doanh_thu_theo_danh_muc", "doanh_thu_theo_thang", "ty_le_giao_tre_theo_bang")
PARTIAL_REASON = "chưa có kết quả đề xuất cho truy vấn đang chọn"
PROFILE_KEYS = (
    "source_name",
    "label",
    "tables",
    "covered_fields",
    "has_data",
    "cost_level",
    "latency_ms",
    "is_simulated",
)
ENTITY_LABELS = (("don_hang", "đơn hàng"), ("mat_hang", "mặt hàng"), ("san_pham", "sản phẩm"))
NUMBER_WORDS = {2: "hai", 3: "ba", 4: "bốn", 5: "năm"}
SIMULATED_REASON = "nguồn mô phỏng, chỉ dùng để so sánh"
NO_DATA_REASON = "không có dữ liệu"
NAME_TIE_REASON = "cùng chi phí và độ trễ, xếp sau theo tên"

LoggerLike = JsonLogger | NullLogger


def _failed(error: PipelineError, code: str) -> PipelineError:
    """Gắn mã lỗi đóng vào ngoại lệ do mô-đun này ném."""

    error.error_code = code  # type: ignore[attr-defined]
    return error


def _checked_text(value: object, source: str, key: str) -> str:
    """Chỉ nhận một chuỗi khác rỗng (ADR-U5-S7)."""

    if not isinstance(value, str) or not value.strip():
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn {source!r} có {key!r} phải là chuỗi khác rỗng."),
            "unknown",
        )
    return value


def _checked_flag(value: object, source: str, key: str) -> bool:
    """Chỉ nhận `true`/`false` thật, không nhận chuỗi truthy hay 0/1 (ADR-U5-S7)."""

    if not isinstance(value, bool):
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn {source!r} có {key!r} phải là true/false."),
            "unknown",
        )
    return value


def _checked_int(value: object, source: str, key: str, low: int, high: int | None = None) -> int:
    """Chỉ nhận số nguyên trong miền, và không nhận `bool` (lớp con của `int`)."""

    if not isinstance(value, int) or isinstance(value, bool):
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn {source!r} có {key!r} phải là số nguyên."),
            "unknown",
        )
    if value < low or (high is not None and value > high):
        bound = f"{low}..{high}" if high is not None else f">= {low}"
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn {source!r} có {key!r} ngoài miền {bound}: {value}."),
            "unknown",
        )
    return value


def _checked_text_list(value: object, source: str, key: str) -> tuple[str, ...]:
    """Chỉ nhận danh sách chuỗi khác rỗng, giữ nguyên thứ tự khai báo."""

    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn {source!r} có {key!r} phải là danh sách chuỗi."),
            "unknown",
        )
    return tuple(value)


def _coverage(covered_fields: tuple[str, ...]) -> str:
    """Dựng câu tiếng Việt mô tả khả năng đáp ứng từ tập mã trường (BR5.3)."""

    if not covered_fields:
        return "Không phủ trường nào của lược đồ trung gian"
    entities = tuple(
        label for name, label in ENTITY_LABELS if any(code.startswith(f"{name}.") for code in covered_fields)
    )
    if len(entities) == 1:
        return f"Chỉ có trường {entities[0]}"
    return f"Đủ {NUMBER_WORDS[len(entities)]} bảng: {', '.join(entities)}"


def _checked_profile(raw: object, index: int) -> SourceProfile:
    """Kiểm kiểu và cấu trúc của một hồ sơ nguồn trước khi dựng nó."""

    if not isinstance(raw, dict):
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn thứ {index} của {CONFIG_LABEL} phải là một ánh xạ."),
            "unknown",
        )
    name = raw.get("source_name")
    if not isinstance(name, str) or not name:
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn thứ {index} của {CONFIG_LABEL} thiếu 'source_name'."),
            "unknown",
        )
    missing_keys = [key for key in PROFILE_KEYS if key not in raw]
    if missing_keys:
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn {name!r} thiếu khoá bắt buộc: {', '.join(missing_keys)}."),
            "unknown",
        )
    tables = _checked_text_list(raw["tables"], name, "tables")
    covered_fields = _checked_text_list(raw["covered_fields"], name, "covered_fields")
    if not tables and covered_fields:
        raise _failed(
            ConfigurationError(f"Hồ sơ nguồn {name!r} có 'tables' rỗng nhưng 'covered_fields' khác rỗng."),
            "unknown",
        )
    return SourceProfile(
        source_name=name,
        label=_checked_text(raw["label"], name, "label"),
        tables=tables,
        covered_fields=covered_fields,
        coverage=_coverage(covered_fields),
        has_data=_checked_flag(raw["has_data"], name, "has_data"),
        cost_level=_checked_int(raw["cost_level"], name, "cost_level", 1, 5),
        latency_ms=_checked_int(raw["latency_ms"], name, "latency_ms", 0),
        is_simulated=_checked_flag(raw["is_simulated"], name, "is_simulated"),
    )


def _checked_source_set(profiles: tuple[SourceProfile, ...]) -> None:
    """Kiểm tập tên nguồn đóng, tính duy nhất và đúng một nguồn mô phỏng (BR5.2)."""

    seen: set[str] = set()
    for profile in profiles:
        if profile.source_name not in SOURCE_NAMES:
            raise _failed(
                SchemaError(f"Nguồn {profile.source_name!r} không thuộc ba nguồn đã chốt."),
                "identifier_invalid",
            )
        if profile.source_name in seen:
            raise _failed(
                SchemaError(f"Tệp {CONFIG_LABEL} khai trùng nguồn {profile.source_name!r}."),
                "identifier_invalid",
            )
        seen.add(profile.source_name)
    absent = tuple(name for name in SOURCE_NAMES if name not in seen)
    if absent:
        raise _failed(
            SchemaError(f"Tệp {CONFIG_LABEL} phải khai đủ ba nguồn đã chốt; thiếu: {', '.join(absent)}."),
            "identifier_invalid",
        )
    simulated = tuple(profile.source_name for profile in profiles if profile.is_simulated)
    if len(simulated) != 1:
        counted = ", ".join(simulated) if simulated else "không có"
        raise _failed(
            SchemaError(
                f"Tệp {CONFIG_LABEL} phải có đúng một nguồn mô phỏng, đếm được {len(simulated)}: {counted}."
            ),
            "identifier_invalid",
        )


def _allowed_fields(field_catalogue: MediatedFieldCatalogue) -> frozenset[str]:
    """Gom mã "entity.field" của C2 thành một tập để đối chiếu."""

    return frozenset(code for codes in field_catalogue.fields_by_entity.values() for code in codes)


def _checked_covered_fields(profile: SourceProfile, allowed: frozenset[str]) -> None:
    """Đối chiếu `covered_fields` với danh mục trường C2, không bỏ qua mã lạ (BR5.3)."""

    unknown = tuple(code for code in profile.covered_fields if code not in allowed)
    if unknown:
        raise _failed(
            SchemaError(
                f"Nguồn {profile.source_name!r} khai trường không có trong danh mục C2: {', '.join(unknown)}."
            ),
            "identifier_invalid",
        )


def _checked_tables(profile: SourceProfile) -> None:
    """Đối chiếu từng tên bảng với `SOURCE_TABLES` của dự án (SR-U5-14)."""

    unknown = tuple(name for name in profile.tables if name not in SOURCE_TABLES)
    if unknown:
        raise _failed(
            SchemaError(
                f"Nguồn {profile.source_name!r} khai bảng ngoài danh sách bảng nguồn: {', '.join(unknown)}."
            ),
            "identifier_invalid",
        )


def _checked_query_fields(raw: object, allowed: frozenset[str]) -> dict[str, tuple[str, ...]]:
    """Kiểm ánh xạ truy vấn → trường cần: đúng ba `query_id` và mọi mã có trong C2."""

    if not isinstance(raw, dict) or not raw:
        raise _failed(SchemaError(f"Tệp {CONFIG_LABEL} thiếu ánh xạ 'query_fields'."), "identifier_invalid")
    declared = tuple(raw)
    missing = tuple(query_id for query_id in QUERY_IDS if query_id not in declared)
    extra = tuple(query_id for query_id in declared if query_id not in QUERY_IDS)
    if missing or extra:
        parts = []
        if missing:
            parts.append("thiếu: " + ", ".join(missing))
        if extra:
            parts.append("thừa: " + ", ".join(extra))
        raise _failed(
            SchemaError(f"Ánh xạ truy vấn của {CONFIG_LABEL} phải đúng ba truy vấn mẫu ({'; '.join(parts)})."),
            "identifier_invalid",
        )
    mapping: dict[str, tuple[str, ...]] = {}
    for query_id in declared:
        codes = raw[query_id]
        if (
            not isinstance(codes, list)
            or not codes
            or not all(isinstance(code, str) and code for code in codes)
        ):
            raise _failed(
                SchemaError(f"Truy vấn {query_id!r} của {CONFIG_LABEL} phải có danh sách mã trường khác rỗng."),
                "identifier_invalid",
            )
        unknown = tuple(code for code in codes if code not in allowed)
        if unknown:
            raise _failed(
                SchemaError(
                    f"Truy vấn {query_id!r} khai trường không có trong danh mục C2: {', '.join(unknown)}."
                ),
                "identifier_invalid",
            )
        mapping[query_id] = tuple(codes)
    return mapping


def _checked_query_fields_match_rewriter(mapping: dict[str, tuple[str, ...]]) -> None:
    """C1: tri thức "truy vấn nào cần trường nào" thuộc U3, không được có bản sao lệch.

    Hàm này dành cho đường chạy **thật** (cấu hình của repo), không chạy trong bộ nạp:
    các fixture test dựng cấu hình rút gọn có chủ đích. Gọi từ test tích hợp để khoá drift.
    """

    from src.integration.rewrite import TEMPLATE_MEDIATED_FIELDS

    expected = {key: tuple(value) for key, value in TEMPLATE_MEDIATED_FIELDS.items()}
    if mapping != expected:
        differing = sorted(
            query_id
            for query_id in set(mapping) | set(expected)
            if mapping.get(query_id) != expected.get(query_id)
        )
        raise SchemaError(
            f"Ánh xạ truy vấn→trường của {CONFIG_LABEL} lệch hằng của U3 ở: "
            f"{', '.join(differing)}. Sửa cấu hình hoặc hằng trong `src/integration/rewrite.py`."
        )


def _read_config(path: Path) -> dict:
    """Đọc tệp cấu hình nguồn bằng `safe_load`; thiếu tệp là lỗi cấu hình (ADR-U5-S1)."""

    if not path.exists():
        raise _failed(
            ConfigurationError(f"Không tìm thấy tệp cấu hình nguồn: {CONFIG_LABEL}"),
            "file_not_found",
        )
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise _failed(
            ConfigurationError(f"Không đọc được tệp cấu hình nguồn {CONFIG_LABEL}: {exc}"),
            "unknown",
        ) from exc
    if not isinstance(raw, dict):
        raise _failed(
            ConfigurationError(f"Tệp cấu hình nguồn {CONFIG_LABEL} phải là một ánh xạ YAML."),
            "unknown",
        )
    sources = raw.get("sources")
    if not isinstance(sources, list) or not sources:
        raise _failed(
            ConfigurationError(f"Tệp {CONFIG_LABEL} thiếu danh sách 'sources' khác rỗng."),
            "unknown",
        )
    return raw


def load_source_catalogue(
    path: Path,
    field_catalogue: MediatedFieldCatalogue,
    pending_query_id: str | None = None,
    logger: LoggerLike | None = None,
) -> SourceCatalogue:
    """Nạp, kiểm toàn bộ rồi dựng danh mục nguồn (C7, BR5.1–BR5.3, BR5.9)."""

    logger = logger if logger is not None else NullLogger()
    try:
        raw = _read_config(Path(path))
        profiles = tuple(_checked_profile(item, index) for index, item in enumerate(raw["sources"], start=1))
        _checked_source_set(profiles)
        allowed = _allowed_fields(field_catalogue)
        for profile in profiles:
            _checked_covered_fields(profile, allowed)
            _checked_tables(profile)
        query_fields = _checked_query_fields(raw.get("query_fields"), allowed)
        if pending_query_id is not None and pending_query_id not in query_fields:
            raise _failed(
                SchemaError(
                    f"Truy vấn chờ đề xuất {pending_query_id!r} không có trong ánh xạ của {CONFIG_LABEL}."
                ),
                "identifier_invalid",
            )
    except (SchemaError, ConfigurationError) as exc:
        logger.error(
            "integration.sources.failed",
            normalise_error_code(getattr(exc, "error_code", "")),
            message=str(exc)[:200],
        )
        raise

    pending = pending_query_id if pending_query_id is not None else next(iter(query_fields))
    catalogue = SourceCatalogue(
        sources=profiles,
        choices=(),
        query_fields=query_fields,
        partial_reason=PARTIAL_REASON,
        pending_query_id=pending,
    )
    logger.info(
        "integration.sources.loaded",
        source_count=len(profiles),
        query_count=len(query_fields),
        simulated_count=sum(1 for profile in profiles if profile.is_simulated),
    )
    logger.warning(
        "integration.sources.partial",
        pending_query_id=pending,
        partial_reason=PARTIAL_REASON,
    )
    return catalogue


def _required_fields(catalogue: SourceCatalogue, query_id: str) -> tuple[str, ...]:
    """Tra ánh xạ truy vấn → trường cần; truy vấn lạ là lỗi lược đồ (W2 bước 1)."""

    required = catalogue.query_fields.get(query_id)
    if required is None:
        raise _failed(
            SchemaError(f"Truy vấn {query_id!r} không có trong ánh xạ của {CONFIG_LABEL}."),
            "identifier_invalid",
        )
    return required


def _evaluate(
    sources: tuple[SourceProfile, ...], required: tuple[str, ...]
) -> tuple[tuple[SourceProfile, tuple[str, ...]], ...]:
    """Tính trường còn thiếu của mỗi nguồn cho một truy vấn (W2 bước 2)."""

    return tuple(
        (profile, tuple(code for code in required if code not in profile.covered_fields)) for profile in sources
    )


def _is_candidate(profile: SourceProfile, missing: tuple[str, ...]) -> bool:
    """Vị từ ứng viên, tách khỏi luật xếp hạng (ADR-U5-S3)."""

    return profile.has_data and not missing and not profile.is_simulated


def _rank(profiles: tuple[SourceProfile, ...]) -> SourceProfile | None:
    """Chọn nguồn đứng đầu theo chi phí, rồi độ trễ, rồi tên (ADR-U5-S6)."""

    if not profiles:
        return None
    return min(profiles, key=lambda profile: (profile.cost_level, profile.latency_ms, profile.source_name))


def _uncovered(
    evaluation: tuple[tuple[SourceProfile, tuple[str, ...]], ...], required: tuple[str, ...]
) -> tuple[str, ...]:
    """Hợp các trường mà không nguồn nào phủ (BR5.6)."""

    return tuple(
        code for code in required if all(code not in profile.covered_fields for profile, _ in evaluation)
    )


def _nearest(evaluation: tuple[tuple[SourceProfile, tuple[str, ...]], ...]) -> str:
    """Nêu nguồn gần nhất và phần nó còn thiếu, cho thông điệp của BR5.6."""

    profile, missing = min(
        evaluation,
        key=lambda item: (
            item[0].is_simulated,
            not item[0].has_data,
            len(item[1]),
            item[0].source_name,
        ),
    )
    return f"nguồn gần nhất {profile.source_name} thiếu: {', '.join(missing) or 'không có trường nào'}"


def _selected_reason(profile: SourceProfile) -> str:
    """Lý do chọn bằng chữ, không dựa vào màu sắc (BR5.8)."""

    return f"được chọn: đủ trường, chi phí {profile.cost_level}, độ trễ {profile.latency_ms} ms"


def _reject_reason(profile: SourceProfile, missing: tuple[str, ...], winner: SourceProfile | None) -> str:
    """Sáu nhánh lý do loại, theo đúng thứ tự ưu tiên của BR5.5."""

    if profile.is_simulated:
        return SIMULATED_REASON
    if not profile.has_data:
        return NO_DATA_REASON
    if missing:
        return "không đủ trường: " + ", ".join(missing)
    if winner is not None and profile.cost_level > winner.cost_level:
        return f"chi phí cao hơn {winner.source_name}"
    if winner is not None and profile.latency_ms > winner.latency_ms:
        return f"cùng chi phí nhưng độ trễ cao hơn {winner.source_name}"
    return NAME_TIE_REASON


def _choice(
    query_id: str,
    profile: SourceProfile,
    missing: tuple[str, ...],
    winner: SourceProfile | None,
) -> SourceChoice:
    """Dựng một dòng quyết định cho cặp (truy vấn, nguồn)."""

    selected = winner is not None and profile.source_name == winner.source_name
    return SourceChoice(
        query_id=query_id,
        source_name=profile.source_name,
        is_selected=selected,
        reason=_selected_reason(profile) if selected else _reject_reason(profile, missing, winner),
        missing_fields=missing,
        tables=profile.tables if selected else (),
    )


def _catalogue_with(
    catalogue: SourceCatalogue,
    query_id: str,
    evaluation: tuple[tuple[SourceProfile, tuple[str, ...]], ...],
    winner: SourceProfile | None,
) -> SourceCatalogue:
    """Dựng bản C7 mới: ghi đè dòng của truy vấn này và xoá nhánh "một phần" (BR5.9)."""

    rows = tuple(_choice(query_id, profile, missing, winner) for profile, missing in evaluation)
    others = tuple(choice for choice in catalogue.choices if choice.query_id != query_id)
    return replace(
        catalogue,
        choices=others + rows,
        partial_reason=None,
        pending_query_id=None,
    )


def select_source(
    catalogue: SourceCatalogue,
    query_id: str,
    logger: LoggerLike | None = None,
) -> SourceSelection:
    """Đề xuất nguồn cho một truy vấn, trả C3 kèm bản C7 đã cập nhật (W2, W3)."""

    logger = logger if logger is not None else NullLogger()
    try:
        required = _required_fields(catalogue, query_id)
        evaluation = _evaluate(catalogue.sources, required)
        ranked = tuple(profile for profile, missing in evaluation if _is_candidate(profile, missing))
        winner = _rank(ranked)
        if winner is not None and winner.is_simulated:
            raise _failed(
                SchemaError("Nguồn mô phỏng không được chọn cho một truy vấn thật (BR5.11)."),
                "identifier_invalid",
            )
        if winner is None:
            missing_fields = _uncovered(evaluation, required)
            raise NoSourceAvailableError(
                f"Không nguồn nào đủ trường cho truy vấn {query_id!r}. "
                f"Trường không nguồn nào phủ: {', '.join(missing_fields) or 'không có'}; "
                f"{_nearest(evaluation)}.",
                missing_fields,
                _catalogue_with(catalogue, query_id, evaluation, None),
            )
        updated = _catalogue_with(catalogue, query_id, evaluation, winner)
        selection = SourceSelection(
            query_id=query_id,
            selected_sources=tuple(
                choice for choice in updated.choices if choice.query_id == query_id and choice.is_selected
            ),
            rejected_sources=tuple(
                choice for choice in updated.choices if choice.query_id == query_id and not choice.is_selected
            ),
            catalogue=updated,
        )
    except (SchemaError, ConfigurationError, NoSourceAvailableError) as exc:
        logger.error(
            "integration.sources.failed",
            normalise_error_code(getattr(exc, "error_code", "")),
            message=str(exc)[:200],
        )
        raise
    logger.info(
        "integration.sources.selected",
        query_id=query_id,
        source_name=selection.selected_sources[0].source_name,
        rejected_count=len(selection.rejected_sources),
    )
    return selection
