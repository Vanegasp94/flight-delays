"""Download BTS On-Time Performance (marketing carrier) monthly files and load them into DuckDB.

Source
------
Bureau of Transportation Statistics, TranStats, "Marketing Carrier On-Time
Performance (Beginning January 2018)". One pre-zipped CSV per month:

    https://transtats.bts.gov/PREZIP/On_Time_Marketing_Carrier_On_Time_Performance_Beginning_January_2018_<YYYY>_<M>.zip

Table page: https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK

What it does
------------
1. Finds the latest month published (unless ``--end`` is given).
2. Downloads each monthly zip into ``<data dir>/raw/bts_otp_marketing/`` (git-ignored).
   Existing files whose size matches the server's Content-Length are kept.
3. Loads every CSV into ``raw.bts_otp_marketing`` in the local DuckDB database with
   every column as VARCHAR and the original column names. Nothing is cleaned,
   cast, dropped or renamed. Three lineage columns are added:
   ``_source_file``, ``_source_year``, ``_source_month``.
4. Records one row per file in ``raw.bts_otp_load_log`` (bytes, CSV data lines,
   rows loaded, status), so failed or short months are visible.

Usage::

    uv run python ingestion/bts_otp.py                      # 2023-01 to latest available
    uv run python ingestion/bts_otp.py --start 2024-01 --end 2024-03
    uv run python ingestion/bts_otp.py --reload             # reload months already in the database
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

import duckdb

from flight_delays.config import get_settings

BASE_URL = "https://transtats.bts.gov/PREZIP"
FILE_STEM = "On_Time_Marketing_Carrier_On_Time_Performance_Beginning_January_2018"
TABLE = "raw.bts_otp_marketing"
LOG_TABLE = "raw.bts_otp_load_log"
HEADERS = {"User-Agent": "Mozilla/5.0"}
DEFAULT_START = "2023-01"


@dataclass
class Month:
    year: int
    month: int

    @property
    def filename(self) -> str:
        return f"{FILE_STEM}_{self.year}_{self.month}.zip"

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.filename}"

    @property
    def label(self) -> str:
        return f"{self.year}-{self.month:02d}"

    def next(self) -> Month:
        return Month(self.year + self.month // 12, self.month % 12 + 1)

    def previous(self) -> Month:
        return Month(self.year - (self.month == 1), 12 if self.month == 1 else self.month - 1)


def parse_month(text: str) -> Month:
    year, month = text.split("-")
    return Month(int(year), int(month))


def head(url: str) -> tuple[int, int | None, str | None]:
    """Return (HTTP status, Content-Length, Last-Modified) for a URL."""
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            size = r.headers.get("Content-Length")
            return r.status, int(size) if size else None, r.headers.get("Last-Modified")
    except urllib.error.HTTPError as e:
        return e.code, None, None


def latest_available(today: dt.date | None = None) -> Month:
    """Walk back from the current month until a monthly file exists (at most 12 steps)."""
    today = today or dt.date.today()
    m = Month(today.year, today.month)
    for _ in range(12):
        if head(m.url)[0] == 200:
            return m
        m = m.previous()
    raise RuntimeError("No BTS monthly file found in the last 12 months")


def month_range(start: Month, end: Month) -> list[Month]:
    out = []
    m = start
    while (m.year, m.month) <= (end.year, end.month):
        out.append(m)
        m = m.next()
    return out


def download(m: Month, raw_dir: Path, attempts: int = 3) -> dict:
    """Download one monthly zip. Returns a dict describing the outcome."""
    dest = raw_dir / m.filename
    info = {"month": m.label, "file": m.filename, "url": m.url, "path": dest}
    status, size, last_modified = head(m.url)
    info.update(http_status=status, remote_bytes=size, last_modified=last_modified)
    if status != 200:
        return info | {"status": f"download failed: HTTP {status}"}
    if dest.exists() and size is not None and dest.stat().st_size == size:
        return info | {"status": "ok", "downloaded": False}
    tmp = dest.with_name(dest.name + ".part")
    err = ""
    for _ in range(attempts):
        try:
            req = urllib.request.Request(m.url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=600) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            if size is not None and tmp.stat().st_size != size:
                raise OSError(f"size {tmp.stat().st_size} != Content-Length {size}")
            tmp.replace(dest)
            return info | {"status": "ok", "downloaded": True}
        except Exception as e:  # noqa: BLE001 - report and retry
            err = str(e)
            time.sleep(5)
    tmp.unlink(missing_ok=True)
    return info | {"status": f"download failed: {err}"}


def count_data_lines(path: Path) -> int:
    """Number of lines after the header. BTS fields contain no embedded newlines."""
    with open(path, "rb") as f:
        return sum(buf.count(b"\n") for buf in iter(lambda: f.read(1 << 22), b"")) - 1


def ensure_log_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {LOG_TABLE} (
            month VARCHAR, source_file VARCHAR, url VARCHAR, zip_bytes BIGINT,
            remote_last_modified VARCHAR, csv_name VARCHAR, csv_data_lines BIGINT,
            rows_loaded BIGINT, n_columns INTEGER, status VARCHAR, loaded_at TIMESTAMP
        )
        """
    )


