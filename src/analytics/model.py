"""Đặc trưng, chia tập, huấn luyện và ngưỡng cảnh báo của khối mô hình đơn trễ (BR2.1–BR2.9)."""

from __future__ import annotations

import warnings
from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from src.analytics.report import ModelBlock
from src.analytics.service import AnalyticsService
from src.common.exceptions import PipelineError
from src.common.logging import NullLogger

TARGET = "is_late"
SPLIT_DATE = "2018-04-01"
# Baseline quần thể ở grain DÒNG HÀNG: 110.195 dòng, 96.476 đơn, 8.713 dòng trễ (FR1.2).
EXPECTED_DELIVERED = 110_195
EXPECTED_LATE = 8_713
# Hai bộ đếm còn lại của BR2.1, cũng đo trên mart thật: 96.476 đơn và 2 đơn thiếu carrier date.
EXPECTED_COHORT_ORDERS = 96_476
EXPECTED_EXCLUDED_CARRIER = 2
MODEL_DIGITS = 4
AUC_TARGET = 0.70
# Mốc sàn chống thoái hoá (NFR5); U3 viết test `slow` so mốc này trên báo cáo thật.
MODEL_AUC_FLOOR = 0.55
UNIT_LABEL = "dòng hàng"
THRESHOLD_METHOD = "max_f1_on_test_grid005"
THRESHOLD_GRID = tuple(round(0.05 * step, 2) for step in range(1, 20))
RANDOM_STATE = 42
MAX_ITER = 1000
BALANCED = "balanced"
UNKNOWN = "unknown"

MODEL_TRAINED_EVENT = "model.trained"

# Năm cột phân loại mã hoá one-hot, bốn cột số chuẩn hoá, hai cờ đã có trong mart (TS-7, BR2.3).
CATEGORICAL_FEATURES = (
    "payment_type",
    "customer_state",
    "customer_region",
    "purchase_month",
    "purchase_weekday",
    "seller_state",
)
NUMERIC_FEATURES = (
    "item_count",
    "item_total",
    "item_price_max",
    "payment_installments",
    "handling_days",
    "approval_days",
)
FLAG_FEATURES = ("has_items", "has_payment")
FEATURES = (
    "item_count",
    "item_total",
    "item_price_max",
    "payment_type",
    "payment_installments",
    "customer_state",
    "customer_region",
    "purchase_month",
    "purchase_weekday",
    "has_items",
    "has_payment",
    "seller_state",
    "handling_days",
    "approval_days",
)
# Mọi cột chỉ biết được sau khi đơn đã giao, cùng họ `is_late` và `has_review` (SD-1, SD-1b).
FORBIDDEN_COLUMNS = (
    "order_delivered_customer_date",
    "order_delivered_carrier_date",
    "order_approved_at",
    "delivery_days",
    "is_late",
    "late_days",
    "review_score",
    "review_comment_title",
    "review_comment_message",
    "is_delivered",
    "has_review",
)


class ModelError(PipelineError):
    """Bước mô hình không dựng được khối hợp lệ; tầng `stats` dừng và không ghi tệp (BR2.1–BR2.9)."""


@dataclass(frozen=True)
class ThresholdPoint:
    """Một điểm trên đường cong precision/recall; chỉ dùng nội bộ để chọn ngưỡng (BR2.5)."""

    threshold: float
    precision: float
    recall: float
    f1: float


def validate_features(features: tuple[str, ...] = FEATURES) -> None:
    """BR2.3 — danh sách đặc trưng là hằng số có tên VÀ đúng thứ tự; không cột nào chỉ có sau khi giao."""

    if tuple(features) != FEATURES:
        raise ModelError("Danh sách đặc trưng không khớp hợp đồng 14 cột (tên hoặc thứ tự) — BR2.3.")
    forbidden = sorted(set(features) & set(FORBIDDEN_COLUMNS))
    if forbidden:
        raise ModelError(
            f"Danh sách đặc trưng còn cột chỉ có sau khi giao: {', '.join(forbidden)}; đây là rò rỉ nhãn (BR2.3)."
        )
    if len(set(features)) != len(features):
        raise ModelError("Danh sách đặc trưng có tên lặp lại (BR2.3).")
    if len(features) != len(FEATURES):
        raise ModelError(
            f"Danh sách đặc trưng phải có đúng {len(FEATURES)} cột, đang có {len(features)} (BR2.3)."
        )


