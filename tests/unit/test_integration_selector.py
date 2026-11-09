"""Unit tests cho bộ chọn nguồn U5: bốn kiểu C3/C7, bộ nạp cấu hình và luật xếp hạng."""

from __future__ import annotations

import time
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
import yaml

from src.common.exceptions import ConfigurationError, NoSourceAvailableError, SchemaError
from src.config import load_config
from src.integration.models import (
    MediatedFieldCatalogue,
    SourceCatalogue,
    SourceChoice,
    SourceProfile,
    SourceSelection,
)
from src.integration.selector import QUERY_IDS, load_source_catalogue, select_source

ROOT = Path(__file__).resolve().parents[2]
SHIPPED_SOURCES = ROOT / "config" / "integration-sources.yaml"

DON_HANG_FIELDS = (
    "don_hang.ma_don",
    "don_hang.ngay_dat",
    "don_hang.trang_thai",
    "don_hang.ma_khach",
    "don_hang.bang_giao",
    "don_hang.ngay_giao_thuc_te",
    "don_hang.ngay_giao_du_kien",
)
MAT_HANG_FIELDS = (
    "mat_hang.ma_don",
    "mat_hang.ma_san_pham",
    "mat_hang.so_thu_tu",
    "mat_hang.gia",
    "mat_hang.gia_van_chuyen",
)
SAN_PHAM_FIELDS = ("san_pham.ma_san_pham", "san_pham.ten_danh_muc")

ORDERS_TABLES = (
    "olist_orders_dataset",
    "olist_customers_dataset",
    "olist_order_items_dataset",
    "olist_products_dataset",
)

QUERY_FIELDS = {
    "doanh_thu_theo_danh_muc": (
        "don_hang.ma_don",
        "don_hang.trang_thai",
        "mat_hang.ma_don",
        "mat_hang.gia",
        "mat_hang.gia_van_chuyen",
        "mat_hang.ma_san_pham",
        "san_pham.ma_san_pham",
        "san_pham.ten_danh_muc",
    ),
    "doanh_thu_theo_thang": (
        "don_hang.ma_don",
        "don_hang.ngay_dat",
        "don_hang.trang_thai",
        "mat_hang.ma_don",
        "mat_hang.gia",
        "mat_hang.gia_van_chuyen",
    ),
    "ty_le_giao_tre_theo_bang": (
        "don_hang.ma_don",
        "don_hang.ngay_giao_thuc_te",
        "don_hang.ngay_giao_du_kien",
        "don_hang.trang_thai",
        "don_hang.bang_giao",
    ),
}


