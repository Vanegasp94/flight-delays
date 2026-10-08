"""Download the source files used by the Brazil VRA research into the data directory.

Sources
-------
- ANAC VRA monthly CSVs:
  https://sistemas.anac.gov.br/dadosabertos/Voos e operações aéreas/Voo Regular Ativo (VRA)/
- Chile JAC "Bitácora de Vuelos" (Parquet, about 138 MB):
  https://datos.gob.cl/dataset/operaciones-aeronaves
- SBGR METAR history from Iowa State Mesonet (CSV, about 5 MB).

Usage::

    uv run python research/brazil_vra/scripts/download.py            # everything (about 1.4 GB)
    uv run python research/brazil_vra/scripts/download.py --only vra
    uv run python research/brazil_vra/scripts/download.py --only chile metar

Existing files are skipped. ANAC regenerates past months from time to time and
the Chile and Mesonet files grow, so a fresh download can differ from the files
the documented numbers were computed on.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import time
import urllib.parse
import urllib.request

from _common import CHILE_PARQUET, DATA_DIR, SBGR_METAR, VRA_DIR, vra_path

MONTHS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
VRA_BASE = (
    "https://sistemas.anac.gov.br/dadosabertos/Voos e operações aéreas/Voo Regular Ativo (VRA)"
)
CHILE_URL = (
    "https://datos.gob.cl/dataset/d5fac3ed-01c7-43f0-9dc4-8970566bc059/resource/"
    "5bc8842e-d95a-4f8f-8ec6-acfbe700258a/download/bitacora-vuelos.parquet"
)
# Same query as used in the session: routine METAR + SPECI, UTC, 2019-01-01 to 2026-10-02.
METAR_URL = (
    "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=SBGR&data=metar"
    "&year1=2019&month1=1&day1=1&year2=2026&month2=10&day2=2&tz=Etc%2FUTC"
    "&format=onlycomma&latlon=no&elev=no&missing=M&trace=T&direct=no"
    "&report_type=3&report_type=4"
)
HEADERS = {"User-Agent": "Mozilla/5.0"}


def vra_months() -> list[tuple[int, int]]:
    """The 103 months used in the research.

    July 2010-2018 (August for 2014: the June and July 2014 folders are empty on
    the server), February/October/November 2018, and every month from January
    2019 to July 2026.
    """
    want = [(y, 7) for y in range(2010, 2019) if y != 2014]
    want += [(2014, 8), (2018, 2), (2018, 10), (2018, 11)]
    want += [(y, m) for y in range(2019, 2027) for m in range(1, 13) if (y, m) <= (2026, 7)]
    return sorted(set(want))


def vra_url(y: int, m: int) -> str:
    return urllib.parse.quote(f"{VRA_BASE}/{y}/{m:02d} - {MONTHS[m - 1]}/VRA_{y}{m}.csv", safe=":/")


def fetch(url: str, dest, attempts: int = 3, timeout: int = 600) -> str:
    if dest.exists() and dest.stat().st_size > 1000:
        return f"cached  {dest.name} ({dest.stat().st_size} bytes)"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    err = ""
    for _ in range(attempts):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            tmp.replace(dest)
            return f"ok      {dest.name} ({dest.stat().st_size} bytes)"
        except Exception as e:  # noqa: BLE001 - report and retry
            err = str(e)
            time.sleep(3)
    tmp.unlink(missing_ok=True)
    return f"FAILED  {dest.name}: {err}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", nargs="+", choices=["vra", "chile", "metar"])
    args = ap.parse_args()
    what = args.only or ["vra", "chile", "metar"]
    print("data directory:", DATA_DIR)
    if "vra" in what:
        VRA_DIR.mkdir(parents=True, exist_ok=True)
        jobs = [(vra_url(y, m), vra_path(y, m)) for y, m in vra_months()]
        with cf.ThreadPoolExecutor(4) as ex:
            for line in ex.map(lambda j: fetch(*j), jobs):
                print(line, flush=True)
    if "chile" in what:
        print(fetch(CHILE_URL, CHILE_PARQUET), flush=True)
    if "metar" in what:
        print(fetch(METAR_URL, SBGR_METAR), flush=True)


if __name__ == "__main__":
    main()
