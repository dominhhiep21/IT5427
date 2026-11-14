"""Unit test khối mô hình của U2: đặc trưng, chia tập, mã hoá, ngưỡng và khối ghi ra (BR2.1–BR2.9)."""

from __future__ import annotations

import re
from pathlib import Path

import duckdb
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression

from src.analytics import model as model_module
from src.analytics.model import (
    CATEGORICAL_FEATURES,
    EXPECTED_DELIVERED,
    EXPECTED_LATE,
    FEATURES,
    FLAG_FEATURES,
    FORBIDDEN_COLUMNS,
    MAX_ITER,
    NUMERIC_FEATURES,
    RANDOM_STATE,
    SPLIT_DATE,
    TARGET,
    THRESHOLD_METHOD,
    ModelError,
    auc_below_target,
    build_estimator,
    build_feature_frame,
    build_model_block,
    choose_threshold,
    delivered_population,
    encode_features,
    split_frame,
    split_summary,
    train_classifier,
    train_from_frame,
    train_model,
    validate_counts,
    validate_features,
)
from src.analytics.service import TRAINING_FRAME_SQL, AnalyticsService
from src.integrate.catalog import VIEW_TABLES

STATES = ("SP", "RJ", "MG")
REGIONS = ("Sudeste", "Nordeste", "Sul")
PAYMENT_TYPES = ("credit_card", "boleto", "voucher")
ROWS = 120
LATE_ROWS = 36


def make_frame(count: int = ROWS) -> pd.DataFrame:
    """Khung grain dòng hàng 120 dòng: 90 dòng trước 2018-04-01, 30 dòng từ mốc cắt trở đi."""

    start = pd.Timestamp("2018-01-01")
    records = []
    for index in range(count):
        records.append(
            {
                "order_id": f"o{index}",
                "order_item_id": 1,
                "date_key": (start + pd.Timedelta(days=index)).strftime("%Y-%m-%d"),
                "is_delivered": True,
                "is_late": (index % 10) < 3,
                "has_items": index % 17 != 0,
                "has_payment": index % 13 != 0,
                "customer_state": STATES[index % 3],
                "customer_region": REGIONS[index % 3],
                "purchase_month": float(1 + index % 12),
                "purchase_weekday": float(index % 7),
                "item_count": float(1 + index % 4),
                "item_total": float(10 + (index % 7) * 5),
                "item_price_max": float(5 + index % 9),
                "payment_type": PAYMENT_TYPES[index % 3],
                "payment_installments": float(1 + index % 6),
                "seller_state": STATES[(index + 1) % 3],
                "handling_days": float(index % 5),
                "approval_days": float(index % 3),
            }
        )
    return pd.DataFrame(records)


def population(count: int = ROWS) -> pd.DataFrame:
    frame = make_frame(count)
    return delivered_population(frame, expected_delivered=count, expected_late=LATE_ROWS)


def split_matrices():
    train, test = split_frame(population())
    return encode_features(build_feature_frame(train), build_feature_frame(test)), train, test


# --- BR2.1: quần thể huấn luyện -------------------------------------------------------------


def test_the_recorded_baseline_is_the_delivered_population():
    assert EXPECTED_DELIVERED == 110_195
    assert EXPECTED_LATE == 8_713


def test_undelivered_orders_are_dropped_explicitly():
    frame = make_frame(8)
    frame.loc[3, "is_delivered"] = False
    frame.loc[3, "is_late"] = True

    kept = delivered_population(frame, expected_delivered=7, expected_late=3)

    assert len(kept) == 7
    assert kept["is_delivered"].all()
    assert "o3" not in set(kept["order_id"])


def test_a_population_that_does_not_match_the_baseline_stops_the_model():
    frame = make_frame(8)

    with pytest.raises(ModelError):
        delivered_population(frame, expected_delivered=EXPECTED_DELIVERED, expected_late=EXPECTED_LATE)


def test_a_late_count_that_does_not_match_the_baseline_stops_the_model():
    frame = make_frame(8)

    with pytest.raises(ModelError):
        delivered_population(frame, expected_delivered=8, expected_late=4)


