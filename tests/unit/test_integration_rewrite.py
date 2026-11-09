"""Unit test cho ba truy vấn mẫu, việc viết lại sang SQL nguồn và phép đối chiếu KPI (U3)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.common.exceptions import KpiMismatchError, QueryExecutionError, SchemaError
from src.integration import rewrite as rewrite_module
from src.integration.models import (
    KpiComparison,
    KpiDefinition,
    QueryRunResult,
    QueryTemplate,
    RewriteStep,
)
from src.integration.rewrite import (
    COUNT_KPI_ID,
    NULL_GROUP_KEY,
    TEMPLATE_IDS,
    get_template,
    latest_sql,
    reset_latest,
    rewrite_plan,
    run_template,
)
from src.integration.schema import SOURCE_TABLES, load_schema

ROOT = Path(__file__).resolve().parents[2]
SHIPPED_SCHEMA = ROOT / "config" / "mediated-schema.yaml"
SHIPPED_CSV_DIR = ROOT / "dataset"

CATEGORY_TEMPLATE = "doanh_thu_theo_danh_muc"
MONTH_TEMPLATE = "doanh_thu_theo_thang"
LATE_TEMPLATE = "ty_le_giao_tre_theo_bang"

ORDERS_HEADER = (
    "order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,"
    "order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date"
)
CUSTOMERS_HEADER = "customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state"
ITEMS_HEADER = "order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value"
PRODUCTS_HEADER = (
    "product_id,product_category_name,product_name_lenght,product_description_lenght,"
    "product_photos_qty,product_weight_g,product_length_cm,product_height_cm,product_width_cm"
)

# o1 giao trễ, o2 đúng hạn, o3 thiếu ngày giao thực tế (vẫn ở mẫu số), o4 bị huỷ, o5 giao trễ.
ORDERS_ROWS = (
    "o1,c1,delivered,2018-01-05 10:00:00,2018-01-05 11:00:00,2018-01-10 10:00:00,"
    "2018-01-20 10:00:00,2018-01-15 00:00:00",
    "o2,c1,delivered,2018-01-06 10:00:00,2018-01-06 11:00:00,2018-01-10 10:00:00,"
    "2018-01-10 10:00:00,2018-01-15 00:00:00",
    "o3,c2,delivered,2018-02-07 10:00:00,2018-02-07 11:00:00,2018-02-10 10:00:00,,2018-02-20 00:00:00",
    "o4,c2,canceled,2018-02-08 10:00:00,,,,",
    "o5,c3,delivered,2018-02-09 10:00:00,2018-02-09 11:00:00,2018-02-20 10:00:00,"
    "2018-03-01 10:00:00,2018-02-20 00:00:00",
)
CUSTOMERS_ROWS = (
    "c1,u1,01001,sao paulo,SP",
    "c2,u2,02002,rio de janeiro,RJ",
    "c3,u3,03003,campinas,SP",
)
ITEMS_ROWS = (
    "o1,1,p1,s1,2018-01-08 00:00:00,100.00,10.00",
    "o1,2,p2,s1,2018-01-08 00:00:00,50.00,5.00",
    "o2,1,p1,s1,2018-01-09 00:00:00,200.00,0.00",
    "o3,1,p3,s1,2018-02-12 00:00:00,300.00,30.00",
    "o4,1,p1,s1,2018-02-12 00:00:00,999.00,0.00",
    "o5,1,p2,s1,2018-02-15 00:00:00,400.00,40.00",
)
# p3 cố ý thiếu danh mục: nhóm thiếu danh mục vẫn phải có dòng và vẫn phải đối chiếu được.
PRODUCTS_ROWS = (
    "p1,beleza_saude,20,100,1,100,10,10,10",
    "p2,cama_mesa_banho,20,100,1,100,10,10,10",
    "p3,,20,100,1,100,10,10,10",
)

# Số kỳ vọng của bộ dữ liệu trên (đơn delivered, doanh thu = price + freight_value).
CATEGORY_TOTALS = {
    "cama_mesa_banho": 495.0,
    NULL_GROUP_KEY: 330.0,
    "beleza_saude": 310.0,
}
MONTH_TOTALS = {"2018-01": 365.0, "2018-02": 770.0}
LATE_RATES = {"SP": 66.67, "RJ": 0.0}
LATE_COUNTS = {"SP": 3.0, "RJ": 1.0}


class RecordingLogger:
    """Logger ghi lại sự kiện để test khẳng định."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, object]]] = []

    def info(self, event: str, **fields: object) -> None:
        self.events.append(("info", event, fields))

    def warning(self, event: str, **fields: object) -> None:
        self.events.append(("warning", event, fields))

    def error(self, event: str, error_code: str, **fields: object) -> None:
        self.events.append(("error", event, {"error_code": error_code, **fields}))

    def names(self) -> list[str]:
        return [event for _, event, _ in self.events]


