"""Lưu và nạp mô hình: vòng ghi-đọc, vắng tệp, tệp hỏng (FR2.4, C2b)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics.model import ModelError
from src.analytics.persistence import (
    MODEL_FILE_NAME,
    FittedModel,
    fit_persistable,
    load_model,
    save_model,
)


def _matrix(rows: int = 20) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "item_count": [1.0 + i % 4 for i in range(rows)],
            "item_total": [10.0 + i for i in range(rows)],
            "has_items": [1.0] * rows,
            "seller_state=SP": [1.0 if i % 2 else 0.0 for i in range(rows)],
            "seller_state=RJ": [0.0 if i % 2 else 1.0 for i in range(rows)],
        }
    )


def _labels(rows: int = 20) -> pd.Series:
    return pd.Series([bool(i % 3) for i in range(rows)])


def _fitted() -> FittedModel:
    return fit_persistable(
        _matrix(),
        _labels(),
        categories={"seller_state": ["RJ", "SP", "unknown"]},
        scaler_means=[1.0, 2.0],
        scaler_scales=[0.5, 0.5],
        state_regions={"SP": "Sudeste"},
    )


def test_round_trip_keeps_feature_names_and_preprocessing(tmp_path) -> None:  # noqa: ANN001
    model = _fitted()
    save_model(model, tmp_path)

    loaded = load_model(tmp_path)
    assert loaded is not None
    assert loaded.feature_names == model.feature_names
    assert loaded.categories == model.categories
    assert loaded.scaler_means == model.scaler_means
    assert loaded.scaler_scales == model.scaler_scales


def test_metadata_carries_versions_and_timestamp(tmp_path) -> None:  # noqa: ANN001
    metadata = save_model(_fitted(), tmp_path)
    assert set(metadata) == {"feature_names", "library_versions", "trained_at"}
    assert "scikit-learn" in metadata["library_versions"]


def test_absent_file_returns_none(tmp_path) -> None:  # noqa: ANN001
    assert load_model(tmp_path) is None


def test_corrupt_payload_is_a_model_error(tmp_path) -> None:  # noqa: ANN001
    (tmp_path / MODEL_FILE_NAME).write_bytes(b"khong phai pickle")
    with pytest.raises(ModelError):
        load_model(tmp_path)


def test_payload_missing_a_key_is_a_model_error(tmp_path) -> None:  # noqa: ANN001
    import pickle

    (tmp_path / MODEL_FILE_NAME).write_bytes(pickle.dumps({"estimator": None}))
    with pytest.raises(ModelError):
        load_model(tmp_path)


def test_feature_names_are_the_expanded_matrix_columns(tmp_path) -> None:  # noqa: ANN001
    model = _fitted()
    assert model.feature_names == list(_matrix().columns)
    assert len(model.feature_names) >= 5


def test_save_creates_the_directory(tmp_path) -> None:  # noqa: ANN001
    target = tmp_path / "models"
    save_model(_fitted(), target)
    assert (target / MODEL_FILE_NAME).exists()


def test_round_trip_keeps_the_state_region_map(tmp_path) -> None:  # noqa: ANN001
    save_model(_fitted(), tmp_path)
    loaded = load_model(tmp_path)
    assert loaded is not None
    assert loaded.state_regions == {"SP": "Sudeste"}
