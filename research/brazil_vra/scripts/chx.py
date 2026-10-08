"""Cross-check VRA times against Chile's flight log for Brazil-Chile flights, including DST periods.

Prints the difference VRA time minus the Chilean log's UTC time, rounded to hours.
"""

import numpy as np
import pandas as pd
from _common import load, load_chile_brazil, vra_path

b = load_chile_brazil()


def cross(y, m, label=None, dayfilter=None):
    if not vra_path(y, m).exists():
        print(y, m, "file missing")
        return
    df = load(y, m)
    R = df[df.sit == "REALIZADO"].copy()
    R["fn"] = pd.to_numeric(R.flt, errors="coerce")
    for kind, vcol, vap, bt in (
        ("arrivals into Chile (VRA Chegada Real vs bitacora A)", "cr_t", "dst", "A"),
        ("departures from Chile (VRA Partida Real vs bitacora D)", "pr_t", "org", "D"),
    ):
        v = R[R[vap].str.startswith("SC")][["al", "fn", "org", "dst", vcol]].dropna()
        v["cl"] = v[vap]
        v["br"] = np.where(vap == "dst", v.org, v.dst)
        bb = b[b.tipo_operacion == bt]
        mm = v.merge(
            bb,
            left_on=["al", "fn", "cl", "br"],
            right_on=["aerolinea_dgac", "fn", "aeropuerto_oaci", "aeropuerto_dgac_orig_dest"],
        )
        mm["d"] = (mm[vcol] - mm.utc).dt.total_seconds() / 60
        mm = mm[mm.d.abs() < 600]  # same-flight candidates within 10h
        if dayfilter is not None:
            for nm, f in dayfilter.items():
                x = mm[f(mm[vcol])]
                print(
                    f"  {y}-{m:02d} {nm}: {kind}: n={len(x)} median VRA-UTC = {x.d.median():.0f} min; rounded-hour counts {dict((x.d / 60).round().value_counts().sort_index())}"
                )
        else:
            print(
                f"  {y}-{m:02d}: {kind}: n={len(mm)} median VRA-UTC = {mm.d.median():.0f} min; rounded-hour counts {dict((mm.d / 60).round().value_counts().sort_index())}"
            )


if __name__ == "__main__":
    cross(2026, 7)
    cross(
        2018,
        11,
        dayfilter={
            "Nov 1-3 (before DST start 4 Nov 2018)": lambda s: s < pd.Timestamp("2018-11-03 20:00"),
            "Nov 5-30 (DST)": lambda s: s >= pd.Timestamp("2018-11-05"),
        },
    )
    cross(
        2018,
        2,
        dayfilter={
            "Feb 1-16 (DST)": lambda s: s < pd.Timestamp("2018-02-17 12:00"),
            "Feb 19-28 (after DST end 18 Feb 2018)": lambda s: s >= pd.Timestamp("2018-02-19"),
        },
    )
    cross(2018, 7)
    cross(
        2019,
        2,
        dayfilter={
            "Feb 1-15 (DST)": lambda s: s < pd.Timestamp("2019-02-16 12:00"),
            "Feb 18-28 (after DST end 17 Feb 2019)": lambda s: s >= pd.Timestamp("2019-02-18"),
        },
    )
