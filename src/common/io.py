"""CSV/Parquet IO and atomic writes."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path

import pandas as pd

from src.common.exceptions import SchemaError
from src.common.types import RunContext, TableSpec


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_columns(df: pd.DataFrame, spec: TableSpec) -> None:
    actual = tuple(df.columns)
    if actual != spec.columns:
        missing = [column for column in spec.columns if column not in actual]
        extra = [column for column in actual if column not in spec.columns]
        raise SchemaError(
            f"{spec.name}: schema mismatch. missing={missing}, extra={extra}, "
            f"expected={list(spec.columns)}, actual={list(actual)}"
        )


def read_csv(path: Path, spec: TableSpec) -> pd.DataFrame:
    if not path.exists():
        raise SchemaError(f"{spec.name}: file not found: {path}")
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    except UnicodeDecodeError as exc:
        raise SchemaError(f"{spec.name}: file is not valid UTF-8: {path}") from exc
    validate_columns(df, spec)
    return df


def read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


class AtomicWriter:
    """Write files to a temp path, verify, then atomically replace the target."""

    def __init__(self, run: RunContext, compression: str = "snappy") -> None:
        self.run = run
        self.compression = compression

    def write_parquet(self, df: pd.DataFrame, final_path: Path) -> None:
        final_path = Path(final_path)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.run.temp_dir / f"{final_path.name}.{uuid.uuid4().hex}.tmp"
        df.to_parquet(
            tmp_path,
            engine="pyarrow",
            compression=self.compression,
            index=False,
        )
        check = pd.read_parquet(tmp_path)
        if len(check) != len(df):
            raise RuntimeError(
                f"Parquet verification failed for {final_path}: "
                f"wrote {len(check)} rows, expected {len(df)}"
            )
        os.replace(tmp_path, final_path)

    def write_json(self, payload: dict, final_path: Path) -> None:
        final_path = Path(final_path)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.run.temp_dir / f"{final_path.name}.{uuid.uuid4().hex}.tmp"
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, default=str)
        os.replace(tmp_path, final_path)

    def cleanup(self) -> None:
        """Remove the temp directory after a successful run."""

        shutil.rmtree(self.run.temp_dir, ignore_errors=True)
