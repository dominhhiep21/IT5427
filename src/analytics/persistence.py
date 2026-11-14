"""Lưu và nạp mô hình bằng `pickle` kèm metadata (FR2.4, C2b, ADR-001).

Mọi I/O của tệp mô hình nằm ở đây, không ở `model.py`. Định dạng `pickle` gắn với phiên bản
thư viện đã sinh ra nó, nên đây KHÔNG phải định dạng trao đổi giữa các máy: máy khác sinh lại.
"""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.analytics.model import ModelError, train_classifier
from src.common.logging import NullLogger

MODEL_FILE_NAME = "logistic.pkl"
MODEL_META_FILE_NAME = "logistic.json"


@dataclass(frozen=True)
class FittedModel:
    """Trạng thái đã khớp của mô hình triển khai: đủ để chấm điểm lại mà không khớp lại."""

    estimator: object
    categories: dict
    scaler_means: list
    scaler_scales: list
    feature_names: list
    state_regions: dict = field(default_factory=dict)

    def to_payload(self) -> dict:
        return {
            "estimator": self.estimator,
            "categories": self.categories,
            "scaler_means": list(self.scaler_means),
            "scaler_scales": list(self.scaler_scales),
            "feature_names": list(self.feature_names),
            "state_regions": dict(self.state_regions),
        }


def save_model(
    model: FittedModel,
    models_dir: Path,
    logger=None,
) -> dict:
    """Ghi payload `pickle` và metadata JSON vào `models_dir`; trả metadata đã ghi."""

    logger = logger or NullLogger()
    models_dir = Path(models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    payload_path = models_dir / MODEL_FILE_NAME
    meta_path = models_dir / MODEL_META_FILE_NAME

    with payload_path.open("wb") as handle:
        pickle.dump(model.to_payload(), handle, protocol=pickle.HIGHEST_PROTOCOL)

    metadata = {
        "feature_names": list(model.feature_names),
        "library_versions": {"scikit-learn": _sklearn_version()},
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("model.saved", path=str(payload_path), features=len(model.feature_names))
    return metadata


def load_model(models_dir: Path) -> FittedModel | None:
    """Nạp mô hình đã lưu; vắng tệp trả `None`, tệp hỏng là `ModelError`."""

    models_dir = Path(models_dir)
    payload_path = models_dir / MODEL_FILE_NAME
    if not payload_path.exists():
        return None
    try:
        with payload_path.open("rb") as handle:
            payload = pickle.load(handle)
    except (OSError, pickle.UnpicklingError, EOFError, AttributeError, ValueError) as error:
        raise ModelError(f"Không nạp được tệp mô hình {payload_path}: {error}") from error
    try:
        return FittedModel(
            estimator=payload["estimator"],
            categories=payload["categories"],
            scaler_means=list(payload["scaler_means"]),
            scaler_scales=list(payload["scaler_scales"]),
            feature_names=list(payload["feature_names"]),
            state_regions=dict(payload.get("state_regions") or {}),
        )
    except (KeyError, TypeError) as error:
        raise ModelError(f"Tệp mô hình {payload_path} thiếu khoá bắt buộc: {error}") from error


def fit_persistable(
    train_matrix: pd.DataFrame,
    labels: pd.Series,
    categories: dict,
    scaler_means: list,
    scaler_scales: list,
    state_regions: dict | None = None,
) -> FittedModel:
    """Khớp mô hình triển khai và đóng gói kèm trạng thái tiền xử lý đã dùng."""

    estimator = train_classifier(train_matrix, labels)
    return FittedModel(
        estimator=estimator,
        categories=dict(categories),
        scaler_means=list(scaler_means),
        scaler_scales=list(scaler_scales),
        feature_names=list(train_matrix.columns),
        state_regions=dict(state_regions or {}),
    )


def fit_from_config(config, logger=None) -> FittedModel:
    """Huấn luyện mô hình triển khai trên mart thật và đóng gói kèm trạng thái tiền xử lý."""

    from src.analytics.model import (
        NUMERIC_FEATURES,
        AnalyticsService,
        _categories,
        build_feature_frame,
        delivered_population,
        encode_features,
        split_frame,
        validate_cohort_counts,
    )

    frame, counts = AnalyticsService(config).training_frame()
    # BR2.1: bốn bộ đếm phải khớp baseline đã chốt, không so với chính lần đọc này.
    validate_cohort_counts(counts)
    population = delivered_population(frame)
    train_rows, _ = split_frame(population)
    train_features = build_feature_frame(train_rows)
    train_matrix, _ = encode_features(train_features, train_features)

    scaler = StandardScaler().fit(train_features[list(NUMERIC_FEATURES)].astype("float64"))
    regions = (
        population.dropna(subset=["customer_state", "customer_region"])
        .groupby("customer_state")["customer_region"]
        .agg(lambda values: values.mode().iat[0])
        .to_dict()
    )
    return fit_persistable(
        train_matrix,
        train_rows["is_late"].fillna(value=False).astype(bool),
        categories=_categories(train_features),
        scaler_means=list(scaler.mean_),
        scaler_scales=list(scaler.scale_),
        state_regions=regions,
    )


def _sklearn_version() -> str:
    import sklearn

    return sklearn.__version__
