"""Which airlines show a shifted UTC offset on 1-3 November 2018 (TAM anomaly).

Reconstructed from an inline command run in the session (it was not saved as a
file at the time).
"""

import pandas as pd
from _common import load, load_chile_brazil

b = load_chile_brazil()
df = load(2018, 11)
R = df[df.sit == "REALIZADO"].copy()
R["fn"] = pd.to_numeric(R.flt, errors="coerce")
for vcol, vap, oth, bt in (("cr_t", "dst", "org", "A"), ("pr_t", "org", "dst", "D")):
    v = R[R[vap].str.startswith("SC")][["al", "fn", "org", "dst", vcol]].dropna()
    mm = v.merge(
        b[b.tipo_operacion == bt],
        left_on=["al", "fn", vap, oth],
        right_on=["aerolinea_dgac", "fn", "aeropuerto_oaci", "aeropuerto_dgac_orig_dest"],
    )
    mm["d"] = (mm[vcol] - mm.utc).dt.total_seconds() / 60
    mm = mm[mm.d.abs() < 300]
    mm["h"] = (mm.d / 60).round().astype(int)
    mm["day"] = mm[vcol].dt.day
    x = mm[mm.day <= 3]
    print(bt, "Nov 1-3 2018 airline x offset")
    print(pd.crosstab(x.al, x.h).to_string())

# SBSP hour histogram by airline: Oct 29-31, Nov 1-3, Nov 6-8
d10 = load(2018, 10)


def hist(df, lo, hi, al):
    x = df[
        (df.sit == "REALIZADO")
        & (df.org == "SBSP")
        & (df.al == al)
        & (df.pr_t >= lo)
        & (df.pr_t < hi)
    ]
    return x.pr_t.dt.hour.value_counts().reindex(range(24), fill_value=0).tolist()


for al in ("TAM", "GLO", "AZU"):
    print(al, "SBSP dep hours Oct 29-31", hist(d10, "2018-10-29", "2018-11-01", al))
    print(al, "SBSP dep hours Nov 1-3  ", hist(df, "2018-11-01", "2018-11-04", al))
    print(al, "SBSP dep hours Nov 6-8  ", hist(df, "2018-11-06", "2018-11-09", al))

# scheduled vs actual departure of one fixed TAM flight across days
x = df[(df.al == "TAM") & (df.org == "SBSP") & (df.dst == "SBRJ")].sort_values("pp_t")
f = x.flt.value_counts().index[0]
print("TAM", f, "SBSP-SBRJ sched/actual dep by day:")
print(x[x.flt == f][["pp", "pr"]].head(8).to_string())
