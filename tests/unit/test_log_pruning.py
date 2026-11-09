"""Unit tests for the `logs/` retention rule (keep the 10 newest files)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from src.common.logging import JsonLogger, new_run_context, prune_logs


def _seed_logs(tmp_path: Path, count: int) -> list[Path]:
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(exist_ok=True)
    paths = []
    for index in range(count):
        path = logs_dir / f"run-{index:02d}.jsonl"
        path.write_text("{}\n", encoding="utf-8")
        stamp = path.stat().st_mtime + index
        os.utime(path, (stamp, stamp))
        paths.append(path)
    return paths


def test_prune_keeps_the_newest_ten(tmp_path: Path):
    paths = _seed_logs(tmp_path, 14)
    run = new_run_context("test", tmp_path / "logs", tmp_path / "tmp")
    logger = JsonLogger(run, console=False)

    deleted = prune_logs(tmp_path / "logs", logger, keep=10)

    remaining = sorted((tmp_path / "logs").glob("*.jsonl"))
    assert deleted == 4
    assert len(remaining) == 11  # 10 kept files plus this run's own log
    assert all(path.exists() for path in paths[-10:])


def test_prune_does_nothing_below_the_limit(tmp_path: Path):
    _seed_logs(tmp_path, 3)
    run = new_run_context("test", tmp_path / "logs", tmp_path / "tmp")
    logger = JsonLogger(run, console=False)

    assert prune_logs(tmp_path / "logs", logger, keep=10) == 0


def test_prune_never_deletes_the_current_log(tmp_path: Path):
    """The current run's log survives even when it is the oldest file on disk."""

    _seed_logs(tmp_path, 12)
    run = new_run_context("test", tmp_path / "logs", tmp_path / "tmp")
    logger = JsonLogger(run, console=False)
    logger.info("integration.load.started", file="x.csv", entity="don_hang", attempt=1)
    # Force the current run's log to be the oldest file, so the safety rule is
    # the only thing that can keep it alive.
    oldest = run.log_path.stat().st_mtime
    os.utime(run.log_path, (oldest - 10_000, oldest - 10_000))

    prune_logs(tmp_path / "logs", logger, keep=10)

    assert run.log_path.exists()


def test_prune_writes_the_pruned_event(tmp_path: Path):
    _seed_logs(tmp_path, 13)
    run = new_run_context("test", tmp_path / "logs", tmp_path / "tmp")
    logger = JsonLogger(run, console=False)

    prune_logs(tmp_path / "logs", logger, keep=10)

    events = [
        json.loads(line) for line in run.log_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    pruned = [event for event in events if event["event"] == "integration.logs.pruned"]
    assert pruned
    assert pruned[0]["deleted"] == 3
    assert pruned[0]["kept"] == 10


def test_prune_warns_instead_of_raising(tmp_path: Path):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    run = new_run_context("test", logs_dir, tmp_path / "tmp")
    logger = JsonLogger(run, console=False)
    for index in range(12):
        path = logs_dir / f"run-{index:02d}.jsonl"
        path.write_text("{}\n", encoding="utf-8")

    def explode(*args, **kwargs):
        raise OSError("thư mục đang bị khoá")

    original = Path.unlink
    Path.unlink = explode
    try:
        assert prune_logs(logs_dir, logger, keep=10) == 0
    finally:
        Path.unlink = original

    events = [
        json.loads(line) for line in run.log_path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert any(event["event"] == "integration.logs.prune_failed" for event in events)