def test_a_frame_without_the_label_or_the_delivery_flag_stops_the_model():
    frame = make_frame(4).drop(columns=[TARGET])

    with pytest.raises(ModelError):
        delivered_population(frame, expected_delivered=4, expected_late=1)


# --- BR2.2: chia tập theo thời gian ---------------------------------------------------------


def test_the_split_keeps_the_cut_day_in_the_test_split():
    frame = population()

    train, test = split_frame(frame)
    bounds = split_summary(train, test, expected_total=ROWS)

    assert bounds["train_end"] < bounds["test_start"]
    assert bounds["test_start"] == SPLIT_DATE
    assert bounds["train_end"] == "2018-03-31"
    assert bounds["train_n"] == 90
    assert bounds["test_n"] == 30
    boundary = frame[pd.to_datetime(frame["date_key"]) == pd.Timestamp(SPLIT_DATE)]
    assert set(boundary["order_id"]) <= set(test["order_id"])
    assert set(train["order_id"]) & set(test["order_id"]) == set()


def test_an_empty_split_stops_the_model():
    frame = population()

    with pytest.raises(ModelError):
        split_frame(frame, split_date="2017-01-01")

    with pytest.raises(ModelError):
        split_frame(frame, split_date="2019-01-01")


def test_a_split_that_does_not_add_up_to_the_sample_stops_the_model():
    train, test = split_frame(population())

    with pytest.raises(ModelError):
        split_summary(train, test, expected_total=ROWS + 1)


def test_a_purchase_date_that_cannot_be_read_stops_the_split():
    frame = population().copy()
    frame.loc[0, "date_key"] = "không-phải-ngày"

    with pytest.raises(ModelError):
        split_frame(frame)


def test_a_split_whose_order_is_inverted_stops_the_summary():
    train, test = split_frame(population())

    with pytest.raises(ModelError):
        split_summary(test, train, expected_total=ROWS)


# --- BR2.3: danh sách đặc trưng, không rò rỉ nhãn -------------------------------------------


def test_the_feature_list_and_the_forbidden_set_do_not_intersect():
    assert len(FEATURES) == 14
    assert len(FORBIDDEN_COLUMNS) == 11
    assert len(set(FEATURES)) == len(FEATURES)
    assert set(FEATURES) & set(FORBIDDEN_COLUMNS) == set()


def test_the_feature_list_is_six_categorical_six_numeric_two_flag_columns():
    assert set(FEATURES) == set(CATEGORICAL_FEATURES) | set(NUMERIC_FEATURES) | set(FLAG_FEATURES)
    assert len(CATEGORICAL_FEATURES) == 6
    assert len(NUMERIC_FEATURES) == 6
    assert len(FLAG_FEATURES) == 2


def test_the_label_and_the_post_delivery_columns_are_forbidden():
    assert TARGET in FORBIDDEN_COLUMNS
    assert "has_review" in FORBIDDEN_COLUMNS
    assert "order_delivered_customer_date" in FORBIDDEN_COLUMNS
    assert "delivery_days" in FORBIDDEN_COLUMNS
    assert "review_score" in FORBIDDEN_COLUMNS


def test_training_is_refused_when_the_feature_list_carries_a_forbidden_column():
    with pytest.raises(ModelError):
        validate_features(FEATURES + ("has_review",))


def test_training_is_refused_when_the_feature_list_has_a_duplicate_or_the_wrong_size():
    with pytest.raises(ModelError):
        validate_features(FEATURES + ("item_total",))

    with pytest.raises(ModelError):
        validate_features(("item_total",))


def test_the_feature_frame_built_from_a_real_shaped_frame_carries_only_the_eleven_names():
    frame = make_frame(12)
    frame["has_review"] = True
    frame["delivery_days"] = 3.5
    frame["review_score"] = 5
    frame["order_delivered_customer_date"] = "2018-01-09"
    frame["order_delivered_carrier_date"] = "2018-01-05"

    features = build_feature_frame(frame)

    assert list(features.columns) == list(FEATURES)
    assert set(features.columns) & set(FORBIDDEN_COLUMNS) == set()


def test_a_missing_feature_column_stops_the_build():
    frame = make_frame(4).drop(columns=["customer_region"])

    with pytest.raises(ModelError):
        build_feature_frame(frame)


# --- TS-8: giá trị thiếu không bỏ dòng ------------------------------------------------------


