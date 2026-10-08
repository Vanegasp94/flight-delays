"""Presence pattern of scheduled/actual times in REALIZADO rows per year, and departure-difference shares."""

import os

from _common import load, vra_path

print(
    "REALIZADO rows by presence of (sched dep, actual dep, sched arr, actual arr); 1=present 0=empty/null"
)
for y in range(2010, 2027):
    m = 8 if y == 2014 else 7
    if not os.path.exists(vra_path(y, m)):
        print(y, m, "MISSING")
        continue
    df = load(y, m)
    R = df[df.sit.str.upper() == "REALIZADO"]
    pat = (
        R.pp_t.notna().astype(int).astype(str)
        + R.pr_t.notna().astype(int).astype(str)
        + R.cp_t.notna().astype(int).astype(str)
        + R.cr_t.notna().astype(int).astype(str)
    ).value_counts()
    d = R[R.pp_t.notna() & R.pr_t.notna()]
    dl = (d.pr_t - d.pp_t).dt.total_seconds() / 60
    eq = d[d.pp_t == d.pr_t]
    print(
        f"{y}-{m:02d} patterns {pat.to_dict()} | dep diff: ==0 {(dl == 0).mean():.1%}, 1-4min late {((dl > 0) & (dl < 5)).mean():.1%}, early {(dl < 0).mean():.1%}, >15 late {(dl > 15).mean():.1%} | just among exact-equal rows: {eq.just.value_counts().head(3).to_dict()}"
    )
    if y in (2016, 2017):
        x = R[R.pp_t.notna() & R.pr_t.isna()]
        print(
            "     sched present/actual missing: just",
            x.just.value_counts().head(4).to_dict(),
            "airlines",
            x.al.value_counts().head(5).to_dict(),
            "| both present: just",
            d.just.value_counts().head(4).to_dict(),
            "airlines",
            d.al.value_counts().head(5).to_dict(),
        )
