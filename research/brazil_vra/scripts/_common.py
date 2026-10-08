"""Shared helpers for the Brazil VRA research scripts.

Data location
-------------
All scripts read from one data directory, set with the environment variable
``BRAZIL_VRA_DATA_DIR`` (default: ``<repo>/data/research/brazil_vra``).
Expected layout, as produced by ``download.py``::

    <data dir>/vra/VRA_<year><month>.csv     ANAC VRA monthly files (month without leading zero)
    <data dir>/bitacora-vuelos.parquet       Chile JAC flight log (datos.gob.cl)
    <data dir>/sbgr_metar.csv                SBGR METAR history (Iowa State Mesonet)

Nothing in these scripts writes to the data directory except ``download.py``.
The loaders only parse values for comparison; they do not clean, drop or
adjust any row.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = Path(
    os.environ.get("BRAZIL_VRA_DATA_DIR", REPO_ROOT / "data" / "research" / "brazil_vra")
)
VRA_DIR = DATA_DIR / "vra"
CHILE_PARQUET = DATA_DIR / "bitacora-vuelos.parquet"
SBGR_METAR = DATA_DIR / "sbgr_metar.csv"

# Short column names used by the scripts, in file order:
# airline, flight number, DI, line type, origin, destination,
# scheduled departure, actual departure, scheduled arrival, actual arrival,
# status, justification code.
C = ["al", "flt", "di", "tl", "org", "dst", "pp", "pr", "cp", "cr", "sit", "just"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def vra_path(y: int, m: int) -> Path:
    return VRA_DIR / f"VRA_{y}{m}.csv"


def load(y: int, m: int) -> pd.DataFrame:
    """Load one VRA month as strings and add parsed ``*_t`` time columns.

    Two raw formats occur in the archive: ``YYYY-MM-DD HH:MM:SS`` (sometimes with
    a ``.100000000`` suffix, which is ignored when parsing) and
    ``dd/mm/yyyy HH:MM``. Empty strings and the literal ``null`` parse to NaT.
    """
    df = pd.read_csv(
        vra_path(y, m),
        sep=";",
        skiprows=1,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )
    df.columns = C
    for c in ["pp", "pr", "cp", "cr"]:
        s = df[c].str.strip()
        s2 = s.str.slice(0, 19)  # read-only parse: ignores fractional suffix
        a = pd.to_datetime(s2, format="%Y-%m-%d %H:%M:%S", errors="coerce")
        b = pd.to_datetime(s.str.slice(0, 16), format="%d/%m/%Y %H:%M", errors="coerce")
        df[c + "_t"] = a.fillna(b)
    return df


def load_chile_brazil() -> pd.DataFrame:
    """Chile flight-log rows to/from five Brazilian airports since 2018, with UTC time.

    Same subset the session cached as ``chile_br.pkl``; built in memory here so
    nothing is written to the data directory.
    """
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    t = pq.read_table(
        CHILE_PARQUET,
        columns=[
            "dt_operacion",
            "aeropuerto_oaci",
            "tipo_operacion",
            "aeropuerto_dgac_orig_dest",
            "aerolinea_dgac",
            "numero_vuelo",
        ],
    )
    b = t.filter(
        pc.and_(
            pc.is_in(
                t["aeropuerto_dgac_orig_dest"],
                value_set=pa.array(["SBGR", "SBGL", "SBFL", "SBPA", "SBBR"]),
            ),
            pc.greater(t["dt_operacion"], pa.scalar(pd.Timestamp("2018-01-01", tz="UTC"))),
        )
    ).to_pandas()
    b["utc"] = b.dt_operacion.dt.tz_convert("UTC").dt.tz_localize(None)
    b["fn"] = pd.to_numeric(b.numero_vuelo, errors="coerce")
    return b