def test_missing_items_and_payments_become_zero_plus_the_existing_flag():
    frame = make_frame(3)
    frame.loc[1, ["item_count", "item_total", "item_price_max"]] = None
    frame.loc[1, "has_items"] = False
    frame.loc[2, ["payment_type", "payment_installments"]] = None
    frame.loc[2, "has_payment"] = False

    features = build_feature_frame(frame)

    assert len(features) == 3
    assert features.loc[1, "item_count"] == 0.0
    assert features.loc[1, "item_total"] == 0.0
    assert features.loc[1, "has_items"] == 0.0
    assert features.loc[2, "payment_type"] == "unknown"
    assert features.loc[2, "payment_installments"] == 0.0
    assert features.loc[2, "has_payment"] == 0.0


def test_orders_without_items_or_payments_stay_in_the_sample():
    frame = make_frame(ROWS)
    frame.loc[[5, 6], ["item_count", "item_total", "item_price_max"]] = None
    frame.loc[[5, 6], "has_items"] = False
    frame.loc[7, ["payment_type", "payment_installments"]] = None
    frame.loc[7, "has_payment"] = False

    block = train_from_frame(frame, expected_delivered=ROWS, expected_late=LATE_ROWS)

    assert block.split["train_n"] + block.split["test_n"] == ROWS


# --- TS-6: one-hot với phạm trù khớp trên tập huấn luyện ------------------------------------


def test_one_hot_categories_come_from_the_training_split_only():
    train_features = build_feature_frame(make_frame(6))
    test_features = build_feature_frame(make_frame(6).assign(payment_type="pix"))

    train_matrix, test_matrix = encode_features(train_features, test_features)

    assert list(train_matrix.columns) == list(test_matrix.columns)
    pix_columns = [name for name in test_matrix.columns if name.startswith("payment_type=")]
    assert pix_columns
    assert "payment_type=pix" not in train_matrix.columns
    assert test_matrix[pix_columns].sum().sum() == 0.0


def test_the_matrices_are_the_same_width_on_both_splits():
    (train_matrix, test_matrix), _, _ = split_matrices()

    assert train_matrix.shape[1] == test_matrix.shape[1]
    assert train_matrix.shape[0] == 90
    assert test_matrix.shape[0] == 30


# --- TS-9: chuẩn hoá khớp trên tập huấn luyện, hội tụ là bắt buộc ---------------------------


def test_the_scaler_is_fitted_on_the_training_split_only():
    train_features = build_feature_frame(make_frame(4).assign(item_count=1.0))
    test_features = build_feature_frame(make_frame(1).assign(item_count=5.0))

    train_matrix, test_matrix = encode_features(train_features, test_features)

    assert train_matrix["item_count"].abs().sum() == 0.0
    assert test_matrix["item_count"].tolist() == [4.0]


def test_a_non_converging_fit_is_an_error(monkeypatch):
    (train_matrix, _), train, _ = split_matrices()
    monkeypatch.setattr(model_module, "build_estimator", lambda: LogisticRegression(max_iter=1))

    with pytest.raises(ModelError):
        train_classifier(train_matrix, train[TARGET].astype(bool))


# --- BR2.4: cân trọng số lớp ----------------------------------------------------------------


def test_the_estimator_is_balanced_seeded_and_bounded():
    params = build_estimator().get_params()

    assert params["class_weight"] == "balanced"
    assert params["max_iter"] == MAX_ITER == 1000
    assert params["random_state"] == RANDOM_STATE


def test_the_fitted_classifier_keeps_the_balanced_weight():
    (train_matrix, _), train, _ = split_matrices()

    classifier = train_classifier(train_matrix, train[TARGET].astype(bool))

    assert classifier.get_params()["class_weight"] == "balanced"
    assert classifier.coef_.shape[0] == 1


# --- BR2.5: ngưỡng là F1 lớn nhất trên lưới 19 điểm -----------------------------------------


def test_the_threshold_grid_is_nineteen_points_from_five_to_ninety_five():
    assert len(model_module.THRESHOLD_GRID) == 19
    assert model_module.THRESHOLD_GRID[0] == 0.05
    assert model_module.THRESHOLD_GRID[-1] == 0.95


