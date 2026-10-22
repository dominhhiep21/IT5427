"""IBGE reference-data client with cache and retry."""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.common.exceptions import ExternalSourceError
from src.common.logging import JsonLogger
from src.common.types import IbgeMetadata
from src.external.region import RegionMapper


class IbgeClient:
    def __init__(self, config, logger: JsonLogger | None = None) -> None:
        self.config = config
        self.logger = logger
        self.estados_path = config.ibge_dir / "estados.json"
        self.municipios_path = config.ibge_dir / "municipios.json"
        self.metadata_path = config.ibge_dir / "metadata.json"

    def _read_json(self, path: Path):
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_json(self, path: Path, payload) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _states_from_raw(self, raw: list[dict]) -> pd.DataFrame:
        rows = [
            {
                "state": str(item["sigla"]).strip().upper(),
                "region": str(item["regiao"]["nome"]).strip(),
            }
            for item in raw
        ]
        frame = pd.DataFrame(rows).drop_duplicates()
        return frame.sort_values("state").reset_index(drop=True)

    def _cache_valid(self) -> bool:
        if not self.estados_path.exists():
            return False
        try:
            raw = self._read_json(self.estados_path)
            frame = self._states_from_raw(raw)
            return len(frame) == 27 and frame["region"].nunique() == 5
        except Exception:
            return False

    def _fetch_api(self, endpoint: str) -> list[dict]:
        url = f"{self.config.ibge_url.rstrip('/')}/{endpoint}"
        last_error: Exception | None = None
        for attempt in range(self.config.ibge_retries + 1):
            try:
                request = urllib.request.Request(
                    url, headers={"Accept": "application/json"}
                )
                with urllib.request.urlopen(
                    request, timeout=self.config.ibge_timeout_seconds
                ) as response:
                    return json.load(response)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt < self.config.ibge_retries:
                    time.sleep(1 + attempt)
        raise ExternalSourceError(f"IBGE request failed: {url}: {last_error}")

    def _save_states(self, raw: list[dict], source: str) -> None:
        self._write_json(self.estados_path, raw)
        payload = self.estados_path.read_bytes()
        metadata = IbgeMetadata(
            url=f"{self.config.ibge_url.rstrip('/')}/estados",
            fetched_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            sha256=hashlib.sha256(payload).hexdigest(),
            states=len(raw),
            source=source,
        )
        self._write_json(self.metadata_path, metadata.__dict__)

    def fetch_states(self, refresh: bool = False) -> tuple[pd.DataFrame, str]:
        if not refresh and self._cache_valid():
            raw = self._read_json(self.estados_path)
            if self.logger:
                self.logger.info("ibge_cache_hit", states=len(raw))
            return self._states_from_raw(raw), "cache"

        try:
            raw = self._fetch_api("estados")
            if not isinstance(raw, list) or len(raw) != 27:
                raise ExternalSourceError(
                    f"IBGE estados returned {len(raw) if isinstance(raw, list) else 'non-list'} rows"
                )
            self._save_states(raw, source="ibge-api")
            if self.logger:
                self.logger.info("ibge_fetched", states=len(raw))
            return self._states_from_raw(raw), "api"
        except ExternalSourceError:
            if self._cache_valid():
                raw = self._read_json(self.estados_path)
                if self.logger:
                    self.logger.warning("ibge_api_failed_using_cache")
                return self._states_from_raw(raw), "cache"
            raise

    def fetch_municipalities(self, refresh: bool = False) -> pd.DataFrame:
        if not refresh and self.municipios_path.exists():
            return pd.DataFrame(self._read_json(self.municipios_path))
        try:
            raw = self._fetch_api("municipios")
            self._write_json(self.municipios_path, raw)
            return pd.DataFrame(raw)
        except ExternalSourceError:
            if self.municipios_path.exists():
                return pd.DataFrame(self._read_json(self.municipios_path))
            raise

    def load_region_map(self, refresh: bool = False) -> pd.DataFrame:
        states, source = self.fetch_states(refresh=refresh)
        RegionMapper.validate(states)
        if self.logger:
            self.logger.info("region_map_ready", states=len(states), source=source)
        return states
