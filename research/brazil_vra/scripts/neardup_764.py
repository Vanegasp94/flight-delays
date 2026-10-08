"""Reproduce the first-pass count of 764 "near-duplicate" rows and show what it is made of.

The first-pass key used the raw scheduled departure, which is the literal string
``null`` for unscheduled flights, so those rows collapsed into one group per
airline/flight/route. Reconstructed from an inline command run in the session
(it was not saved as a file at the time).
"""

import pandas as pd
from _common import load

df = load(2026, 7)
# key as used in the first-pass count (scheduled dep raw string; 'null' when unscheduled)
key = ["al", "flt", "org", "dst", "pp"]
g = df.groupby(key).flt.transform("size")
nd = df[g > 1]
print(
    "rows in groups",
    len(nd),
    "groups",
    nd.groupby(key).ngroups,
    "extra rows",
    len(nd) - nd.groupby(key).ngroups,
)
print(
    "of the extra rows, scheduled dep == null:",
    (len(nd[nd.pp == "null"]) - nd[nd.pp == "null"].groupby(key).ngroups),
)
u = nd[nd.pp == "null"]
print(
    "null-sched groups: rows",
    len(u),
    "groups",
    u.groupby(key).ngroups,
    "| group size dist",
    u.groupby(key).size().value_counts().sort_index().to_dict(),
)
print(
    "distinct actual-departure dates per group (quantiles):",
    u.groupby(key)
    .pr_t.apply(lambda s: s.dt.date.nunique())
    .describe()[["min", "50%", "max"]]
    .to_dict(),
)
print(
    "groups where two rows share the same actual departure timestamp:",
    (u.groupby(key).pr.apply(lambda s: s.duplicated().any())).sum(),
)
print("airlines", u.al.value_counts().head(10).to_dict())
print(
    "Tipo Linha",
    u.tl.value_counts().to_dict(),
    "DI",
    u.di.value_counts().to_dict(),
    "Z-prefix",
    u.flt.str.startswith("Z").sum(),
)
d = u.groupby(key)[["di", "tl", "pr", "cr", "sit"]].nunique().gt(1).sum()
print("columns differing within groups (groups count):", d.to_dict())
k0 = u.groupby(key).size().idxmax()
print("largest group example:")
print(
    u[(u[key] == pd.Series(k0, index=key)).all(axis=1)][
        ["al", "flt", "di", "tl", "org", "dst", "pp", "pr", "cr", "sit"]
    ]
    .head(6)
    .to_string()
)
