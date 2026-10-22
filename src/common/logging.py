"""Run context and JSON-lines logging."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.common.types import RunContext


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_run_context(stage: str, logs_dir: Path, temp_root: Path) -> RunContext:
    """Create a run id, log path and temp directory for one pipeline run."""

    started_at = _utc_now()
    run_id = f"{started_at.strftime('%Y%m%dT%H%M%S')}-{uuid.uuid4().hex[:8]}"
    temp_dir = temp_root / run_id
    log_path = logs_dir / f"{run_id}.jsonl"
    temp_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    return RunContext(
        run_id=run_id,
        stage=stage,
        started_at=started_at,
        temp_dir=temp_dir,
        log_path=log_path,
    )


class JsonLogger:
    """Write structured events to a JSON-lines file and a short console summary."""

    def __init__(self, run: RunContext, console: bool = True) -> None:
        self.run = run
        self.console = console

    def _write(self, level: str, event: str, **fields: object) -> None:
        record = {
            "timestamp": _utc_now().isoformat().replace("+00:00", "Z"),
            "level": level,
            "run_id": self.run.run_id,
            "stage": self.run.stage,
            "event": event,
            **fields,
        }
        with self.run.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def info(self, event: str, **fields: object) -> None:
        self._write("INFO", event, **fields)

    def warning(self, event: str, **fields: object) -> None:
        self._write("WARNING", event, **fields)

    def error(self, event: str, error_code: str, **fields: object) -> None:
        self._write("ERROR", event, error_code=error_code, **fields)

    def summary(self, message: str) -> None:
        self._write("INFO", "summary", message=message)
        if self.console:
            print(message)