def _write_csv(directory: Path, name: str, header: str, rows: tuple[str, ...]) -> None:
    (directory / f"{name}.csv").write_text(
        header + "\n" + "".join(f"{row}\n" for row in rows), encoding="utf-8"
    )


def _dataset(directory: Path) -> Path:
    directory.mkdir(exist_ok=True)
    _write_csv(directory, "olist_orders_dataset", ORDERS_HEADER, ORDERS_ROWS)
    _write_csv(directory, "olist_customers_dataset", CUSTOMERS_HEADER, CUSTOMERS_ROWS)
    _write_csv(directory, "olist_order_items_dataset", ITEMS_HEADER, ITEMS_ROWS)
    _write_csv(directory, "olist_products_dataset", PRODUCTS_HEADER, PRODUCTS_ROWS)
    return directory


class Selection:
    """Đối tượng C3 tối thiểu mà trường đọc: mã truy vấn, nguồn đã chọn và bảng nguồn đó khai."""

    def __init__(self, query_id: str, source_name: str = "olist_csv", tables: tuple[str, ...] = ()) -> None:
        self.query_id = query_id
        choice = type("Choice", (), {"source_name": source_name, "tables": tables})()
        self.selected_sources = (choice,)
        self.rejected_sources = ()
        self.missing_fields = ()


def _selection(template_id: str) -> Selection:
    return Selection(template_id)


def test_a_selected_source_must_declare_every_table_the_template_reads():
    """C3 phải được tiêu thụ thật: nguồn thắng khai thiếu bảng thì U3 từ chối chạy."""

    partial = Selection(CATEGORY_TEMPLATE, tables=("olist_orders_dataset",))

    with pytest.raises(SchemaError) as caught:
        rewrite_module._checked_selection(partial, CATEGORY_TEMPLATE)

    assert "olist_order_items_dataset" in str(caught.value)


def test_a_selected_source_that_declares_no_tables_is_not_checked():
    """Bộ dựng thử không khai bảng: bỏ qua phép kiểm thay vì báo lỗi sai."""

    assert rewrite_module._checked_selection(Selection(CATEGORY_TEMPLATE), CATEGORY_TEMPLATE) == "olist_csv"


def _reference(values: dict[str, float], counts: dict[str, float] | None = None, calls: list | None = None):
    counts = counts or {}

    def reference(template_id: str, params: dict[str, str]):
        if calls is not None:
            calls.append((template_id, dict(params)))
        return {key: (value, counts.get(key)) for key, value in values.items()}

    return reference


def _category_reference(**overrides: float):
    values = {**CATEGORY_TOTALS, "__all__": 1135.0}
    values.update(overrides)
    return _reference(values)


def _month_reference(**overrides: float):
    values = {**MONTH_TOTALS, "__all__": 1135.0}
    values.update(overrides)
    return _reference(values)


def _late_reference(**overrides: float):
    values = {**LATE_RATES, "__all__": 50.0}
    values.update(overrides)
    return _reference(values, counts={**LATE_COUNTS, "__all__": 4.0})


@pytest.fixture(autouse=True)
def _reset_latest() -> None:
    reset_latest()


# --- Mô hình dữ liệu -------------------------------------------------------


def test_three_templates_are_declared_with_the_contract_ids():
    assert TEMPLATE_IDS == (CATEGORY_TEMPLATE, MONTH_TEMPLATE, LATE_TEMPLATE)
    assert tuple(get_template(template_id).template_id for template_id in TEMPLATE_IDS) == TEMPLATE_IDS


def test_query_template_is_frozen_and_carries_plan_and_kpi():
    template = get_template(CATEGORY_TEMPLATE)

    assert isinstance(template, QueryTemplate)
    assert isinstance(template.kpi, KpiDefinition)
    assert template.kpi.kpi_id == CATEGORY_TEMPLATE
    assert template.title
    assert template.mediated_query_text
    assert all(isinstance(step, RewriteStep) for step in template.plan)
    with pytest.raises(FrozenInstanceError):
        template.template_id = "khac"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("template_id", "expected_steps"),
    [(CATEGORY_TEMPLATE, 3), (MONTH_TEMPLATE, 2), (LATE_TEMPLATE, 2)],
)
def test_plan_steps_are_numbered_from_one_without_gaps(template_id: str, expected_steps: int):
    plan = rewrite_plan(template_id)

    assert len(plan) == expected_steps
    assert [step.step for step in plan] == list(range(1, expected_steps + 1))
    assert plan[0].mediated_entity == "don_hang"
    assert plan[0].join_condition == ""
    assert all(step.join_condition for step in plan[1:])


