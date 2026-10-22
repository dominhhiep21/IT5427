"""Atomic writer tests."""

from __future__ import annotations

import pandas as pd

from src.common.io import read_parquet


def test_atomic_writer_round_trip(config, run, writer):
    frame = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    target = config.cleaned_dir / "sample.parquet"
    writer.write_parquet(frame, target)
    loaded = read_parquet(target)
    assert len(loaded) == 2
    assert list(loaded.columns) == ["a", "b"]

    writer.write_json({"ok": True}, config.reports_dir / "sample.json")
    assert (config.reports_dir / "sample.json").exists()
    writer.cleanup()
    assert not run.temp_dir.exists()
