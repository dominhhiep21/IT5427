"""Aggregate geolocation rows to one row per zip code prefix."""

from __future__ import annotations

import pandas as pd

from src.clean.common import normalize_state, normalize_text, to_integer, to_numeric
from src.common.types import GeoCleaningStats

ZIP = "geolocation_zip_code_prefix"
LAT = "geolocation_lat"
LNG = "geolocation_lng"
CITY = "geolocation_city"
STATE = "geolocation_state"

ORIGINAL_COLUMNS = [ZIP, LAT, LNG, CITY, STATE]


def clean_geolocation(
    df: pd.DataFrame,
    lat_min: float = -34.0,
    lat_max: float = 6.0,
    lng_min: float = -74.0,
    lng_max: float = -34.0,
) -> tuple[pd.DataFrame, GeoCleaningStats]:
    raw = df.copy()
    raw[ZIP] = to_integer(raw[ZIP])
    raw[LAT] = to_numeric(raw[LAT])
    raw[LNG] = to_numeric(raw[LNG])

    raw_valid = (
        raw[LAT].between(lat_min, lat_max) & raw[LNG].between(lng_min, lng_max)
    )
    outside_bbox = int((~raw_valid).sum())

    dedup = raw.drop_duplicates(subset=ORIGINAL_COLUMNS, keep="first").copy()
    dedup["city_norm"] = normalize_text(dedup[CITY]).fillna("unknown")
    dedup["state_norm"] = normalize_state(dedup[STATE]).fillna("unknown")
    dedup["valid_coord"] = (
        dedup[LAT].between(lat_min, lat_max) & dedup[LNG].between(lng_min, lng_max)
    )

    valid = dedup[dedup["valid_coord"]]
    coord = (
        valid.groupby(ZIP)
        .agg(
            lat_median=(LAT, "median"),
            lng_median=(LNG, "median"),
            valid_coord_count=(LAT, "size"),
        )
        .reset_index()
    )

    city_counts = (
        dedup.groupby([ZIP, "city_norm"], dropna=False)
        .size()
        .reset_index(name="city_count")
    )
    city_mode = (
        city_counts.sort_values(
            [ZIP, "city_count", "city_norm"],
            ascending=[True, False, True],
        )
        .drop_duplicates(ZIP)[[ZIP, "city_norm"]]
        .rename(columns={"city_norm": "city_mode"})
    )

    state_counts = (
        dedup.groupby([ZIP, "state_norm"], dropna=False)
        .size()
        .reset_index(name="state_count")
    )
    state_mode = (
        state_counts.sort_values(
            [ZIP, "state_count", "state_norm"],
            ascending=[True, False, True],
        )
        .drop_duplicates(ZIP)[[ZIP, "state_norm"]]
        .rename(columns={"state_norm": "state_mode"})
    )

    row_count = dedup.groupby(ZIP).size().reset_index(name="row_count")
    city_variants = (
        dedup.groupby(ZIP)["city_norm"]
        .nunique()
        .reset_index(name="city_variant_count")
    )

    result = dedup[[ZIP]].drop_duplicates().reset_index(drop=True)
    for frame in (coord, city_mode, state_mode, row_count, city_variants):
        result = result.merge(frame, on=ZIP, how="left")

    result = result.rename(columns={ZIP: "zip_code_prefix"})
    result["valid_coord_count"] = result["valid_coord_count"].fillna(0).astype("Int64")
    result["row_count"] = result["row_count"].fillna(0).astype("Int64")
    result["city_variant_count"] = result["city_variant_count"].fillna(0).astype("Int64")

    result = result[
        [
            "zip_code_prefix",
            "lat_median",
            "lng_median",
            "city_mode",
            "state_mode",
            "row_count",
            "valid_coord_count",
            "city_variant_count",
        ]
    ].sort_values("zip_code_prefix").reset_index(drop=True)

    stats = GeoCleaningStats(
        raw_rows=len(raw),
        deduped_rows=len(dedup),
        outside_bbox=outside_bbox,
        zips=len(result),
        zips_without_coord=int(result["lat_median"].isna().sum()),
        multi_city_zips=int((result["city_variant_count"] > 1).sum()),
    )
    return result, stats