def test_kpi_comparison_carries_group_key_and_signed_delta():
    comparison = KpiComparison(
        kpi_id=CATEGORY_TEMPLATE,
        group_key="beleza_saude",
        expected_value=310.0,
        actual_value=300.0,
        delta=10.0,
        tolerance=0.01,
        matches=False,
    )

    assert comparison.group_key == "beleza_saude"
    assert comparison.delta == pytest.approx(10.0)
    with pytest.raises(FrozenInstanceError):
        comparison.matches = True  # type: ignore[misc]


def test_query_run_result_keeps_the_optional_fields_of_the_contract():
    result = QueryRunResult(
        plan_id="plan-1",
        template_id=LATE_TEMPLATE,
        template_title="Tỷ lệ giao trễ theo bang",
        mediated_query_text="SELECT ...",
        rewrite_plan=[RewriteStep(1, "don_hang", "olist_orders_dataset")],
        source_sql="SELECT ...",
        rows=[],
        row_count=0,
        elapsed_ms=1,
        total_orders=None,
        months=None,
        partial=[],
    )

    assert result.total_orders is None
    assert result.months is None
    assert result.row_count == len(result.rows)


# --- Mẫu SQL và nguồn ------------------------------------------------------


@pytest.mark.parametrize("template_id", TEMPLATE_IDS)
def test_source_sql_is_a_parameterised_constant_reference(template_id: str):
    template = get_template(template_id)
    sql = template.source_sql

    assert "?" in sql
    assert "{" not in sql
    for table in rewrite_module.template_tables(template_id):
        assert table in SOURCE_TABLES
        assert table in sql
    assert sql == rewrite_module.SOURCE_SQL[template_id]


def test_unknown_template_id_raises_a_schema_error():
    with pytest.raises(SchemaError) as caught:
        get_template("doanh_thu_theo_nam")

    assert "doanh_thu_theo_nam" in str(caught.value)


def test_shipped_schema_declares_every_field_the_templates_need():
    schema = load_schema(SHIPPED_SCHEMA, csv_dir=SHIPPED_CSV_DIR)

    assert schema.entity("don_hang").field("bang_giao").loaded is True
    assert schema.entity("san_pham").field("ten_danh_muc").loaded is True
    assert schema.entity("don_hang").field("ngay_giao_thuc_te").source_column == (
        "order_delivered_customer_date"
    )
    assert schema.entity("don_hang").field("ngay_giao_du_kien").source_column == (
        "order_estimated_delivery_date"
    )
    assert schema.entity("mat_hang").field("gia_van_chuyen").source_column == "freight_value"
    for template_id in TEMPLATE_IDS:
        for code in rewrite_module.template_mediated_fields(template_id):
            entity_name, field_name = code.split(".")
            assert schema.entity(entity_name).field(field_name) is not None


# --- Tham số và C3 ---------------------------------------------------------


def test_params_must_be_a_mapping(tmp_path: Path):
    with pytest.raises(SchemaError):
        run_template(CATEGORY_TEMPLATE, "2018-01-01", _selection(CATEGORY_TEMPLATE))


def test_an_invalid_date_is_rejected(tmp_path: Path):
    with pytest.raises(SchemaError) as caught:
        run_template(
            CATEGORY_TEMPLATE,
            {"ngay_tu": "31/01/2018"},
            _selection(CATEGORY_TEMPLATE),
            csv_dir=_dataset(tmp_path),
            reference=_category_reference(),
        )

    assert "ngay_tu" in str(caught.value)


def test_an_unknown_param_key_is_rejected(tmp_path: Path):
    with pytest.raises(SchemaError) as caught:
        run_template(
            MONTH_TEMPLATE,
            {"tu_ngay": "2018-01-01"},
            _selection(MONTH_TEMPLATE),
            csv_dir=_dataset(tmp_path),
            reference=_month_reference(),
        )

    assert "tu_ngay" in str(caught.value)


