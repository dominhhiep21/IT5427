"""Write the C5 result file and run the whole linkage for one target entity (L3)."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.common.exceptions import SchemaError
from src.common.io import AtomicWriter
from src.common.logging import UNKNOWN_ERROR_CODE, NullLogger, normalise_error_code
from src.common.types import RunContext
from src.linkage.index import build_index
from src.linkage.models import (
    MAX_PAIRS,
    LinkageResult,
    LinkageResultError,
    blocking_rule,
)
from src.linkage.score import cap, score_pairs, summarise

RESULT_FILE_TEMPLATE = "linkage-{target_entity}.json"
MAX_MESSAGE_CHARS = 200
STARTED_EVENT = "integration.linkage.started"
COMPLETED_EVENT = "integration.linkage.completed"
FAILED_EVENT = "integration.linkage.failed"


def result_path(config, target_entity: str) -> Path:
    """`data/integration/linkage-<target_entity>.json` (C5)."""

    name = RESULT_FILE_TEMPLATE.format(target_entity=target_entity)
    return Path(config.integration_dir) / name


def _read_payload(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _writer_for(config, result: LinkageResult) -> AtomicWriter:
    """`AtomicWriter` for a call that has no pipeline run context to borrow."""

    temp_dir = Path(config.temp_dir) / result.run_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    run = RunContext(
        run_id=result.run_id,
        stage="linkage",
        started_at=datetime.now(timezone.utc),
        temp_dir=temp_dir,
        log_path=Path(config.logs_dir) / f"{result.run_id}.jsonl",
    )
    return AtomicWriter(run, config.parquet_compression)


def _verify(path: Path, result: LinkageResult) -> None:
    """Read the file back: `write_json` does not check itself the way `write_parquet` does (TS-U4-5)."""

    payload = _read_payload(path)
    summary = payload.get("summary")
    if not isinstance(summary, dict) or "pairs_total" not in summary:
        raise LinkageResultError(f"kiểm lại {path.name}: thiếu summary.pairs_total")
    expected_pairs = min(int(summary["pairs_total"]), MAX_PAIRS)
    actual_pairs = len(payload.get("pairs") or [])
    if actual_pairs != len(result.pairs):
        raise LinkageResultError(
            f"kiểm lại {path.name}: lệch số cặp so với kết quả, {len(result.pairs)} → {actual_pairs}"
        )
    if actual_pairs != expected_pairs:
        raise LinkageResultError(
            f"kiểm lại {path.name}: lệch số cặp, ghi {expected_pairs}, đọc lại {actual_pairs}"
        )
    expected_skipped = int(summary.get("pairs_skipped", 0))
    actual_skipped = len(payload.get("skipped") or [])
    if actual_skipped != expected_skipped:
        raise LinkageResultError(
            f"kiểm lại {path.name}: lệch số cặp bỏ qua, ghi {expected_skipped}, đọc lại {actual_skipped}"
        )


def write_result(config, result: LinkageResult, writer: AtomicWriter | None = None) -> Path:
    """Write one `LinkageResult` to its C5 path, then verify what landed on disk."""

    path = result_path(config, result.target_entity)
    writer = writer or _writer_for(config, result)
    writer.write_json(result.to_dict(), path)
    _verify(path, result)
    return path


def build_result(config, target_entity: str, run_id: str, computed_at: str | None = None) -> LinkageResult:
    """Run L1 and L2 for one target and shape the outcome into the C5 payload."""

    index = build_index(config, target_entity)
    outcome = score_pairs(index, blocking_rule(target_entity))
    summary = summarise(outcome, index)
    pairs, _, _ = cap(outcome.pairs)
    return LinkageResult(
        target_entity=target_entity,
        run_id=run_id,
        computed_at=computed_at or datetime.now(timezone.utc).isoformat(),
        pairs=pairs,
        skipped=outcome.skipped,
        summary=summary,
    )


def _error_code(exc: BaseException) -> str:
    if isinstance(exc, LinkageResultError):
        return "result_unreadable"
    if isinstance(exc, FileNotFoundError):
        return "file_not_found"
    if isinstance(exc, PermissionError):
        return "permission_denied"
    if isinstance(exc, SchemaError):
        return "column_missing"
    return UNKNOWN_ERROR_CODE


def generate_linkage(config, target_entity: str, run, writer: AtomicWriter, logger=None) -> LinkageResult:
    """Build, write and verify one target's result, emitting its three lifecycle events."""

    logger = logger or NullLogger()
    started = time.perf_counter()
    logger.info(STARTED_EVENT, target_entity=target_entity)
    try:
        result = build_result(config, target_entity, run.run_id)
        write_result(config, result, writer)
    except Exception as exc:
        logger.error(
            FAILED_EVENT,
            normalise_error_code(_error_code(exc)),
            target_entity=target_entity,
            message=str(exc)[:MAX_MESSAGE_CHARS],
        )
        raise

    summary = result.summary
    logger.info(
        COMPLETED_EVENT,
        target_entity=target_entity,
        pairs_scored=summary["pairs_scored"],
        pairs_matched=summary["pairs_matched"],
        pairs_review=summary["pairs_review"],
        pairs_skipped=summary["pairs_skipped"],
        pairs_truncated=summary["pairs_truncated"],
        elapsed_ms=int((time.perf_counter() - started) * 1000),
    )
    return result