def table_exists(con: duckdb.DuckDBPyConnection) -> bool:
    return bool(
        con.execute(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'raw' AND table_name = 'bts_otp_marketing'"
        ).fetchone()[0]
    )


def already_loaded(con: duckdb.DuckDBPyConnection, m: Month) -> int:
    if not table_exists(con):
        return 0
    return con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE _source_file = ?", [m.filename]
    ).fetchone()[0]


def load(con: duckdb.DuckDBPyConnection, m: Month, info: dict) -> dict:
    """Load one downloaded zip into DuckDB. All columns VARCHAR, names as in the file."""
    zip_path: Path = info["path"]
    result = {"csv_name": None, "csv_data_lines": None, "rows_loaded": None, "n_columns": None}
    try:
        with zipfile.ZipFile(zip_path) as z:
            bad = z.testzip()
            if bad:
                raise zipfile.BadZipFile(f"corrupt member {bad}")
            csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if len(csvs) != 1:
                raise ValueError(f"expected one CSV in zip, found {csvs}")
            with tempfile.TemporaryDirectory(dir=zip_path.parent) as tmp:
                csv_path = Path(z.extract(csvs[0], tmp))
                result["csv_name"] = csvs[0]
                result["csv_data_lines"] = count_data_lines(csv_path)
                source = f"""
                    SELECT *, '{m.filename}' AS _source_file,
                           {m.year} AS _source_year, {m.month} AS _source_month
                    FROM read_csv('{csv_path.as_posix()}', header = true, all_varchar = true,
                                  delim = ',', quote = '"')
                """
                con.execute("BEGIN")
                if table_exists(con):
                    con.execute(f"DELETE FROM {TABLE} WHERE _source_file = ?", [m.filename])
                    con.execute(f"INSERT INTO {TABLE} BY NAME {source}")
                else:
                    con.execute(f"CREATE TABLE {TABLE} AS {source}")
                con.execute("COMMIT")
        result["rows_loaded"] = already_loaded(con, m)
        result["n_columns"] = con.execute(
            "SELECT count(*) FROM information_schema.columns "
            "WHERE table_schema = 'raw' AND table_name = 'bts_otp_marketing'"
        ).fetchone()[0]
        if result["rows_loaded"] == result["csv_data_lines"]:
            result["status"] = "ok"
        else:
            result["status"] = "row count differs from CSV line count"
    except Exception as e:  # noqa: BLE001 - one bad month must not stop the others
        try:
            con.execute("ROLLBACK")
        except duckdb.Error:
            pass
        result["status"] = f"load failed: {e}"
    return result


def write_log(con: duckdb.DuckDBPyConnection, m: Month, info: dict, result: dict) -> None:
    con.execute(f"DELETE FROM {LOG_TABLE} WHERE source_file = ?", [m.filename])
    zip_path: Path = info["path"]
    con.execute(
        f"INSERT INTO {LOG_TABLE} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, now()::TIMESTAMP)",
        [
            m.label,
            m.filename,
            m.url,
            zip_path.stat().st_size if zip_path.exists() else None,
            info.get("last_modified"),
            result.get("csv_name"),
            result.get("csv_data_lines"),
            result.get("rows_loaded"),
            result.get("n_columns"),
            result.get("status"),
        ],
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Download and load BTS On-Time Performance data.")
    ap.add_argument("--start", default=DEFAULT_START, help="first month, YYYY-MM")
    ap.add_argument("--end", help="last month, YYYY-MM (default: latest published)")
    ap.add_argument("--reload", action="store_true", help="reload months already in the database")
    args = ap.parse_args()

    settings = get_settings()
    raw_dir = settings.data_dir / "raw" / "bts_otp_marketing"
    raw_dir.mkdir(parents=True, exist_ok=True)

    end = parse_month(args.end) if args.end else latest_available()
    months = month_range(parse_month(args.start), end)
    print(f"source: {BASE_URL}/{FILE_STEM}_<YYYY>_<M>.zip")
    print(f"months: {months[0].label} to {months[-1].label} ({len(months)} files)")
    print(f"raw files: {raw_dir}")
    print(f"database: {settings.duckdb_path}")

    with cf.ThreadPoolExecutor(3) as ex:
        infos = list(ex.map(lambda m: download(m, raw_dir), months))

    con = duckdb.connect(str(settings.duckdb_path))
    ensure_log_table(con)
    for m, info in zip(months, infos, strict=True):
        if info["status"] != "ok":
            result = {"status": info["status"]}
        elif not args.reload and already_loaded(con, m):
            print(f"{m.label}  already loaded ({already_loaded(con, m)} rows)", flush=True)
            continue
        else:
            result = load(con, m, info)
        write_log(con, m, info, result)
        print(
            f"{m.label}  {result['status']}  rows={result.get('rows_loaded')} "
            f"csv_lines={result.get('csv_data_lines')} cols={result.get('n_columns')}",
            flush=True,
        )
    con.close()


if __name__ == "__main__":
    main()