def validate_cohort_counts(counts: Mapping[str, int] | None) -> None:
    """BR2.1 — bốn bộ đếm quần thể phải khớp baseline đã chốt; lệch là ModelError."""

    if counts is None:
        return
    expected = {
        "cohort_rows": EXPECTED_DELIVERED,
        "cohort_orders": EXPECTED_COHORT_ORDERS,
        "late_rows": EXPECTED_LATE,
        "excluded_missing_carrier": EXPECTED_EXCLUDED_CARRIER,
    }
    missing = [key for key in expected if key not in counts]
    if missing:
        raise ModelError(f"Bộ đếm quần thể thiếu khoá {', '.join(missing)} (BR2.1).")
    wrong = [
        f"{key}={counts[key]} (phải {value})" for key, value in expected.items() if int(counts[key]) != value
    ]
    if wrong:
        raise ModelError(f"Bộ đếm quần thể lệch baseline: {'; '.join(wrong)} (BR2.1).")


def delivered_population(
    frame: pd.DataFrame,
    expected_delivered: int = EXPECTED_DELIVERED,
    expected_late: int = EXPECTED_LATE,
) -> pd.DataFrame:
    """BR2.1 — chỉ đơn đã giao, lọc tường minh, rồi kiểm cỡ mẫu và số đơn trễ."""

    missing = [column for column in ("is_delivered", TARGET) if column not in frame.columns]
    if missing:
        raise ModelError(f"Khung dữ liệu thiếu cột {', '.join(missing)} nên không lọc được quần thể (BR2.1).")
    delivered = frame[frame["is_delivered"].fillna(value=False).astype(bool)]
    if len(delivered) != expected_delivered:
        raise ModelError(f"Quần thể đã giao có {len(delivered)} đơn, không phải {expected_delivered} (BR2.1).")
    late = int(delivered[TARGET].fillna(value=False).astype(bool).sum())
    if late != expected_late:
        raise ModelError(f"Quần thể đã giao có {late} đơn trễ, không phải {expected_late} (BR2.1).")
    return delivered


def measure_state_baseline(
    frame: pd.DataFrame,
    *,
    label_column: str = TARGET,
    feature_column: str = "customer_state",
    cut_date: str = SPLIT_DATE,
    random_state: int = RANDOM_STATE,
) -> float:
    """BR1.4, BR1.5, FR1.3 — AUC của baseline MỘT đặc trưng trên đúng tập kiểm tra; hàm thuần."""

    if cut_date != SPLIT_DATE:
        raise ModelError(f"Mốc cắt baseline là {cut_date}, khác mốc của mô hình {SPLIT_DATE} (BR1.4).")
    for column in (label_column, feature_column, "date_key"):
        if column not in frame.columns:
            raise ModelError(f"Khung dữ liệu thiếu cột {column} (BR1.4).")

    train, test = split_frame(frame, cut_date)
    labels = test[label_column].fillna(value=False).astype(bool)
    class_count = int(labels.nunique())
    if len(test) == 0 or class_count < 2:
        raise ModelError(
            f"Tập kiểm tra có {len(test)} dòng và {class_count} lớp nhãn; AUC không xác định (BR1.5)."
        )

    encoder = pd.get_dummies(
        train[feature_column].astype("object").where(train[feature_column].notna(), UNKNOWN),
        prefix=feature_column,
        dtype="float64",
    )
    encoded_train = encoder
    encoded_test = pd.get_dummies(
        test[feature_column].astype("object").where(test[feature_column].notna(), UNKNOWN),
        prefix=feature_column,
        dtype="float64",
    ).reindex(columns=encoder.columns, fill_value=0.0)

    model = LogisticRegression(max_iter=MAX_ITER, random_state=random_state, class_weight=BALANCED)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model.fit(encoded_train, train[label_column].fillna(value=False).astype(bool))
    scores = model.predict_proba(encoded_test)[:, 1]
    return float(roc_auc_score(labels, scores))


