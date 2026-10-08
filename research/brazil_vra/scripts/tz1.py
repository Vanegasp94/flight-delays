"""Time-zone tests on the July 2026 VRA file.

A: hour-of-day histograms of actual departures; B: block-time symmetry between
airports in different Brazilian time zones; C: through-flight gaps (same-day match).
"""

import numpy as np
from _common import load

df = load(2026, 7)
R = df[df.sit == "REALIZADO"]
print("A. Hour-of-day of Partida Real, by origin (count per hour 0..23)")
for ap in ["SBSP", "SBRJ", "SBGR", "SBEG", "SBRB"]:
    h = R[R.org == ap].pr_t.dt.hour.value_counts().reindex(range(24), fill_value=0)
    print(ap, h.tolist())
print(
    "A2. Chegada Real hour at SBSP",
    R[R.dst == "SBSP"].cr_t.dt.hour.value_counts().reindex(range(24), fill_value=0).tolist(),
)
print("\nB. Median block minutes each direction (sched n / sched med / actual med)")


def blk(a, b):
    x = R[(R.org == a) & (R.dst == b)]
    s = ((x.cp_t - x.pp_t).dt.total_seconds() / 60).dropna()
    r = ((x.cr_t - x.pr_t).dt.total_seconds() / 60).dropna()
    return len(x), (s.median() if len(s) else None), (r.median() if len(r) else None)


for a, b in [
    ("SBGR", "SBEG"),
    ("SBBR", "SBEG"),
    ("SBBR", "SBRB"),
    ("SBGR", "SBPV"),
    ("SBBR", "SBPV"),
    ("SBGR", "SBCY"),
    ("SBGR", "SBCG"),
    ("SBEG", "SBRB"),
    ("SBGR", "SBBR"),
    ("SBGR", "SBRF"),
    ("SBGR", "LPPT"),
    ("SBGR", "KMIA"),
    ("SBGR", "SCEL"),
    ("SBGR", "SAEZ"),
    ("SBEG", "KMIA"),
    ("SBEG", "MPTO"),
]:
    print(f"{a}->{b}", blk(a, b), f"| {b}->{a}", blk(b, a))
print(
    "\nC. Through flights: same airline+flight no, arrival at X then next departure from X (minutes gap, actual times)"
)
for X in ["SBEG", "SBRB", "SBPV", "SBCY", "SBCG", "SBBV", "SBBR", "SBCF"]:
    a = R[R.dst == X][["al", "flt", "cr_t", "org"]].dropna()
    d = R[R.org == X][["al", "flt", "pr_t", "dst"]].dropna()
    a["day"] = a.cr_t.dt.date
    d["day"] = d.pr_t.dt.date
    m = a.merge(d, on=["al", "flt", "day"])
    m = m[m.org != m.dst]
    g = (m.pr_t - m.cr_t).dt.total_seconds() / 60
    if len(g):
        print(
            X,
            "n",
            len(g),
            "neg",
            int((g < 0).sum()),
            "0-19",
            int(((g >= 0) & (g < 20)).sum()),
            "quantiles 5/25/50/75/95",
            np.percentile(g, [5, 25, 50, 75, 95]).round(0).tolist(),
        )
    else:
        print(X, "n 0")