def test_the_picked_threshold_is_the_grid_point_with_the_highest_f1():
    labels = pd.Series([True, False, False, False])
    scores = pd.Series([0.9, 0.85, 0.1, 0.05])

    point = choose_threshold(labels, scores)

    # Chỉ 0,90 tách đúng một đơn trễ: precision 1, recall 1, F1 1.
    assert point.threshold == 0.9
    assert point.precision == 1.0
    assert point.recall == 1.0
    assert point.f1 == 1.0


def test_a_tie_on_f1_picks_the_higher_threshold():
    labels = pd.Series([True, True, False, False])
    scores = pd.Series([0.9, 0.8, 0.2, 0.1])

    point = choose_threshold(labels, scores)

    # Mọi điểm trong lưới từ 0,25 tới 0,80 đều cho F1 1: ngưỡng 0,25 đã bỏ 0,2 ra ngoài, còn
    # ngưỡng 0,80 vẫn bắt đúng hai đơn trễ; hoà thì chọn ngưỡng cao hơn.
    assert point.threshold == 0.8


def test_a_test_split_with_one_class_cannot_pick_a_threshold():
    labels = pd.Series([False, False, False])

    with pytest.raises(ModelError):
        choose_threshold(labels, pd.Series([0.2, 0.4, 0.6]))


# --- BR2.6: AUC dưới 0,70 được ghi rõ -------------------------------------------------------


def test_an_auc_below_the_target_is_flagged():
    assert auc_below_target(0.69) is True
    assert auc_below_target(0.70) is False
    assert auc_below_target(0.7001) is False


# --- BR2.7: ba con số đếm khớp nhau ---------------------------------------------------------


def test_counts_that_do_not_add_up_stop_the_block():
    counts = {
        "flagged": 3,
        "not_flagged": 6,
        "total": 10,
        "threshold_method": THRESHOLD_METHOD,
        "auc_below_target": False,
    }

    with pytest.raises(ModelError):
        validate_counts(counts, 10)


def test_counts_that_do_not_match_the_test_split_stop_the_block():
    counts = {
        "flagged": 3,
        "not_flagged": 7,
        "total": 10,
        "threshold_method": THRESHOLD_METHOD,
        "auc_below_target": False,
    }

    validate_counts(counts, 10)
    with pytest.raises(ModelError):
        validate_counts(counts, 11)


def test_a_built_block_counts_add_up_to_the_test_split():
    block = train_from_frame(make_frame(ROWS), expected_delivered=ROWS, expected_late=LATE_ROWS)
    counts = block.counts

    assert counts["flagged"] + counts["not_flagged"] == counts["total"] == block.split["test_n"]
    assert counts["threshold_method"] == THRESHOLD_METHOD
    assert counts["auc_below_target"] is (block.auc < 0.7)


# --- BR2.8: khối trả về, không mở tệp báo cáo -----------------------------------------------