def build_feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """BR2.3, TS-8 — dựng đúng 11 cột đặc trưng; thiếu thì điền, không bỏ dòng nào."""

    validate_features()
    missing = [column for column in FEATURES if column not in frame.columns]
    if missing:
        raise ModelError(f"Khung dữ liệu thiếu cột đặc trưng: {', '.join(missing)} (BR2.3).")
    features = pd.DataFrame(index=frame.index)
    for column in NUMERIC_FEATURES:
        features[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0).astype("float64")
    for column in FLAG_FEATURES:
        features[column] = frame[column].fillna(value=False).astype(bool).astype("float64")
    for column in CATEGORICAL_FEATURES:
        series = frame[column].astype("object")
        features[column] = series.where(series.notna(), UNKNOWN).astype(str)
    return features[list(FEATURES)]


def split_frame(
    frame: pd.DataFrame,
    split_date: str = SPLIT_DATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """BR2.2 — chia tập theo `order_id`: mọi dòng hàng của một đơn nằm cùng một phía."""

    dates = pd.to_datetime(frame["date_key"], format="%Y-%m-%d", errors="coerce")
    if bool(dates.isna().any()):
        raise ModelError("Có đơn không có ngày đặt hợp lệ nên không chia được tập (BR2.2).")
    cut = pd.Timestamp(split_date)

    if "order_id" not in frame.columns:
        # Khung không có khoá đơn (ví dụ baseline một đặc trưng của U1): chia theo dòng,
        # vì không có gì để rò rỉ giữa hai tập.
        train = frame[dates < cut]
        test = frame[dates >= cut]
        if train.empty or test.empty:
            raise ModelError(
                f"Mốc cắt {split_date} để lại tập rỗng: {len(train)} dòng huấn luyện, "
                f"{len(test)} dòng kiểm tra (BR2.2)."
            )
        return train, test

    order_dates = (
        pd.DataFrame({"order_id": frame["order_id"], "date": dates})
        .groupby("order_id", as_index=False)["date"]
        .min()
    )
    train_orders = set(order_dates.loc[order_dates["date"] < cut, "order_id"])
    test_orders = set(order_dates.loc[order_dates["date"] >= cut, "order_id"])
    if train_orders & test_orders:
        raise ModelError("Có đơn nằm ở cả hai tập: phép chia theo order_id đã hỏng (BR2.2).")

    train = frame[frame["order_id"].isin(train_orders)]
    test = frame[frame["order_id"].isin(test_orders)]
    if train.empty or test.empty:
        raise ModelError(
            f"Mốc cắt {split_date} để lại tập rỗng: {len(train)} dòng huấn luyện, "
            f"{len(test)} dòng kiểm tra (BR2.2)."
        )
    return train, test


def split_summary(
    train: pd.DataFrame,
    test: pd.DataFrame,
    expected_total: int = EXPECTED_DELIVERED,
) -> dict:
    """BR2.2 — mốc thời gian và cỡ mẫu hai tập; thứ tự sai hoặc tổng lệch thì dừng."""

    train_start, train_end = _date_bounds(train)
    test_start, test_end = _date_bounds(test)
    if not train_end < test_start:
        raise ModelError(f"Tập huấn luyện không đứng trước tập kiểm tra: {train_end} rồi {test_start} (BR2.2).")
    if len(train) + len(test) != expected_total:
        raise ModelError(f"Hai tập cộng lại {len(train) + len(test)} đơn, không phải {expected_total} (BR2.2).")
    return {
        "train_start": train_start,
        "train_end": train_end,
        "test_start": test_start,
        "test_end": test_end,
        "train_n": len(train),
        "test_n": len(test),
    }


def encode_features(
    train_features: pd.DataFrame,
    test_features: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """TS-6, TS-9 — one-hot và chuẩn hoá bằng tham số khớp chỉ trên tập huấn luyện."""

    categories = _categories(train_features)
    numeric = list(NUMERIC_FEATURES)
    scaler = StandardScaler().fit(train_features[numeric].astype("float64"))
    matrices = []
    for features in (train_features, test_features):
        scaled = pd.DataFrame(
            scaler.transform(features[numeric].astype("float64")),
            columns=numeric,
            index=features.index,
        )
        flags = features[list(FLAG_FEATURES)].astype("float64")
        matrices.append(pd.concat([scaled, flags, _one_hot(features, categories)], axis=1))
    return matrices[0], matrices[1]


def build_estimator() -> LogisticRegression:
    """BR2.4 — bộ phân loại logistic, trọng số lớp cân bằng, `random_state` cố định."""

    return LogisticRegression(class_weight=BALANCED, max_iter=MAX_ITER, random_state=RANDOM_STATE)


def train_classifier(train_matrix: pd.DataFrame, labels: pd.Series) -> LogisticRegression:
    """BR2.4, TS-9 — huấn luyện và biến cảnh báo không hội tụ thành lỗi, không thành ghi chú."""

    estimator = build_estimator()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        estimator.fit(train_matrix, labels)
    limit = estimator.get_params().get("max_iter")
    if any(issubclass(item.category, ConvergenceWarning) for item in caught):
        raise ModelError(f"Bộ phân loại không hội tụ sau {limit} vòng lặp nên kết quả không dùng được (TS-9).")
    return estimator


def choose_threshold(
    labels: pd.Series,
    scores: pd.Series,
    grid: tuple[float, ...] = THRESHOLD_GRID,
) -> ThresholdPoint:
    """BR2.5 — ngưỡng có F1 lớn nhất trên lưới 19 điểm; hoà thì chọn ngưỡng cao hơn."""

    positive = int(labels.sum())
    if positive == 0 or positive == len(labels):
        raise ModelError("Tập kiểm tra chỉ có một lớp nên không chọn được ngưỡng (BR2.5).")
    best: ThresholdPoint | None = None
    for threshold in grid:
        flagged = scores >= threshold
        flagged_count = int(flagged.sum())
        true_positive = int((flagged & labels).sum())
        precision = true_positive / flagged_count if flagged_count else 0.0
        recall = true_positive / positive
        denominator = precision + recall
        f1 = 2 * precision * recall / denominator if denominator else 0.0
        if best is None or f1 >= best.f1:
            best = ThresholdPoint(threshold=threshold, precision=precision, recall=recall, f1=f1)
    return best


def auc_below_target(auc: float) -> bool:
    """BR2.6 — AUC dưới 0,70 được đánh dấu là không đạt, không ẩn đi."""

    return float(auc) < AUC_TARGET


def validate_counts(counts: dict, test_n: int) -> None:
    """BR2.7 — `flagged + not_flagged` phải bằng `total`, và `total` phải bằng cỡ mẫu tập kiểm tra."""

    if int(counts["flagged"]) + int(counts["not_flagged"]) != int(counts["total"]):
        raise ModelError(
            f"Ba con số đếm lệch nhau: {counts['flagged']} + {counts['not_flagged']} "
            f"≠ {counts['total']} (BR2.7)."
        )
    if int(counts["total"]) != int(test_n):
        raise ModelError(f"Số đếm trên tập kiểm tra là {counts['total']}, cỡ mẫu là {test_n} (BR2.7).")


def beats_floor(auc: float, baseline_auc: float, floor: float = MODEL_AUC_FLOOR) -> bool:
    """NFR5 — mốc sàn không bao giờ thấp hơn baseline đo lại; hàm thuần, hai nhánh."""

    if not 0 < float(floor) < 1:
        raise ModelError(f"Mốc sàn {floor} phải nằm trong (0, 1) (NFR5).")
    return float(auc) >= max(float(floor), float(baseline_auc))


def build_model_block(
    split: dict,
    auc: float,
    threshold: float,
    precision: float,
    recall: float,
    flagged: int,
    *,
    auc_tree: float = 0.0,
    baseline_auc: float = 0.0,
    cohort_counts: dict | None = None,
) -> ModelBlock:
    """BR2.5–BR2.7 — đếm khớp trước, làm tròn 4 chữ số, hai cờ tính trên giá trị đã làm tròn."""

    total = int(split["test_n"])
    auc_value = _rounded(auc)
    baseline_value = _rounded(baseline_auc)
    cohorts = cohort_counts or {
        "cohort_rows": 0,
        "cohort_orders": 0,
        "late_rows": 0,
        "excluded_missing_carrier": 0,
    }
    counts = {
        "flagged": int(flagged),
        "not_flagged": total - int(flagged),
        "total": total,
        "threshold_method": THRESHOLD_METHOD,
        # Hai cờ tính trên giá trị đã làm tròn để tệp không mâu thuẫn với chính nó (BR2.6).
        "auc_below_target": auc_below_target(auc_value),
        "cohort_rows": int(cohorts["cohort_rows"]),
        "cohort_orders": int(cohorts["cohort_orders"]),
        "late_rows": int(cohorts["late_rows"]),
        "excluded_missing_carrier": int(cohorts["excluded_missing_carrier"]),
    }
    validate_counts(counts, total)
    threshold_value = _rounded(threshold)
    if not 0 < threshold_value < 1:
        raise ModelError(f"Ngưỡng sau khi làm tròn là {threshold_value}, phải nằm trong (0, 1) (BR2.9).")
    return ModelBlock(
        target=TARGET,
        split=dict(split),
        auc=auc_value,
        threshold=threshold_value,
        precision=_rounded(precision),
        recall=_rounded(recall),
        counts=counts,
        unit=UNIT_LABEL,
        auc_tree=_rounded(auc_tree),
        baseline_auc=baseline_value,
        beats_baseline=auc_value > baseline_value,
    )


def train_from_frame(
    frame: pd.DataFrame,
    expected_delivered: int = EXPECTED_DELIVERED,
    expected_late: int = EXPECTED_LATE,
    logger=None,
    cohort_counts: dict | None = None,
) -> ModelBlock:
    """Huấn luyện trên một khung grain dòng hàng có sẵn và trả khối mô hình (BR2.1–BR2.9).

    `cohort_counts` là bốn bộ đếm do `training_frame()` trả kèm; chặng C nối chúng vào
    `counts` của báo cáo v3. Ở chặng A chúng chỉ đi qua, chưa vào khối.
    """

    logger = logger or NullLogger()
    validate_features()
    population = delivered_population(frame, expected_delivered, expected_late)
    train_rows, test_rows = split_frame(population)
    split = split_summary(train_rows, test_rows, expected_total=expected_delivered)
    train_matrix, test_matrix = encode_features(
        build_feature_frame(train_rows),
        build_feature_frame(test_rows),
    )
    train_labels = train_rows[TARGET].fillna(value=False).astype(bool)
    test_labels = test_rows[TARGET].fillna(value=False).astype(bool)
    estimator = train_classifier(train_matrix, train_labels)
    scores = pd.Series(estimator.predict_proba(test_matrix)[:, 1], index=test_rows.index)
    auc = float(roc_auc_score(test_labels, scores))
    point = choose_threshold(test_labels, scores)
    flagged = int((scores >= point.threshold).sum())

    tree = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
    tree.fit(train_matrix, train_labels)
    tree_scores = tree.predict_proba(test_matrix)[:, 1]
    auc_tree = float(roc_auc_score(test_labels, tree_scores))

    baseline_auc = measure_state_baseline(population)

    block = build_model_block(
        split,
        auc,
        point.threshold,
        point.precision,
        point.recall,
        flagged,
        auc_tree=auc_tree,
        baseline_auc=baseline_auc,
        cohort_counts=cohort_counts,
    )
    logger.info(
        MODEL_TRAINED_EVENT,
        auc=block.auc,
        threshold=block.threshold,
        train_n=split["train_n"],
        test_n=split["test_n"],
        auc_below_target=block.counts["auc_below_target"],
    )
    return block


def train_model(config, logger=None) -> ModelBlock:
    """Đọc khung grain dòng hàng kèm bộ đếm quần thể rồi trả khối mô hình (BR2.1, BR2.8)."""

    frame, counts = AnalyticsService(config).training_frame()
    validate_cohort_counts(counts)
    return train_from_frame(frame, logger=logger, cohort_counts=counts)


def _categories(train_features: pd.DataFrame) -> dict[str, list[str]]:
    return {
        column: sorted({UNKNOWN} | {str(value) for value in train_features[column].unique()})
        for column in CATEGORICAL_FEATURES
    }


@dataclass(frozen=True)
class PredictionContribution:
    """Một trường đóng góp vào log-odds; mọi cột one-hot của trường đã được gộp."""

    field: str
    sign: str
    log_odds: float


@dataclass(frozen=True)
class PredictionOutcome:
    """Kết quả chấm một dòng hàng: xác suất, kết luận theo ngưỡng, ba đóng góp lớn nhất."""

    probability: float
    verdict: str
    contributions: tuple[PredictionContribution, ...]


INPUT_KEYS = (
    "seller_state",
    "customer_state",
    "order_date",
    "item_price",
    "handling_days",
    "approval_days",
    "item_count",
    "payment_type",
    "installments",
    "has_items",
    "has_payment",
)


# Miền hợp lệ của 11 giá trị nhập (BR2.11 bước 2: thiếu, sai kiểu, hay NGOÀI MIỀN đều là ModelError).
MAX_DAYS = 365
STATE_CODE_LENGTH = 2


def _numeric_input(item: Mapping[str, object], key: str, minimum: float, maximum: float | None = None) -> float:
    """Đọc một ô số của biểu mẫu và kiểm miền; mọi lỗi đều nêu tên trường (BR2.11)."""

    try:
        value = float(item[key])
    except (TypeError, ValueError) as error:
        raise ModelError(f"{key} không phải số: {error} (BR2.11).") from error
    if value != value or value in (float("inf"), float("-inf")):
        raise ModelError(f"{key} không phải số hữu hạn (BR2.11).")
    if value < minimum:
        raise ModelError(f"{key} ngoài miền: phải >= {minimum}, nhận {value} (BR2.11).")
    if maximum is not None and value > maximum:
        raise ModelError(f"{key} ngoài miền: phải <= {maximum}, nhận {value} (BR2.11).")
    return value


def _state_code(item: Mapping[str, object], key: str) -> str:
    """Đọc một mã bang hai chữ cái; sai dạng là ModelError nêu tên trường (BR2.11)."""

    value = str(item[key])
    if len(value) != STATE_CODE_LENGTH or not value.isascii() or not value.isalpha():
        raise ModelError(f"{key} ngoài miền: cần mã bang hai chữ cái, nhận {value!r} (BR2.11).")
    return value.upper()


def _serve_features(item: Mapping[str, object], state_regions: Mapping[str, str] | None = None) -> pd.DataFrame:
    """Dựng một dòng 14 đặc trưng từ 11 giá trị nhập của biểu mẫu (C3, BR2.11)."""

    missing = [key for key in INPUT_KEYS if key not in item or item[key] in (None, "")]
    if missing:
        raise ModelError(f"Thiếu giá trị nhập: {', '.join(missing)} (BR2.11).")
    try:
        moment = pd.Timestamp(str(item["order_date"]))
    except (TypeError, ValueError) as error:
        raise ModelError(f"order_date không đọc được: {error} (BR2.11).") from error
    price = _numeric_input(item, "item_price", 0.0)
    item_count = _numeric_input(item, "item_count", 1.0)
    handling_days = _numeric_input(item, "handling_days", 0.0, MAX_DAYS)
    approval_days = _numeric_input(item, "approval_days", 0.0, MAX_DAYS)
    installments = _numeric_input(item, "installments", 1.0)
    customer_state = _state_code(item, "customer_state")
    seller_state = _state_code(item, "seller_state")
    region = (state_regions or {}).get(customer_state, UNKNOWN)
    return pd.DataFrame(
        [
            {
                "item_count": item_count,
                # Một dòng nhập là một món: tổng đơn = giá × số món, đúng hợp đồng serve_inputs.
                "item_total": price * item_count,
                "item_price_max": price,
                "payment_type": str(item["payment_type"]),
                "payment_installments": installments,
                "customer_state": customer_state,
                "customer_region": region,
                "purchase_month": str(moment.month),
                "purchase_weekday": str(moment.weekday()),
                "has_items": bool(item["has_items"]),
                "has_payment": bool(item["has_payment"]),
                "seller_state": seller_state,
                "handling_days": handling_days,
                "approval_days": approval_days,
            }
        ]
    )


def score_item(
    model: object,
    item: Mapping[str, object],
    *,
    threshold: float,
) -> PredictionOutcome:
    """BR2.10, BR2.11 — chấm một dòng hàng từ trạng thái đã lưu; hàm thuần, tất định."""

    features = _serve_features(item, getattr(model, "state_regions", None))
    numeric = features[list(NUMERIC_FEATURES)].astype("float64").to_numpy()
    means = pd.Series(model.scaler_means, index=list(NUMERIC_FEATURES), dtype="float64")
    scales = pd.Series(model.scaler_scales, index=list(NUMERIC_FEATURES), dtype="float64")
    scaled = pd.DataFrame((numeric - means.to_numpy()) / scales.to_numpy(), columns=list(NUMERIC_FEATURES))
    flags = features[list(FLAG_FEATURES)].astype("float64")
    one_hot = _one_hot(features, model.categories)
    matrix = pd.concat([scaled, flags, one_hot], axis=1)

    if list(matrix.columns) != list(model.feature_names):
        raise ModelError("Ma trận lúc chấm điểm lệch danh sách cột đã huấn luyện (BR2.11).")

    coefficients = pd.Series(model.estimator.coef_[0], index=list(matrix.columns))
    probability = float(model.estimator.predict_proba(matrix)[0, 1])
    raw = coefficients * matrix.iloc[0]

    totals: dict[str, float] = {column: float(raw[column]) for column in NUMERIC_FEATURES}
    totals.update({column: float(raw[column]) for column in FLAG_FEATURES})
    for column, value in raw.items():
        field = column.split("=", 1)[0] if "=" in column else column
        if field in NUMERIC_FEATURES or field in FLAG_FEATURES:
            continue
        totals[field] = totals.get(field, 0.0) + float(value)

    ranked = sorted(totals.items(), key=lambda pair: abs(pair[1]), reverse=True)[:3]
    contributions = tuple(
        PredictionContribution(
            field=field,
            sign="positive" if value >= 0 else "negative",
            log_odds=round(value, MODEL_DIGITS),
        )
        for field, value in ranked
    )
    verdict = "at_or_above_threshold" if probability >= float(threshold) else "below_threshold"
    return PredictionOutcome(probability=probability, verdict=verdict, contributions=contributions)


def _one_hot(features: pd.DataFrame, categories: dict[str, list[str]]) -> pd.DataFrame:
    blocks = []
    for column in CATEGORICAL_FEATURES:
        values = features[column].astype(str)
        blocks.append(
            pd.DataFrame(
                {f"{column}={value}": (values == value).astype("float64") for value in categories[column]},
                index=features.index,
            )
        )
    return pd.concat(blocks, axis=1)


def _date_bounds(frame: pd.DataFrame) -> tuple[str, str]:
    dates = pd.to_datetime(frame["date_key"])
    return dates.min().strftime("%Y-%m-%d"), dates.max().strftime("%Y-%m-%d")


def _rounded(value: float) -> float:
    return round(float(value), MODEL_DIGITS)
