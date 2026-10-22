"""Validate and apply the IBGE state-to-region mapping."""

from __future__ import annotations

import pandas as pd

from src.common.exceptions import ExternalSourceError

EXPECTED_REGIONS = {"Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"}


class RegionMapper:
    @staticmethod
    def validate(region_map: pd.DataFrame, states_in_data: set[str] | None = None) -> None:
        if len(region_map) != 27:
            raise ExternalSourceError(
                f"Expected 27 states in IBGE map, got {len(region_map)}"
            )
        if region_map["state"].duplicated().any():
            raise ExternalSourceError("Duplicate states in IBGE map")
        if region_map["region"].isna().any():
            raise ExternalSourceError("Null region in IBGE map")
        actual_regions = set(region_map["region"].unique())
        if actual_regions != EXPECTED_REGIONS:
            raise ExternalSourceError(
                f"Unexpected IBGE regions: {sorted(actual_regions)}"
            )
        if states_in_data:
            missing = states_in_data - set(region_map["state"])
            if missing:
                raise ExternalSourceError(
                    f"States missing from IBGE map: {sorted(missing)}"
                )

    @staticmethod
    def attach(
        frame: pd.DataFrame,
        state_column: str,
        region_map: pd.DataFrame,
        output_column: str = "region",
    ) -> pd.DataFrame:
        mapping = region_map.set_index("state")["region"]
        out = frame.copy()
        out[output_column] = out[state_column].map(mapping)
        return out
