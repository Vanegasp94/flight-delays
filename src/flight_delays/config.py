"""Project configuration, read from environment variables (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_DIR = "data"
DEFAULT_DUCKDB_FILENAME = "flight_delays.duckdb"


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    duckdb_path: Path


def get_settings() -> Settings:
    data_dir = Path(os.environ.get("FLIGHT_DELAYS_DATA_DIR", DEFAULT_DATA_DIR))
    duckdb_path = Path(
        os.environ.get("FLIGHT_DELAYS_DUCKDB_PATH", str(data_dir / DEFAULT_DUCKDB_FILENAME))
    )
    return Settings(data_dir=data_dir, duckdb_path=duckdb_path)
