"""Describe Z-prefix rows, origin == destination rows and near-duplicate rows in the July 2026 file."""

import pandas as pd
from _common import load

df = load(2026, 7)
raw = ["al", "flt", "di", "tl", "org", "dst", "pp", "pr", "cp", "cr", "sit", "just"]
print("rows", len(df))
z = df[df.flt.str.startswith("Z")]
print("\n== Z-prefix rows:", len(z))
print("by airline:", z.al.value_counts().head(12).to_dict())
print("DI x Tipo Linha:")
print(pd.crosstab(z.di, z.tl, margins=True).to_string())
print(
    "situacao",
    z.sit.value_counts().to_dict(),
    "| scheduled dep null:",
    (z.pp == "null").sum(),
    "| org==dst:",
    (z.org == z.dst).sum(),
)
print("for comparison non-Z rows DI:", df[~df.flt.str.startswith("Z")].di.value_counts().to_dict())
# does the Z flight share number+day with a non-Z row of the same airline?
df["day"] = df.pp_t.fillna(df.pr_t).dt.date
df["num"] = df.flt.str.lstrip("Z")
k = df[~df.flt.str.startswith("Z")].groupby(["al", "num", "day"]).size().rename("n_nonZ")
zz = df[df.flt.str.startswith("Z")].join(k, on=["al", "num", "day"])
print(
    "Z rows whose airline+number(without Z)+Brasília date also exists as a non-Z row:",
    zz.n_nonZ.notna().sum(),
    "of",
    len(zz),
)
print(
    "Z rows with Z-number repeated same airline/day:",
    (zz.groupby(["al", "flt", "day"]).flt.transform("size") > 1).sum(),
)
print("sample:")
print(z[raw].sample(6, random_state=2).to_string())
od = df[df.org == df.dst]
print("\n== origin==destination rows:", len(od))
print("by airline:", od.al.value_counts().to_dict())
print("DI x Tipo Linha:")
print(pd.crosstab(od.di, od.tl, margins=True).to_string())
print(
    "Z-prefix:",
    od.flt.str.startswith("Z").sum(),
    "| sched null:",
    (od.pp == "null").sum(),
    "| situacao",
    od.sit.value_counts().to_dict(),
)
blk = (od.cr_t - od.pr_t).dt.total_seconds() / 60
print(
    "actual block min quantiles 5/25/50/75/95:",
    blk.quantile([0.05, 0.25, 0.5, 0.75, 0.95]).round(0).tolist(),
    "top airports",
    od.org.value_counts().head(6).to_dict(),
)
print(od[raw].sample(5, random_state=3).to_string())
# near-duplicates: same airline, flight, origin, destination, and (scheduled dep or, if null, actual dep) raw string
df["depkey"] = df.pp.where(df.pp != "null", df.pr)
key = ["al", "flt", "org", "dst", "depkey"]
g = df.groupby(key).flt.transform("size")
nd = df[g > 1].copy()
print(
    "\n== near-duplicate rows (all members of groups):",
    len(nd),
    "groups:",
    nd.groupby(key).ngroups,
    "extra rows:",
    len(nd) - nd.groupby(key).ngroups,
)
print("group sizes:", nd.groupby(key).size().value_counts().to_dict())
diff = nd.groupby(key)[["di", "tl", "pp", "pr", "cp", "cr", "sit", "just"]].nunique().gt(1)
print("groups in which each column differs:", diff.sum().to_dict())
pat = diff.apply(
    lambda r: "+".join(c for c in diff.columns if r[c]) or "IDENTICAL", axis=1
).value_counts()
print("difference patterns (groups):", pat.to_dict())
print("by airline (rows):", nd.al.value_counts().head(12).to_dict())
print(
    "Tipo Linha (rows):",
    nd.tl.value_counts().to_dict(),
    "| DI:",
    nd.di.value_counts().to_dict(),
    "| situacao:",
    nd.sit.value_counts().to_dict(),
)
print(
    "situacao combos per group:",
    nd.groupby(key).sit.apply(lambda s: "+".join(sorted(s))).value_counts().to_dict(),
)
print(
    "fractional-second scheduled time in near-dup rows:",
    nd.pp.str.contains(r"\.").sum(),
    "of",
    len(nd),
    "| in whole file",
    df.pp.str.contains(r"\.").sum(),
)
fr = df[df.pp.str.contains(r"\.")]
print(
    "fractional rows: Tipo Linha",
    fr.tl.value_counts().to_dict(),
    "DI",
    fr.di.value_counts().to_dict(),
    "airlines",
    fr.al.value_counts().head(8).to_dict(),
)
# typical differing example groups
for p in pat.index[:4]:
    kk = diff.index[
        (
            diff.apply(lambda r: "+".join(c for c in diff.columns if r[c]) or "IDENTICAL", axis=1)
            == p
        ).values
    ][0]
    ex = nd[(nd[key] == pd.Series(kk, index=key)).all(axis=1)]
    print("example pattern", p)
    print(ex[raw].to_string())


# time difference between actual deps within group
def spread(s):
    return (s.max() - s.min()).total_seconds() / 60


sp = nd[nd.sit == "REALIZADO"].groupby(key).pr_t.agg(spread)
print(
    "spread of actual departure within group (min) quantiles:",
    sp.quantile([0.1, 0.5, 0.9]).tolist(),
    "share ==0:",
    (sp == 0).mean(),
)
