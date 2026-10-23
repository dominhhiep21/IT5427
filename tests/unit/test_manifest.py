"""Manifest idempotency tests."""

from __future__ import annotations

from src.pipeline.manifest import ManifestStore


def test_manifest_records_and_detects_success(tmp_path):
    store = ManifestStore(tmp_path / "manifest.json")
    assert not store.has_success("abc")
    store.record(
        {
            "batch_id": "batch-1",
            "files": [{"table": "orders", "sha256": "abc", "status": "success"}],
            "status": "success",
        }
    )
    assert store.has_success("abc")
    payload = store.load()
    assert len(payload["batches"]) == 1


def test_manifest_replaces_same_batch(tmp_path):
    store = ManifestStore(tmp_path / "manifest.json")
    store.record({"batch_id": "batch-1", "files": [], "status": "failed"})
    store.record({"batch_id": "batch-1", "files": [], "status": "success"})
    payload = store.load()
    assert len(payload["batches"]) == 1
    assert payload["batches"][0]["status"] == "success"
