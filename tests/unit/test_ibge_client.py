"""IBGE cache and failure behavior tests."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from src.common.exceptions import ExternalSourceError
from src.external.ibge import IbgeClient


def _write_cache(config, region_map):
    raw = [
        {"sigla": row.state, "regiao": {"nome": row.region}}
        for row in region_map.itertuples()
    ]
    (config.ibge_dir / "estados.json").write_text(
        json.dumps(raw), encoding="utf-8"
    )


def test_cache_hit(config, region_map):
    _write_cache(config, region_map)
    client = IbgeClient(config)
    frame, source = client.fetch_states()
    assert source == "cache"
    assert len(frame) == 27
    assert frame["region"].nunique() == 5


def test_cache_fallback_when_refresh_fails(config, region_map):
    _write_cache(config, region_map)
    bad = replace(
        config,
        ibge_url="http://127.0.0.1:9",
        ibge_retries=0,
        ibge_timeout_seconds=1,
    )
    frame, source = IbgeClient(bad).fetch_states(refresh=True)
    assert source == "cache"
    assert len(frame) == 27


def test_missing_cache_and_api_failure_raises(config):
    bad = replace(
        config,
        ibge_url="http://127.0.0.1:9",
        ibge_retries=0,
        ibge_timeout_seconds=1,
    )
    with pytest.raises(ExternalSourceError):
        IbgeClient(bad).fetch_states()
