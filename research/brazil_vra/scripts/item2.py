"""Share of REALIZADO rows where actual equals scheduled exactly, July of each year 2010-2026.

August is used for 2014 because the June and July 2014 folders are empty on the ANAC server.
"""

import os

from _common import load, vra_path

print(
    "year-month | rows | REALIZADO | REAL. with sched+actual dep | dep exact % | dep raw-string-equal % | REAL. with sched+actual arr | arr exact % | both exact % | raw time format sample"
)
for y in range(2010, 2027):
    m = 8 if y == 2014 else 7
    if not os.path.exists(vra_path(y, m)):
        print(y, m, "MISSING")
        continue
    df = load(y, m)
    R = df[df.sit.str.upper() == "REALIZADO"]
    d = R[R.pp_t.notna() & R.pr_t.notna()]
    a = R[R.cp_t.notna() & R.cr_t.notna()]
    b = R[R.pp_t.notna() & R.pr_t.notna() & R.cp_t.notna() & R.cr_t.notna()]
    unp = sum(
        (
            (df[c].str.strip() != "")
            & (df[c].str.strip().str.lower() != "null")
            & df[c + "_t"].isna()
        ).sum()
        for c in ["pp", "pr", "cp", "cr"]
    )
    print(
        f"{y}-{m:02d} | {len(df)} | {len(R)} | {len(d)} | {(d.pp_t == d.pr_t).mean():.1%} | {(d.pp == d.pr).mean():.1%} | {len(a)} | {(a.cp_t == a.cr_t).mean():.1%} | {((b.pp_t == b.pr_t) & (b.cp_t == b.cr_t)).mean():.1%} | {df.pp.iloc[0]!r} unparsed={unp} situacoes={df.sit.value_counts().to_dict()}"
    )