class RecordingLogger:
    """Logger ghi lại mọi sự kiện trong bộ nhớ, không ghi tệp."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    def info(self, event: str, **fields: object) -> None:
        self.events.append(("INFO", event, fields))

    def warning(self, event: str, **fields: object) -> None:
        self.events.append(("WARNING", event, fields))

    def error(self, event: str, error_code: str, **fields: object) -> None:
        self.events.append(("ERROR", event, {**fields, "error_code": error_code}))


def _profile(name: str = "olist_csv") -> SourceProfile:
    return SourceProfile(
        source_name=name,
        label="Olist (CSV trong dataset/)",
        tables=("olist_orders_dataset",),
        covered_fields=("don_hang.ma_don",),
        coverage="Chỉ có trường đơn hàng",
        has_data=True,
        cost_level=3,
        latency_ms=800,
        is_simulated=False,
    )


def _field_catalogue() -> MediatedFieldCatalogue:
    return MediatedFieldCatalogue(
        fields_by_entity={
            "don_hang": DON_HANG_FIELDS,
            "mat_hang": MAT_HANG_FIELDS,
            "san_pham": SAN_PHAM_FIELDS,
        }
    )


def _source(
    name: str,
    label: str,
    tables: tuple[str, ...],
    covered_fields: tuple[str, ...],
    *,
    has_data: bool = True,
    cost_level: int = 3,
    latency_ms: int = 800,
    is_simulated: bool = False,
) -> dict:
    return {
        "source_name": name,
        "label": label,
        "tables": list(tables),
        "covered_fields": list(covered_fields),
        "has_data": has_data,
        "cost_level": cost_level,
        "latency_ms": latency_ms,
        "is_simulated": is_simulated,
    }


def _profiles() -> list[dict]:
    return [
        _source(
            "olist_csv",
            "Olist (CSV trong dataset/)",
            ORDERS_TABLES,
            DON_HANG_FIELDS + MAT_HANG_FIELDS + SAN_PHAM_FIELDS,
        ),
        _source("ibge_cache", "Cache IBGE cục bộ", (), (), cost_level=2, latency_ms=200),
        _source(
            "partner_simulated",
            "Nguồn đối tác (mô phỏng)",
            ("olist_orders_dataset",),
            DON_HANG_FIELDS,
            cost_level=1,
            latency_ms=50,
            is_simulated=True,
        ),
    ]


def _config(
    sources: list[dict] | None = None,
    queries: dict[str, list[str]] | None = None,
) -> dict:
    return {
        "sources": sources if sources is not None else _profiles(),
        "query_fields": (
            queries
            if queries is not None
            else {query_id: list(codes) for query_id, codes in QUERY_FIELDS.items()}
        ),
    }


def _config_without_queries() -> dict:
    raw = _config()
    raw.pop("query_fields")
    return raw


def _write(tmp_path: Path, raw: dict) -> Path:
    path = tmp_path / "integration-sources.yaml"
    path.write_text(yaml.safe_dump(raw, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def test_source_profile_and_catalogue_are_frozen_and_tuple_based():
    profile = _profile()

    with pytest.raises(FrozenInstanceError):
        profile.cost_level = 1  # type: ignore[misc]
    assert isinstance(profile.tables, tuple)
    assert isinstance(profile.covered_fields, tuple)

    catalogue = SourceCatalogue(
        sources=(profile,),
        choices=(),
        query_fields={"doanh_thu_theo_thang": ("don_hang.ma_don",)},
    )
    with pytest.raises(FrozenInstanceError):
        catalogue.choices = ()  # type: ignore[misc]
    assert isinstance(catalogue.sources, tuple)
    assert isinstance(catalogue.query_fields["doanh_thu_theo_thang"], tuple)


def test_source_catalogue_carries_no_generated_at():
    catalogue = SourceCatalogue(sources=(_profile(),), choices=(), query_fields={})

    assert not hasattr(catalogue, "generated_at")
    assert catalogue.partial_reason is None
    assert catalogue.pending_query_id is None


def test_source_choice_and_selection_require_their_mandatory_fields():
    with pytest.raises(TypeError):
        SourceChoice(query_id="doanh_thu_theo_thang", source_name="olist_csv", is_selected=True)  # type: ignore[call-arg]

    choice = SourceChoice(
        query_id="doanh_thu_theo_thang",
        source_name="olist_csv",
        is_selected=True,
        reason="được chọn: đủ trường",
    )
    catalogue = SourceCatalogue(sources=(_profile(),), choices=(choice,), query_fields={})

    with pytest.raises(TypeError):
        SourceSelection(
            query_id="doanh_thu_theo_thang",
            selected_sources=(choice,),
            rejected_sources=(),
        )  # type: ignore[call-arg]

    selection = SourceSelection(
        query_id="doanh_thu_theo_thang",
        selected_sources=(choice,),
        rejected_sources=(),
        catalogue=catalogue,
    )
    assert selection.missing_fields == ()
    assert selection.catalogue is catalogue


def test_load_rejects_a_missing_file(tmp_path: Path):
    with pytest.raises(ConfigurationError) as excinfo:
        load_source_catalogue(tmp_path / "khong-co.yaml", _field_catalogue())

    assert "config/integration-sources.yaml" in str(excinfo.value)


@pytest.mark.parametrize(
    "broken",
    [
        pytest.param("- chi-la-mot-danh-sach\n", id="khong-phai-anh-xa"),
        pytest.param({"sources": ["chi-la-mot-chuoi"], "query_fields": {}}, id="nguon-khong-phai-anh-xa"),
        pytest.param("sources: [khong dong ngoac\n", id="yaml-hong"),
        pytest.param({"query_fields": {}}, id="thieu-sources"),
        pytest.param({"sources": [], "query_fields": {}}, id="sources-rong"),
        pytest.param(_config_without_queries(), id="thieu-query-fields"),
    ],
)
def test_load_rejects_a_broken_config_document(tmp_path: Path, broken):
    path = tmp_path / "integration-sources.yaml"
    if isinstance(broken, str):
        path.write_text(broken, encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(broken, allow_unicode=True, sort_keys=False), encoding="utf-8")

    with pytest.raises((ConfigurationError, SchemaError)):
        load_source_catalogue(path, _field_catalogue())


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        pytest.param(
            lambda raw: raw["sources"][0].update({"has_data": "false"}),
            "has_data",
            id="has_data-chuoi",
        ),
        pytest.param(
            lambda raw: raw["sources"][0].update({"latency_ms": "800"}),
            "latency_ms",
            id="latency_ms-chuoi",
        ),
        pytest.param(
            lambda raw: raw["sources"][0].update({"latency_ms": -1}),
            "latency_ms",
            id="latency_ms-am",
        ),
        pytest.param(
            lambda raw: raw["sources"][0].update({"cost_level": 9}),
            "cost_level",
            id="cost_level-ngoai-mien",
        ),
        pytest.param(
            lambda raw: raw["sources"][0].pop("is_simulated"),
            "is_simulated",
            id="thieu-is_simulated",
        ),
        pytest.param(
            lambda raw: raw["sources"][1].pop("label"),
            "label",
            id="thieu-label",
        ),
        pytest.param(
            lambda raw: raw["sources"][0].update({"tables": "olist_orders_dataset"}),
            "tables",
            id="tables-khong-phai-danh-sach",
        ),
        pytest.param(
            lambda raw: raw["sources"][0].update({"label": "  "}),
            "label",
            id="label-rong",
        ),
        pytest.param(
            lambda raw: raw["sources"][0].pop("source_name"),
            "source_name",
            id="thieu-source_name",
        ),
    ],
)
def test_load_rejects_a_malformed_profile(tmp_path: Path, mutate, fragment: str):
    raw = _config()
    mutate(raw)

    with pytest.raises(ConfigurationError) as excinfo:
        load_source_catalogue(_write(tmp_path, raw), _field_catalogue())

    assert fragment in str(excinfo.value)


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        pytest.param(
            lambda raw: raw["sources"][0]["covered_fields"].append("don_hang.khong_ton_tai"),
            "don_hang.khong_ton_tai",
            id="truong-la-trong-covered_fields",
        ),
        pytest.param(
            lambda raw: raw["query_fields"]["doanh_thu_theo_thang"].append("don_hang.khong_ton_tai"),
            "don_hang.khong_ton_tai",
            id="truong-la-trong-anh-xa",
        ),
        pytest.param(
            lambda raw: raw["sources"][0]["tables"].append("olist_khong_ton_tai"),
            "olist_khong_ton_tai",
            id="bang-la",
        ),
        pytest.param(
            lambda raw: raw["query_fields"].update({"doanh_thu_theo_thang": "don_hang.ma_don"}),
            "doanh_thu_theo_thang",
            id="anh-xa-khong-phai-danh-sach",
        ),
    ],
)
def test_load_rejects_unknown_identifiers(tmp_path: Path, mutate, fragment: str):
    raw = _config()
    mutate(raw)

    with pytest.raises(SchemaError) as excinfo:
        load_source_catalogue(_write(tmp_path, raw), _field_catalogue())

    assert fragment in str(excinfo.value)


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(
            lambda raw: raw["sources"].append(_source("nguon_thu_tu", "Nguồn thứ tư", (), ())),
            id="ten-nguon-la",
        ),
        pytest.param(
            lambda raw: raw["sources"].append(
                _source("ibge_cache", "Cache IBGE cục bộ", (), (), cost_level=2, latency_ms=200)
            ),
            id="ten-nguon-trung",
        ),
        pytest.param(
            lambda raw: raw["sources"][1].update({"is_simulated": True}),
            id="hai-nguon-mo-phong",
        ),
    ],
)
def test_load_rejects_an_invalid_source_set(tmp_path: Path, mutate):
    raw = _config()
    mutate(raw)

    with pytest.raises(SchemaError):
        load_source_catalogue(_write(tmp_path, raw), _field_catalogue())


def test_load_rejects_a_source_set_missing_one_of_the_three(tmp_path: Path):
    raw = _config()
    raw["sources"] = [profile for profile in raw["sources"] if profile["source_name"] != "ibge_cache"]

    with pytest.raises(SchemaError) as caught:
        load_source_catalogue(_write(tmp_path, raw), _field_catalogue())

    assert "ibge_cache" in str(caught.value)


def test_load_rejects_empty_tables_with_covered_fields(tmp_path: Path):
    raw = _config()
    raw["sources"][1]["covered_fields"] = ["don_hang.ma_don"]

    with pytest.raises(ConfigurationError):
        load_source_catalogue(_write(tmp_path, raw), _field_catalogue())


@pytest.mark.parametrize(
    ("mutate", "pending_query_id"),
    [
        pytest.param(
            lambda raw: raw["query_fields"].pop("ty_le_giao_tre_theo_bang"),
            None,
            id="thieu-mot-truy-van",
        ),
        pytest.param(
            lambda raw: raw["query_fields"].update({"truy_van_la": ["don_hang.ma_don"]}),
            None,
            id="thua-mot-truy-van",
        ),
        pytest.param(lambda raw: raw, "truy_van_la", id="pending-query-la"),
    ],
)
def test_load_rejects_a_query_map_outside_the_three_samples(
    tmp_path: Path, mutate, pending_query_id: str | None
):
    raw = _config()
    mutate(raw)

    with pytest.raises(SchemaError):
        load_source_catalogue(
            _write(tmp_path, raw),
            _field_catalogue(),
            pending_query_id=pending_query_id,
        )


def test_the_shipped_config_and_the_rewriter_agree_on_query_fields():
    """C1: ánh xạ truy vấn→trường có đúng một nguồn sự thật; cấu hình phải khớp hằng của U3."""

    from src.integration.rewrite import TEMPLATE_IDS, TEMPLATE_MEDIATED_FIELDS

    raw = yaml.safe_load(SHIPPED_SOURCES.read_text(encoding="utf-8"))
    declared = {key: tuple(value) for key, value in raw["query_fields"].items()}
    expected = {key: tuple(value) for key, value in TEMPLATE_MEDIATED_FIELDS.items()}

    assert declared == expected
    assert tuple(QUERY_IDS) == tuple(TEMPLATE_IDS)


def test_every_covered_field_belongs_to_a_table_its_profile_declares():
    """C7: hồ sơ không được khai phủ một trường mà bảng nó khai không chứa."""

    raw = yaml.safe_load(SHIPPED_SOURCES.read_text(encoding="utf-8"))
    schema = yaml.safe_load((ROOT / "config" / "mediated-schema.yaml").read_text(encoding="utf-8"))
    field_tables = {
        f"{entity['name']}.{field['field_name']}": field["source_table"]
        for entity in schema["entities"]
        for field in entity["fields"]
    }

    wrong = [
        (profile["source_name"], code, field_tables[code])
        for profile in raw["sources"]
        for code in profile.get("covered_fields", [])
        if field_tables[code] not in profile["tables"]
    ]

    assert wrong == []


def test_load_builds_three_profiles_with_a_derived_coverage_sentence(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())

    assert isinstance(catalogue.sources, tuple)
    assert [profile.source_name for profile in catalogue.sources] == [
        "olist_csv",
        "ibge_cache",
        "partner_simulated",
    ]
    coverage = {profile.source_name: profile.coverage for profile in catalogue.sources}
    assert coverage["olist_csv"] == "Đủ ba bảng: đơn hàng, mặt hàng, sản phẩm"
    assert coverage["ibge_cache"] == "Không phủ trường nào của lược đồ trung gian"
    assert coverage["partner_simulated"] == "Chỉ có trường đơn hàng"
    assert catalogue.sources[0].tables == ORDERS_TABLES
    assert catalogue.sources[1].tables == ()
    assert catalogue.sources[2].is_simulated is True
    assert not any("<" in profile.coverage or ">" in profile.coverage for profile in catalogue.sources)


def test_load_reports_the_partial_branch_with_the_first_or_explicit_query(tmp_path: Path):
    path = _write(tmp_path, _config())

    default = load_source_catalogue(path, _field_catalogue())
    assert default.choices == ()
    assert default.partial_reason == "chưa có kết quả đề xuất cho truy vấn đang chọn"
    assert default.pending_query_id == "doanh_thu_theo_danh_muc"
    assert list(default.query_fields) == list(QUERY_FIELDS)

    explicit = load_source_catalogue(path, _field_catalogue(), pending_query_id="ty_le_giao_tre_theo_bang")
    assert explicit.pending_query_id == "ty_le_giao_tre_theo_bang"


def test_load_logs_the_loaded_and_partial_events_only_with_a_logger(tmp_path: Path, capsys):
    path = _write(tmp_path, _config())

    load_source_catalogue(path, _field_catalogue())
    assert capsys.readouterr().out == ""

    logger = RecordingLogger()
    load_source_catalogue(path, _field_catalogue(), logger=logger)

    assert [(level, event) for level, event, _ in logger.events] == [
        ("INFO", "integration.sources.loaded"),
        ("WARNING", "integration.sources.partial"),
    ]
    assert logger.events[0][2] == {"source_count": 3, "query_count": 3, "simulated_count": 1}
    assert logger.events[1][2] == {
        "pending_query_id": "doanh_thu_theo_danh_muc",
        "partial_reason": "chưa có kết quả đề xuất cho truy vấn đang chọn",
    }


def test_load_logs_the_failed_event_with_a_closed_error_code(tmp_path: Path):
    logger = RecordingLogger()

    with pytest.raises(ConfigurationError):
        load_source_catalogue(tmp_path / "khong-co.yaml", _field_catalogue(), logger=logger)

    level, event, fields = logger.events[0]
    assert (level, event) == ("ERROR", "integration.sources.failed")
    assert fields["error_code"] == "file_not_found"
    assert "config/integration-sources.yaml" in fields["message"]


def test_select_picks_olist_csv_for_every_sample_query(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())

    for query_id in QUERY_FIELDS:
        selection = select_source(catalogue, query_id)
        assert [item.source_name for item in selection.selected_sources] == ["olist_csv"], query_id
        assert selection.selected_sources[0].tables == ORDERS_TABLES
        assert selection.selected_sources[0].reason


def test_select_returns_the_updated_catalogue_and_clears_the_partial_flag(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())

    selection = select_source(catalogue, "doanh_thu_theo_thang")

    updated = selection.catalogue
    assert updated is not catalogue
    assert updated.partial_reason is None
    assert updated.pending_query_id is None
    assert len(updated.choices) == 3
    assert sum(choice.is_selected for choice in updated.choices) == 1
    assert [item.source_name for item in selection.rejected_sources] == [
        "ibge_cache",
        "partner_simulated",
    ]


def test_select_rejects_the_simulated_source_even_when_it_is_cheapest(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())

    selection = select_source(catalogue, "ty_le_giao_tre_theo_bang")
    rejected = {item.source_name: item.reason for item in selection.rejected_sources}

    assert rejected["partner_simulated"] == "nguồn mô phỏng, chỉ dùng để so sánh"
    assert "olist_csv" not in rejected


def test_select_rejects_a_source_without_data(tmp_path: Path):
    profiles = _profiles()
    profiles[0]["has_data"] = False
    profiles[1]["covered_fields"] = list(QUERY_FIELDS["doanh_thu_theo_thang"])
    profiles[1]["tables"] = ["olist_orders_dataset"]
    catalogue = load_source_catalogue(_write(tmp_path, _config(sources=profiles)), _field_catalogue())

    selection = select_source(catalogue, "doanh_thu_theo_thang")
    rejected = {item.source_name: item.reason for item in selection.rejected_sources}

    assert [item.source_name for item in selection.selected_sources] == ["ibge_cache"]
    assert rejected["olist_csv"] == "không có dữ liệu"


def test_select_rejects_a_source_missing_fields(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())

    selection = select_source(catalogue, "doanh_thu_theo_thang")
    rejected = {item.source_name: item for item in selection.rejected_sources}

    assert rejected["ibge_cache"].reason == "không đủ trường: " + ", ".join(
        QUERY_FIELDS["doanh_thu_theo_thang"]
    )
    assert rejected["ibge_cache"].missing_fields == QUERY_FIELDS["doanh_thu_theo_thang"]
    assert rejected["ibge_cache"].tables == ()


@pytest.mark.parametrize(
    ("latency_ms", "cost_level", "loser", "expected", "winner"),
    [
        pytest.param(800, 4, "ibge_cache", "chi phí cao hơn olist_csv", "olist_csv", id="chi-phi-cao-hon"),
        pytest.param(
            900,
            3,
            "ibge_cache",
            "cùng chi phí nhưng độ trễ cao hơn olist_csv",
            "olist_csv",
            id="do-tre-cao-hon",
        ),
        pytest.param(
            800,
            3,
            "olist_csv",
            "cùng chi phí và độ trễ, xếp sau theo tên",
            "ibge_cache",
            id="xep-sau-theo-ten",
        ),
    ],
)
def test_select_rejects_the_loser_by_cost_then_latency_then_name(
    tmp_path: Path, latency_ms: int, cost_level: int, loser: str, expected: str, winner: str
):
    profiles = _profiles()
    required = QUERY_FIELDS["doanh_thu_theo_thang"]
    profiles[1]["covered_fields"] = list(required)
    profiles[1]["tables"] = ["olist_orders_dataset"]
    profiles[1]["latency_ms"] = latency_ms
    profiles[1]["cost_level"] = cost_level
    catalogue = load_source_catalogue(_write(tmp_path, _config(sources=profiles)), _field_catalogue())

    selection = select_source(catalogue, "doanh_thu_theo_thang")
    rejected = {item.source_name: item.reason for item in selection.rejected_sources}

    assert rejected[loser] == expected
    assert [item.source_name for item in selection.selected_sources] == [winner]


def test_select_is_deterministic_when_the_declaration_order_is_reversed(tmp_path: Path):
    required = QUERY_FIELDS["doanh_thu_theo_danh_muc"]
    forward = _profiles()
    forward[1]["covered_fields"] = list(required)
    forward[1]["tables"] = ["olist_orders_dataset"]
    forward[1]["cost_level"] = 3
    forward[1]["latency_ms"] = 800
    reversed_profiles = list(reversed(forward))
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()

    first = select_source(
        load_source_catalogue(_write(tmp_path / "a", _config(sources=forward)), _field_catalogue()),
        "doanh_thu_theo_danh_muc",
    )
    second = select_source(
        load_source_catalogue(_write(tmp_path / "b", _config(sources=reversed_profiles)), _field_catalogue()),
        "doanh_thu_theo_danh_muc",
    )

    assert first.selected_sources[0].source_name == "ibge_cache"
    assert second.selected_sources[0].source_name == "ibge_cache"
    first_reasons = {item.source_name: item.reason for item in first.rejected_sources}
    second_reasons = {item.source_name: item.reason for item in second.rejected_sources}
    assert first_reasons == second_reasons
    assert first.selected_sources[0].tables == second.selected_sources[0].tables


def test_select_raises_when_no_source_covers_the_query(tmp_path: Path):
    profiles = _profiles()
    profiles[0]["covered_fields"].remove("don_hang.bang_giao")
    profiles[2]["covered_fields"].remove("don_hang.bang_giao")
    catalogue = load_source_catalogue(_write(tmp_path, _config(sources=profiles)), _field_catalogue())

    with pytest.raises(NoSourceAvailableError) as excinfo:
        select_source(catalogue, "ty_le_giao_tre_theo_bang")

    error = excinfo.value
    assert error.missing_fields == ("don_hang.bang_giao",)
    assert "don_hang.bang_giao" in str(error)
    assert [choice.source_name for choice in error.catalogue.choices] == [
        "olist_csv",
        "ibge_cache",
        "partner_simulated",
    ]
    assert not any(choice.is_selected for choice in error.catalogue.choices)
    assert error.catalogue.partial_reason is None
    assert all(choice.reason for choice in error.catalogue.choices)


def test_select_rejects_an_unknown_query_id(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())

    with pytest.raises(SchemaError) as excinfo:
        select_source(catalogue, "truy_van_la")

    assert "truy_van_la" in str(excinfo.value)


def test_select_logs_the_selected_event(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())
    logger = RecordingLogger()

    select_source(catalogue, "doanh_thu_theo_thang", logger=logger)

    level, event, fields = logger.events[-1]
    assert (level, event) == ("INFO", "integration.sources.selected")
    assert fields == {
        "query_id": "doanh_thu_theo_thang",
        "source_name": "olist_csv",
        "rejected_count": 2,
    }


def test_select_overwrites_the_rows_of_the_same_query(tmp_path: Path):
    catalogue = load_source_catalogue(_write(tmp_path, _config()), _field_catalogue())

    first = select_source(catalogue, "doanh_thu_theo_thang")
    second = select_source(first.catalogue, "doanh_thu_theo_thang")
    other = select_source(second.catalogue, "ty_le_giao_tre_theo_bang")

    assert len(first.catalogue.choices) == 3
    assert len(second.catalogue.choices) == 3
    assert len(other.catalogue.choices) == 6
    assert [choice.query_id for choice in other.catalogue.choices].count("doanh_thu_theo_thang") == 3


def test_shipped_config_loads_through_app_config_and_selects_olist_csv(tmp_path: Path):
    (tmp_path / "dataset").mkdir()
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f'paths:\n  raw_csv_dir: dataset\n  integration_sources_path: "{SHIPPED_SOURCES.as_posix()}"\n',
        encoding="utf-8",
    )
    config = load_config(config_path)
    assert config.integration_sources_path == SHIPPED_SOURCES

    started = time.perf_counter()
    catalogue = load_source_catalogue(config.integration_sources_path, _field_catalogue())
    selection = select_source(catalogue, "ty_le_giao_tre_theo_bang")
    elapsed_ms = (time.perf_counter() - started) * 1000

    assert len(catalogue.sources) == 3
    assert len(catalogue.query_fields) == 3
    assert [item.source_name for item in selection.selected_sources] == ["olist_csv"]
    assert elapsed_ms <= 2000