def test_a_param_that_smuggles_sql_is_rejected_before_any_query(tmp_path: Path):
    with pytest.raises(SchemaError):
        run_template(
            CATEGORY_TEMPLATE,
            {"trang_thai": "delivered'; DROP TABLE olist_orders_dataset; --"},
            _selection(CATEGORY_TEMPLATE),
            csv_dir=_dataset(tmp_path),
            reference=_category_reference(),
        )

    assert get_template(CATEGORY_TEMPLATE).source_sql == rewrite_module.SOURCE_SQL[CATEGORY_TEMPLATE]


def test_a_selection_without_selected_sources_is_rejected(tmp_path: Path):
    empty = Selection(CATEGORY_TEMPLATE)
    empty.selected_sources = ()

    with pytest.raises(SchemaError):
        run_template(CATEGORY_TEMPLATE, {}, empty, csv_dir=_dataset(tmp_path))


def test_a_selection_for_another_query_is_rejected(tmp_path: Path):
    with pytest.raises(SchemaError) as caught:
        run_template(
            CATEGORY_TEMPLATE,
            {},
            _selection(MONTH_TEMPLATE),
            csv_dir=_dataset(tmp_path),
            reference=_category_reference(),
        )

    assert MONTH_TEMPLATE in str(caught.value)


# --- Chạy trên DuckDB ------------------------------------------------------


def test_category_template_groups_by_category_and_sums_price_plus_freight(tmp_path: Path):
    result = run_template(
        CATEGORY_TEMPLATE,
        {},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_category_reference(),
    )

    assert result.row_count == len(result.rows) == 3
    assert [row["nhom"] for row in result.rows] == ["cama_mesa_banho", NULL_GROUP_KEY, "beleza_saude"]
    assert result.rows[0]["gia_tri"] == pytest.approx(495.0)
    assert result.rows[0]["so_dong"] == 2
    assert result.total_orders == 4
    assert result.months is None


