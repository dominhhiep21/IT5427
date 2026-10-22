"""Configuration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.common.exceptions import ConfigurationError
from src.config import load_config


def test_load_config_creates_directories(config):
    assert config.raw_csv_dir.exists()
    assert config.raw_dir.exists()
    assert config.cleaned_dir.exists()
    assert config.reports_dir.exists()
    assert config.logs_dir.exists()
    assert config.temp_dir.exists()
    assert config.parquet_compression == "snappy"
    assert config.iqr_multiplier == 1.5


def test_load_config_missing_dataset(tmp_path: Path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "paths:\n  raw_csv_dir: does-not-exist\n", encoding="utf-8"
    )
    with pytest.raises(ConfigurationError):
        load_config(config_path)
