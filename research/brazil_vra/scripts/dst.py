"""Behaviour of VRA times around the 2018/2019 daylight-saving transitions."""

import pandas as pd
from _common import load, load_chile_brazil

b = load_chile_brazil()


def offs(y, m):
    df = load(y, m)
    R = df[df.sit == "REALIZADO"].copy()
    R["fn"] = pd.to_numeric(R.flt, errors="coerce")
    v = R[R.dst.str.startswith("SC")][["al", "fn", "org", "dst", "cr_t"]].dropna()
    mm = v.merge(
        b[b.tipo_operacion == "A"],
        left_on=["al", "fn", "dst", "org"],
        right_on=["aerolinea_dgac", "fn", "aeropuerto_oaci", "aeropuerto_dgac_orig_dest"],
    )
    mm["d"] = (mm.cr_t - mm.utc).dt.total_seconds() / 60
    mm = mm[mm.d.abs() < 600]
    mm["h"] = (mm.d / 60).round().astype(int)
    mm["day"] = mm.cr_t.dt.date
    return df, mm


for y, m, lo, hi in (
    (2018, 10, "2018-10-14", "2018-11-01"),
    (2018, 11, "2018-11-01", "2018-11-07"),
    (2019, 2, "2019-02-14", "2019-02-20"),
):
    df, mm = offs(y, m)
    x = mm[(mm.cr_t >= lo) & (mm.cr_t < hi)]
    print(f"== {y}-{m:02d}: VRA arrival minus Chile-log UTC, rounded hours, by day")
    print(pd.crosstab(x.day, x.h).to_string())
    print("by airline:")
    print(pd.crosstab(x.al, x.h).to_string())
# whole Oct 2018 by airline
df, mm = offs(2018, 10)
print("== Oct 2018 full month by airline x offset")
print(pd.crosstab(mm.al, mm.h).to_string())
x = mm[mm.h == -2]
print("Oct 2018 offset -2 rows by day:", x.day.value_counts().sort_index().to_dict())
print("\n== Transition hours")
d11 = load(2018, 11)
d2 = load(2019, 2)
d218 = load(2018, 2)
for c in ["pp_t", "pr_t", "cp_t", "cr_t"]:
    n = ((d11[c] >= "2018-11-04 00:00") & (d11[c] < "2018-11-04 01:00")).sum()
    n0 = ((d11[c] >= "2018-11-11 00:00") & (d11[c] < "2018-11-11 01:00")).sum()
    print(
        f"2018-11-04 00:00-00:59 (hour skipped at DST start) {c}: {n} rows; same hour one week later: {n0}"
    )
for nm, df, day in (("2019-02-16", d2, "2019-02-16"), ("2018-02-17", d218, "2018-02-17")):
    for c in ["pr_t", "cr_t"]:
        n = ((df[c] >= day + " 23:00") & (df[c] <= day + " 23:59:59")).sum()
        wk = pd.Timestamp(day) - pd.Timedelta(days=7)
        n0 = ((df[c] >= wk + pd.Timedelta(hours=23)) & (df[c] < wk + pd.Timedelta(hours=24))).sum()
        print(
            f"{nm} 23:00-23:59 (hour repeated at DST end) {c}: {n} rows; same hour one week earlier: {n0}"
        )


# block times across transitions
def acr(df, t0, label):
    R = df[df.sit == "REALIZADO"]
    x = R[
        (R.pr_t < t0) & (R.cr_t >= t0) & (R.pr_t > pd.Timestamp(t0) - pd.Timedelta(hours=14))
    ].copy()
    x["act"] = (x.cr_t - x.pr_t).dt.total_seconds() / 60
    x["sch"] = (x.cp_t - x.pp_t).dt.total_seconds() / 60
    # compare with median actual block of same route in rest of month
    med = (
        R.assign(act=(R.cr_t - R.pr_t).dt.total_seconds() / 60)
        .groupby(["org", "dst"])
        .act.median()
        .rename("route_med")
    )
    x = x.join(med, on=["org", "dst"])
    x["diff"] = x.act - x.route_med
    print(
        f"{label}: flights airborne across {t0}: n={len(x)}; actual block minus route median: median {x['diff'].median():.0f} min; quantiles 10/90 {x['diff'].quantile(0.1):.0f}/{x['diff'].quantile(0.9):.0f}; sched block minus route median: {(x.sch - x.route_med).median():.0f}"
    )
    neg = R[((R.cr_t - R.pr_t).dt.total_seconds() < 0)]
    print("   negative actual block rows in month:", len(neg))


acr(d11, "2018-11-04 01:00", "DST start 2018-11-04 (00:00->01:00)")
acr(d2, "2019-02-17 00:00", "DST end 2019-02-17 (00:00->23:00)")
acr(d218, "2018-02-18 00:00", "DST end 2018-02-18 (00:00->23:00)")
acr(d11, "2018-11-18 00:30", "control (ordinary Sunday 2018-11-18 00:30)")
# block symmetry during DST: SBGR<->SBRF (Recife did not observe DST), SBGR<->SBEG
for nm, df, lo, hi in (
    ("Nov 5-30 2018 (DST)", d11, "2018-11-05", "2018-12-01"),
    ("Feb 1-15 2019 (DST)", d2, "2019-02-01", "2019-02-16"),
    ("Feb 18-28 2019 (no DST)", d2, "2019-02-18", "2019-03-01"),
):
    R = df[(df.sit == "REALIZADO") & (df.pr_t >= lo) & (df.pr_t < hi)]
    for a, bb in (("SBGR", "SBRF"), ("SBGR", "SBEG"), ("SBBR", "SBEG"), ("SBGR", "SBFZ")):
        f = lambda o, d_: (
            (
                R[(R.org == o) & (R.dst == d_)].cr_t - R[(R.org == o) & (R.dst == d_)].pr_t
            ).dt.total_seconds()
            / 60
        )
        x, yv = f(a, bb), f(bb, a)
        print(
            f"{nm} {a}->{bb} n={len(x)} med actual block {x.median():.0f} | {bb}->{a} n={len(yv)} med {yv.median():.0f}"
        )
