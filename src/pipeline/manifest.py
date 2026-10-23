"""Manifest for idempotent micro-batch processing."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


class ManifestStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        if not self.path.exists():
            return {"batches": []}
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        payload.setdefault("batches", [])
        return payload

    def save(self, payload: dict) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def has_success(self, file_hash: str) -> bool:
        for batch in self.load()["batches"]:
            for item in batch.get("files", []):
                if item.get("sha256") == file_hash and item.get("status") in {"success", "skipped"}:
                    return True
        return False

    def record(self, entry: dict) -> None:
        payload = self.load()
        payload["batches"] = [
            batch for batch in payload["batches"] if batch.get("batch_id") != entry.get("batch_id")
        ]
        entry.setdefault(
            "processed_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        payload["batches"].append(entry)
        payload["batches"].sort(key=lambda batch: batch.get("batch_id", ""))
        self.save(payload)
