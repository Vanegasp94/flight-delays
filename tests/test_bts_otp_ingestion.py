"""Tests for ingestion/bts_otp.py that need neither the network nor real BTS data."""

import importlib
import sys
import zipfile
from pathlib import Path

import duckdb
import pytest

INGESTION = Path(__file__).resolve().parents[1] / "ingestion"

# Two data rows in the shape of a BTS file: quoted fields containing commas,
# an empty field, and a trailing comma on every line (including the header).
SAMPLE_CSV = (
    '"Year","Month","FlightDate","Origin","OriginCityName","DepDelay","Cancelled",\n'
    '2023,1,2023-01-22,"HPN","White Plains, NY",-4.00,0.00,\n'
    '2023,1,2023-01-23,"LAX","Los Angeles, CA",,1.00,\n'
)


@pytest.fixture
def bts(monkeypatch):
    monkeypatch.syspath_prepend(str(INGESTION))
    sys.modules.pop("bts_otp", None)
    module = importlib.import_module("bts_otp")
    yield module
    sys.modules.pop("bts_otp", None)


def test_month_filename_and_url(bts):
    m = bts.Month(2023, 1)
    assert m.label == "2023-01"
    assert m.filename == (
        "On_Time_Marketing_Carrier_On_Time_Performance_Beginning_January_2018_2023_1.zip"
    )
    assert m.url == f"https://transtats.bts.gov/PREZIP/{m.filename}"


def test_month_next_and_previous_cross_year_boundaries(bts):
    assert bts.Month(2023, 12).next() == bts.Month(2024, 1)
    assert bts.Month(2024, 1).previous() == bts.Month(2023, 12)
    assert bts.Month(2024, 6).next() == bts.Month(2024, 7)
    assert bts.Month(2024, 6).previous() == bts.Month(2024, 5)


def test_month_range_is_inclusive(bts):
    months = bts.month_range(bts.parse_month("2023-11"), bts.parse_month("2024-02"))
    assert [m.label for m in months] == ["2023-11", "2023-12", "2024-01", "2024-02"]
    assert bts.month_range(bts.parse_month("2024-03"), bts.parse_month("2024-02")) == []


def test_count_data_lines_excludes_header(bts, tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text(SAMPLE_CSV, encoding="utf-8", newline="")
    assert bts.count_data_lines(path) == 2


def test_load_keeps_values_as_text_and_adds_lineage(bts, tmp_path):
    m = bts.Month(2023, 1)
    zip_path = tmp_path / m.filename
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("sample_2023_1.csv", SAMPLE_CSV)
    con = duckdb.connect(str(tmp_path / "test.duckdb"))
    bts.ensure_log_table(con)

    result = bts.load(con, m, {"path": zip_path})

    assert result["status"] == "ok"
    assert result["rows_loaded"] == 2
    assert result["csv_data_lines"] == 2
    types = dict(
        con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = 'raw' AND table_name = 'bts_otp_marketing'"
        ).fetchall()
    )
    source_columns = [c for c in types if not c.startswith("_source_")]
    assert all(types[c] == "VARCHAR" for c in source_columns)
    assert {"_source_file", "_source_year", "_source_month"} <= set(types)
    rows = con.execute(
        'SELECT "OriginCityName", "DepDelay", "Cancelled", _source_file, _source_year, '
        f'_source_month FROM {bts.TABLE} ORDER BY "FlightDate"'
    ).fetchall()
    # values are not cast or adjusted; an empty field is NULL
    assert rows == [
        ("White Plains, NY", "-4.00", "0.00", m.filename, 2023, 1),
        ("Los Angeles, CA", None, "1.00", m.filename, 2023, 1),
    ]

    # loading the same month again replaces its rows instead of duplicating them
    again = bts.load(con, m, {"path": zip_path})
    assert again["rows_loaded"] == 2
    assert con.execute(f"SELECT count(*) FROM {bts.TABLE}").fetchone()[0] == 2
    con.close()


def test_load_reports_a_corrupt_zip_instead_of_raising(bts, tmp_path):
    m = bts.Month(2023, 2)
    zip_path = tmp_path / m.filename
    zip_path.write_bytes(b"this is not a zip file")
    con = duckdb.connect(str(tmp_path / "test.duckdb"))
    bts.ensure_log_table(con)

    result = bts.load(con, m, {"path": zip_path})

    assert result["status"].startswith("load failed")
    assert result["rows_loaded"] is None
    con.close()
