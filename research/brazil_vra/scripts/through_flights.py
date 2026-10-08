"""Through-flight gap test at western airports, July 2026 (refined version of tz1.py part C).

For the same airline and flight number, pairs an arrival at X with a departure
from X when the gap is between -180 and +180 minutes. Reconstructed from an
inline command run in the session (it was not saved as a file at the time).
"""

from _common import load

df = load(2026, 7)
R = df[df.sit == "REALIZADO"]
print(
    "Through flights (same airline+flight no): arrival at X, then departure from X within -180..+180 min"
)
for X in ["SBEG", "SBRB", "SBPV", "SBCY", "SBBV", "SBMQ", "SBSN"]:
    a = R[R.dst == X][["al", "flt", "cr_t", "org"]].dropna()
    d = R[R.org == X][["al", "flt", "pr_t", "dst"]].dropna()
    m = a.merge(d, on=["al", "flt"])
    m = m[m.org != m.dst]
    g = (m.pr_t - m.cr_t).dt.total_seconds() / 60
    g = g[(g > -180) & (g < 180)]
    if len(g):
        print(
            X,
            "n",
            len(g),
            "negative",
            int((g < 0).sum()),
            "min",
            g.min(),
            "median",
            g.median(),
            "max",
            g.max(),
        )
print(
    "SBRB dep hours in file",
    sorted(R[R.org == "SBRB"].pr_t.dt.hour.value_counts().to_dict().items()),
)
x = R[(R.org == "SBRB") & (R.dst == "SBBR")]
print(
    "SBRB->SBBR sched block",
    ((x.cp_t - x.pp_t).dt.total_seconds() / 60)
    .describe()[["count", "min", "50%", "max"]]
    .to_dict(),
)
x = R[(R.org == "SBBR") & (R.dst == "SBRB")]
print(
    "SBBR->SBRB sched block",
    ((x.cp_t - x.pp_t).dt.total_seconds() / 60)
    .describe()[["count", "min", "50%", "max"]]
    .to_dict(),
)