def test_the_block_builder_never_reaches_for_the_report_file(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("U2 không được đọc hay ghi tệp báo cáo (BR2.8)")

    monkeypatch.setattr("src.analytics.report.write_report", forbidden)
    monkeypatch.setattr("src.analytics.report.read_report", forbidden)

    block = train_from_frame(make_frame(ROWS), expected_delivered=ROWS, expected_late=LATE_ROWS)

    assert block.target == TARGET


def test_the_model_module_does_not_name_the_report_file():
    source = Path(model_module.__file__).read_text(encoding="utf-8")

    assert "analysis.json" not in source
    assert "write_report" not in source
    assert "read_report" not in source
    assert not hasattr(model_module, "write_report")
    assert not hasattr(model_module, "read_report")


# --- BR2.9: làm tròn 4 chữ số, ngưỡng vẫn trong (0, 1) --------------------------------------


def test_the_block_rounds_every_number_to_four_digits():
    block = build_model_block(
        split={"train_n": 4, "test_n": 4},
        auc=0.81234567,
        threshold=0.55,
        precision=0.666666,
        recall=0.3333333,
        flagged=2,
    )

    assert block.auc == 0.8123
    assert block.precision == 0.6667
    assert block.recall == 0.3333
    assert block.threshold == 0.55
    for value in (block.auc, block.threshold, block.precision, block.recall):
        assert round(value, 4) == value
    assert 0 < block.threshold < 1


def test_a_threshold_that_rounds_to_one_or_zero_is_an_error():
    with pytest.raises(ModelError):
        build_model_block(
            split={"test_n": 4},
            auc=0.8,
            threshold=0.99996,
            precision=1.0,
            recall=1.0,
            flagged=1,
        )

    with pytest.raises(ModelError):
        build_model_block(
            split={"test_n": 4},
            auc=0.8,
            threshold=0.00004,
            precision=1.0,
            recall=1.0,
            flagged=1,
        )


def test_the_block_carries_exactly_the_eleven_contract_fields():
    block = train_from_frame(make_frame(ROWS), expected_delivered=ROWS, expected_late=LATE_ROWS)
    payload = block.to_dict()

    assert set(payload) == {
        "target",
        "split",
        "auc",
        "threshold",
        "precision",
        "recall",
        "counts",
        "unit",
        "auc_tree",
        "baseline_auc",
        "beats_baseline",
    }
    assert payload["target"] == TARGET
    assert payload["unit"] == "dòng hàng"
    assert len(payload["counts"]) == 9
    assert set(payload["split"]) == {
        "train_start",
        "train_end",
        "test_start",
        "test_end",
        "train_n",
        "test_n",
    }
    assert 0 <= payload["auc"] <= 1
    assert 0 < payload["threshold"] < 1
    assert 0 <= payload["precision"] <= 1
    assert 0 <= payload["recall"] <= 1


def test_two_runs_on_the_same_frame_give_the_same_block():
    frame = make_frame(ROWS)

    first = train_from_frame(frame, expected_delivered=ROWS, expected_late=LATE_ROWS)
    second = train_from_frame(frame, expected_delivered=ROWS, expected_late=LATE_ROWS)

    assert first.to_dict() == second.to_dict()


# --- S2: phương thức đọc bảng huấn luyện trên DuckDB tạm ------------------------------------

ORDERS_VIEW = """
    CREATE OR REPLACE VIEW v_fact_orders AS
    SELECT 'o' || CAST(i AS VARCHAR) AS order_id,
           'c' || CAST(i AS VARCHAR) AS customer_id,
           CASE WHEN i <= 2 THEN '2018-03-31' ELSE '2018-04-01' END AS date_key,
           TRUE AS is_delivered,
           (i % 2) = 0 AS is_late,
           TRUE AS has_items,
           TRUE AS has_payment,
           'delivered' AS order_status,
           CAST(CASE WHEN i <= 2 THEN '2018-03-31 09:00' ELSE '2018-04-01 09:00' END AS TIMESTAMP)
               AS order_approved_at,
           CAST(CASE WHEN i <= 2 THEN '2018-04-02 09:00' ELSE '2018-04-03 09:00' END AS TIMESTAMP)
               AS order_delivered_carrier_date
    FROM range(1, 6) AS t(i)
"""

CUSTOMERS_VIEW = """
    CREATE OR REPLACE VIEW v_dim_customer AS
    SELECT 'c' || CAST(i AS VARCHAR) AS customer_id,
           'SP' AS state,
           'Sudeste' AS region
    FROM range(1, 5) AS t(i)
"""

DATES_VIEW = """
    CREATE OR REPLACE VIEW v_dim_date AS
    SELECT date_key,
           CAST(strftime('%m', CAST(date_key AS DATE)) AS INTEGER) AS month,
           CAST(strftime('%w', CAST(date_key AS DATE)) AS INTEGER) AS weekday
    FROM (SELECT '2018-03-31' AS date_key UNION SELECT '2018-04-01')
"""

ITEMS_VIEW = """
    CREATE OR REPLACE VIEW v_fact_order_items AS
    SELECT 'o1' AS order_id, CAST(1 AS INTEGER) AS order_item_id, 'c1' AS customer_id,
           '2018-03-31' AS date_key, 'SP' AS seller_state,
           CAST(10.0 AS DOUBLE) AS price,
           CAST(2.0 AS DOUBLE) AS freight_value, CAST(12.0 AS DOUBLE) AS item_total
    UNION ALL
    SELECT 'o1' AS order_id, CAST(2 AS INTEGER) AS order_item_id, 'c1' AS customer_id,
           '2018-03-31' AS date_key, 'RJ' AS seller_state,
           CAST(20.0 AS DOUBLE) AS price,
           CAST(3.0 AS DOUBLE) AS freight_value, CAST(23.0 AS DOUBLE) AS item_total
    UNION ALL
    SELECT 'o3' AS order_id, CAST(1 AS INTEGER) AS order_item_id, 'c3' AS customer_id,
           '2018-04-01' AS date_key, 'SP' AS seller_state,
           CAST(5.0 AS DOUBLE) AS price,
           CAST(1.0 AS DOUBLE) AS freight_value, CAST(6.0 AS DOUBLE) AS item_total
"""

PAYMENTS_VIEW = """
    CREATE OR REPLACE VIEW v_fact_payments AS
    SELECT 'o1' AS order_id, CAST(1 AS INTEGER) AS payment_sequential, 'credit_card' AS payment_type,
           CAST(2 AS INTEGER) AS payment_installments, CAST(35.0 AS DOUBLE) AS payment_value
    UNION ALL
    SELECT 'o1' AS order_id, CAST(2 AS INTEGER) AS payment_sequential, 'voucher' AS payment_type,
           CAST(5 AS INTEGER) AS payment_installments, CAST(0.0 AS DOUBLE) AS payment_value
"""


def build_views(config) -> None:
    conn = duckdb.connect(str(config.duckdb_path))
    try:
        for statement in (ORDERS_VIEW, CUSTOMERS_VIEW, DATES_VIEW, ITEMS_VIEW, PAYMENTS_VIEW):
            conn.execute(statement)
    finally:
        conn.close()


def test_the_training_frame_keeps_one_row_per_order_item_pair_on_a_temp_warehouse(config):
    build_views(config)

    frame, counts = AnalyticsService(config).training_frame()

    assert len(frame) == 3
    assert not frame[["order_id", "order_item_id"]].duplicated().any()
    assert frame["order_id"].duplicated().any()
    assert set(FEATURES) | {TARGET, "is_delivered", "date_key"} <= set(frame.columns)
    assert counts["cohort_rows"] == 3
    assert counts["cohort_orders"] == 2


def test_the_training_frame_takes_the_first_payment_type_and_the_largest_installment(config):
    build_views(config)

    frame, _ = AnalyticsService(config).training_frame()
    order_one = frame.loc[frame["order_id"] == "o1"]

    assert set(order_one["payment_type"]) == {"credit_card"}
    assert set(order_one["payment_installments"].astype(int)) == {5}
    assert set(order_one["item_count"].astype(int)) == {2}
    assert set(order_one["item_total"].astype(float)) == {35.0}
    assert set(order_one["item_price_max"].astype(float)) == {20.0}
    assert set(order_one["seller_state"]) == {"SP", "RJ"}


def test_an_order_without_items_has_no_row_at_row_grain(config):
    build_views(config)

    frame, counts = AnalyticsService(config).training_frame()

    assert "o2" not in set(frame["order_id"])
    assert "o4" not in set(frame["order_id"])
    assert counts["cohort_orders"] == 2


def test_the_training_sql_only_touches_declared_views():
    names = set(re.findall(r"v_[a-z_]+", TRAINING_FRAME_SQL))
    declared = {f"v_{table}" for table in VIEW_TABLES}

    assert names
    assert names <= declared


def test_the_production_entry_refuses_a_population_off_the_baseline(config):
    build_views(config)

    with pytest.raises(ModelError):
        train_model(config)


def test_the_training_frame_refuses_a_join_that_multiplies_rows(config):
    build_views(config)
    conn = duckdb.connect(str(config.duckdb_path))
    try:
        conn.execute(
            "CREATE OR REPLACE VIEW v_dim_customer AS "
            "SELECT 'c' || CAST(i AS VARCHAR) AS customer_id, 'SP' AS state, 'Sudeste' AS region "
            "FROM range(1, 5) AS t(i) UNION ALL "
            "SELECT 'c1' AS customer_id, 'RJ' AS state, 'Sudeste' AS region"
        )
    finally:
        conn.close()

    with pytest.raises(ValueError):
        AnalyticsService(config).training_frame()