def test_month_template_groups_by_purchase_month_ascending(tmp_path: Path):
    result = run_template(
        MONTH_TEMPLATE,
        {},
        _selection(MONTH_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_month_reference(),
    )

    assert [row["thang"] for row in result.rows] == ["2018-01", "2018-02"]
    assert result.rows[0]["gia_tri"] == pytest.approx(365.0)
    assert result.rows[1]["gia_tri"] == pytest.approx(770.0)
    assert result.months == ["2018-01", "2018-02"]
    assert result.total_orders == 4


def test_late_template_keeps_rows_without_a_delivery_date_in_the_denominator(tmp_path: Path):
    result = run_template(
        LATE_TEMPLATE,
        {},
        _selection(LATE_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_late_reference(),
    )

    rates = {row["nhom"]: row["ty_le"] for row in result.rows}
    counts = {row["nhom"]: row["so_dong"] for row in result.rows}
    assert rates == {"SP": pytest.approx(66.67), "RJ": pytest.approx(0.0)}
    assert counts == {"SP": 3, "RJ": 1}
    assert result.total_orders is None
    assert result.months is None


def test_the_date_range_narrows_both_sides(tmp_path: Path):
    calls: list = []
    reference = _reference(
        {"cama_mesa_banho": 440.0, NULL_GROUP_KEY: 330.0, "__all__": 770.0},
        calls=calls,
    )

    result = run_template(
        CATEGORY_TEMPLATE,
        {"ngay_tu": "2018-02-01", "ngay_den": "2018-02-28"},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=reference,
    )

    assert {row["nhom"] for row in result.rows} == {"cama_mesa_banho", NULL_GROUP_KEY}
    assert calls == [
        (
            CATEGORY_TEMPLATE,
            {"ngay_tu": "2018-02-01", "ngay_den": "2018-02-28", "trang_thai": "delivered"},
        )
    ]


def test_an_empty_status_param_widens_the_revenue_query(tmp_path: Path):
    reference = _reference(
        {"cama_mesa_banho": 495.0, NULL_GROUP_KEY: 330.0, "beleza_saude": 1309.0, "__all__": 2134.0}
    )

    result = run_template(
        CATEGORY_TEMPLATE,
        {"trang_thai": ""},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=reference,
    )

    assert {row["nhom"] for row in result.rows} == {"cama_mesa_banho", NULL_GROUP_KEY, "beleza_saude"}


def test_the_revenue_query_filters_delivered_by_default(tmp_path: Path):
    result = run_template(
        CATEGORY_TEMPLATE,
        {},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_category_reference(),
    )

    assert sum(row["so_dong"] for row in result.rows) == 5


def test_elapsed_ms_measures_the_sql_and_load_ms_is_logged_separately(tmp_path: Path):
    logger = RecordingLogger()

    result = run_template(
        CATEGORY_TEMPLATE,
        {},
        _selection(CATEGORY_TEMPLATE),
        logger,
        csv_dir=_dataset(tmp_path),
        reference=_category_reference(),
    )

    assert isinstance(result.elapsed_ms, int) and result.elapsed_ms >= 0
    completed = [fields for _, event, fields in logger.events if event == "integration.query.completed"]
    assert logger.names()[0] == "integration.query.started"
    assert len(completed) == 1
    assert isinstance(completed[0]["load_ms"], int)
    assert completed[0]["load_ms"] >= 0
    assert completed[0]["elapsed_ms"] == result.elapsed_ms


def test_a_slow_query_is_only_a_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    logger = RecordingLogger()
    monkeypatch.setattr(rewrite_module, "SLOW_QUERY_MS", -1)

    result = run_template(
        MONTH_TEMPLATE,
        {},
        _selection(MONTH_TEMPLATE),
        logger,
        csv_dir=_dataset(tmp_path),
        reference=_month_reference(),
    )

    assert result.row_count == 2
    assert "integration.query.slow" in logger.names()


def test_a_missing_source_file_is_a_query_execution_error(tmp_path: Path):
    dataset = _dataset(tmp_path)
    (dataset / "olist_products_dataset.csv").unlink()

    with pytest.raises(QueryExecutionError):
        run_template(
            CATEGORY_TEMPLATE,
            {},
            _selection(CATEGORY_TEMPLATE),
            csv_dir=dataset,
            reference=_category_reference(),
        )


def test_a_column_missing_from_the_header_is_a_schema_error(tmp_path: Path):
    dataset = _dataset(tmp_path)
    _write_csv(
        dataset, "olist_products_dataset", PRODUCTS_HEADER.replace("product_category_name", "categoria"), ()
    )

    with pytest.raises(SchemaError) as caught:
        run_template(
            CATEGORY_TEMPLATE,
            {},
            _selection(CATEGORY_TEMPLATE),
            csv_dir=dataset,
            reference=_category_reference(),
        )

    assert "product_category_name" in str(caught.value)


def test_a_sql_failure_is_logged_and_wrapped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    logger = RecordingLogger()
    monkeypatch.setitem(rewrite_module.SOURCE_SQL, MONTH_TEMPLATE, "SELECT * FROM bang_khong_ton_tai")

    with pytest.raises(QueryExecutionError):
        run_template(
            MONTH_TEMPLATE,
            {},
            _selection(MONTH_TEMPLATE),
            logger,
            csv_dir=_dataset(tmp_path),
            reference=_month_reference(),
        )

    failed = [fields for _, event, fields in logger.events if event == "integration.query.failed"]
    assert failed and failed[0]["error_code"] == "sql_error"


def test_a_failing_reference_propagates_unchanged_and_is_logged(tmp_path: Path):
    logger = RecordingLogger()

    def explosion(template_id: str, params: dict[str, str]):
        raise QueryExecutionError("không mở được warehouse/olist.duckdb")

    with pytest.raises(QueryExecutionError) as caught:
        run_template(
            MONTH_TEMPLATE,
            {},
            _selection(MONTH_TEMPLATE),
            logger,
            csv_dir=_dataset(tmp_path),
            reference=explosion,
        )

    assert "warehouse" in str(caught.value)
    assert "integration.query.failed" in logger.names()


# --- Đọc lại SQL -----------------------------------------------------------


def test_latest_sql_is_none_before_the_first_run():
    assert latest_sql(CATEGORY_TEMPLATE) is None


def test_latest_sql_returns_the_sql_of_the_latest_run(tmp_path: Path):
    run_template(
        CATEGORY_TEMPLATE,
        {},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_category_reference(),
    )

    assert latest_sql(CATEGORY_TEMPLATE) == rewrite_module.SOURCE_SQL[CATEGORY_TEMPLATE]
    assert latest_sql(MONTH_TEMPLATE) is None


def test_latest_sql_of_an_unknown_template_raises_a_schema_error():
    with pytest.raises(SchemaError):
        latest_sql("doanh_thu_theo_nam")


# --- Đối chiếu KPI ---------------------------------------------------------


def test_a_matching_run_compares_every_group_and_the_all_row(tmp_path: Path):
    result = run_template(
        CATEGORY_TEMPLATE,
        {},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_category_reference(),
    )

    keys = {(row.kpi_id, row.group_key) for row in result.kpi_comparison}
    assert (CATEGORY_TEMPLATE, "beleza_saude") in keys
    assert (CATEGORY_TEMPLATE, "__all__") in keys
    assert (COUNT_KPI_ID, "__all__") in keys
    assert all(row.matches for row in result.kpi_comparison)
    assert result.partial == []


def test_a_two_cent_drift_raises_a_mismatch_error(tmp_path: Path):
    reference = _category_reference(beleza_saude=310.02)

    with pytest.raises(KpiMismatchError) as caught:
        run_template(
            CATEGORY_TEMPLATE,
            {},
            _selection(CATEGORY_TEMPLATE),
            csv_dir=_dataset(tmp_path),
            reference=reference,
        )

    assert caught.value.groups == (
        (CATEGORY_TEMPLATE, "beleza_saude", pytest.approx(310.02 - 310.0, abs=1e-9)),
    )
    assert "beleza_saude" in str(caught.value)


def test_a_one_cent_drift_is_within_the_money_tolerance(tmp_path: Path):
    reference = _category_reference(beleza_saude=310.01)

    result = run_template(
        CATEGORY_TEMPLATE,
        {},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=reference,
    )

    assert result.row_count == 3


def test_a_group_missing_on_one_side_is_compared_against_zero_and_fails(tmp_path: Path):
    reference = _reference({"cama_mesa_banho": 495.0, NULL_GROUP_KEY: 330.0, "__all__": 805.0})

    with pytest.raises(KpiMismatchError) as caught:
        run_template(
            CATEGORY_TEMPLATE,
            {},
            _selection(CATEGORY_TEMPLATE),
            csv_dir=_dataset(tmp_path),
            reference=reference,
        )

    assert any(group_key == "beleza_saude" for _, group_key, _ in caught.value.groups)


def test_a_group_the_reference_cannot_value_goes_to_partial_instead_of_failing(tmp_path: Path):
    values = {**CATEGORY_TOTALS, "__all__": 1135.0}
    values["beleza_saude"] = None
    result = run_template(
        CATEGORY_TEMPLATE,
        {},
        _selection(CATEGORY_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_reference(values),  # type: ignore[arg-type]
    )

    assert result.partial
    assert "beleza_saude" in " ".join(result.partial)
    assert all(row.group_key != "beleza_saude" for row in result.kpi_comparison)


def test_the_row_count_tolerance_is_zero(tmp_path: Path):
    reference = _reference({"cama_mesa_banho": 495.0, NULL_GROUP_KEY: 330.0, "__all__": 825.0})
    reference_values = reference

    def drifted(template_id: str, params: dict[str, str]):
        values = dict(reference_values(template_id, params))
        values["__all__"] = (4.0, None)
        return values

    with pytest.raises(KpiMismatchError) as caught:
        run_template(
            CATEGORY_TEMPLATE,
            {},
            _selection(CATEGORY_TEMPLATE),
            csv_dir=_dataset(tmp_path),
            reference=drifted,
        )

    assert any(kpi_id == COUNT_KPI_ID for kpi_id, _, _ in caught.value.groups)


def test_the_late_template_compares_the_rate_and_the_order_count(tmp_path: Path):
    result = run_template(
        LATE_TEMPLATE,
        {},
        _selection(LATE_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_late_reference(),
    )

    keys = {(row.kpi_id, row.group_key) for row in result.kpi_comparison}
    assert (LATE_TEMPLATE, "SP") in keys
    assert (COUNT_KPI_ID, "SP") in keys
    assert (LATE_TEMPLATE, "__all__") in keys
    assert all(row.matches for row in result.kpi_comparison)


def test_the_outcome_carries_both_queries_the_plan_and_the_kpi_definition(tmp_path: Path):
    result = run_template(
        MONTH_TEMPLATE,
        {},
        _selection(MONTH_TEMPLATE),
        csv_dir=_dataset(tmp_path),
        reference=_month_reference(),
    )

    assert result.template_id == MONTH_TEMPLATE
    assert result.mediated_query_text
    assert result.source_sql == rewrite_module.SOURCE_SQL[MONTH_TEMPLATE]
    assert len(result.rewrite_plan) == 2
    assert {definition.kpi_id for definition in result.kpi_definitions} == {
        MONTH_TEMPLATE,
        COUNT_KPI_ID,
    }
