from pathlib import Path

from flight_delays.config import get_settings


def test_defaults(monkeypatch):
    monkeypatch.delenv("FLIGHT_DELAYS_DATA_DIR", raising=False)
    monkeypatch.delenv("FLIGHT_DELAYS_DUCKDB_PATH", raising=False)
    settings = get_settings()
    assert settings.data_dir == Path("data")
    assert settings.duckdb_path == Path("data") / "flight_delays.duckdb"


def test_environment_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("FLIGHT_DELAYS_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLIGHT_DELAYS_DUCKDB_PATH", str(tmp_path / "x.duckdb"))
    settings = get_settings()
    assert settings.data_dir == tmp_path
    assert settings.duckdb_path == tmp_path / "x.duckdb"
