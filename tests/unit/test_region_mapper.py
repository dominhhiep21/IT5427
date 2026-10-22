"""IBGE region mapping tests."""

from __future__ import annotations

import pandas as pd
import pytest

from src.common.exceptions import ExternalSourceError
from src.external.region import RegionMapper


def test_region_map_has_27_states_and_5_regions(region_map):
    RegionMapper.validate(region_map)
    assert len(region_map) == 27
    assert region_map["region"].nunique() == 5


def test_unknown_state_raises(region_map):
    with pytest.raises(ExternalSourceError):
        RegionMapper.validate(region_map, states_in_data={"SP", "ZZ"})


def test_attach_region(region_map):
    frame = pd.DataFrame({"state": ["SP", "RJ"]})
    out = RegionMapper.attach(frame, "state", region_map)
    assert out["region"].tolist() == ["Sudeste", "Sudeste"]
