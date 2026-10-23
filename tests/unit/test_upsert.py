"""Natural-key upsert tests."""

from __future__ import annotations

import pandas as pd

from src.pipeline.upsert import upsert


def test_upsert_replaces_existing_key():
    existing = pd.DataFrame(
        [{"order_id": "o1", "status": "shipped"}, {"order_id": "o2", "status": "delivered"}]
    )
    new = pd.DataFrame([{"order_id": "o1", "status": "delivered"}])
    result = upsert(existing, new, ["order_id"])
    assert len(result) == 2
    assert result.loc[result["order_id"] == "o1", "status"].iloc[0] == "delivered"


def test_upsert_appends_new_key():
    existing = pd.DataFrame([{"order_id": "o1", "status": "delivered"}])
    new = pd.DataFrame([{"order_id": "o2", "status": "shipped"}])
    result = upsert(existing, new, ["order_id"])
    assert len(result) == 2
    assert set(result["order_id"]) == {"o1", "o2"}
