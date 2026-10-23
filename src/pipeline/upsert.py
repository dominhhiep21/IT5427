"""Natural-key upsert for cleaned tables."""

from __future__ import annotations

import pandas as pd


def upsert(existing: pd.DataFrame, new: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if new.empty:
        return existing
    if existing.empty:
        return new.reset_index(drop=True)
    missing = [column for column in existing.columns if column not in new.columns]
    for column in missing:
        new[column] = pd.NA
    new = new[existing.columns]
    key_frame = new[keys].drop_duplicates()
    marked = existing.merge(key_frame, on=keys, how="left", indicator=True)
    kept = marked[marked["_merge"] == "left_only"].drop(columns="_merge")
    combined = pd.concat([kept, new], ignore_index=True)
    return combined.sort_values(keys).reset_index(drop=True)
