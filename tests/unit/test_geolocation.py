"""Geolocation aggregation tests."""

from __future__ import annotations

from src.clean.geolocation import clean_geolocation


def test_geolocation_dedup_median_mode_and_zip_preservation(small_geo):
    cleaned, stats = clean_geolocation(small_geo)

    assert len(cleaned) == 3
    assert stats.raw_rows == 6
    assert stats.deduped_rows == 5
    assert stats.outside_bbox == 1
    assert stats.zips == 3
    assert stats.zips_without_coord == 1
    assert stats.multi_city_zips == 1

    zip100 = cleaned.loc[cleaned["zip_code_prefix"] == 100].iloc[0]
    zip200 = cleaned.loc[cleaned["zip_code_prefix"] == 200].iloc[0]
    zip300 = cleaned.loc[cleaned["zip_code_prefix"] == 300].iloc[0]

    assert zip100["lat_median"] == -23.6
    assert zip100["lng_median"] == -46.5
    assert zip100["city_mode"] == "sao paulo"
    assert zip200["lat_median"] is None or str(zip200["lat_median"]) == "nan"
    assert zip300["lat_median"] == -22.0
