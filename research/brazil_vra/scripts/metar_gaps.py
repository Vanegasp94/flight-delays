"""Hourly coverage and gaps of the SBGR METAR history from Iowa State Mesonet, from 2019-01-01.

Reconstructed from an inline command run in the session (it was not saved as a
file at the time).
"""

import collections
import csv
import datetime as dt

from _common import SBGR_METAR

with open(SBGR_METAR) as fh:
    rows = list(csv.DictReader(fh))
t = sorted(dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M") for r in rows)
print("reports", len(t), "first", t[0], "last", t[-1])
hrs = set(x.replace(minute=0) for x in t)
start = dt.datetime(2019, 1, 1)
end = t[-1].replace(minute=0)
allh = [
    start + dt.timedelta(hours=i) for i in range(int((end - start).total_seconds() // 3600) + 1)
]
miss = [h for h in allh if h not in hrs]
print(
    "hours in span",
    len(allh),
    "hours with >=1 report",
    len(allh) - len(miss),
    "missing hours",
    len(miss),
    f"{len(miss) / len(allh):.3%}",
)
by = collections.Counter(h.year for h in miss)
print("missing hours by year", sorted(by.items()))
gaps = []
run = []
for h in miss:
    if run and h - run[-1] == dt.timedelta(hours=1):
        run.append(h)
    else:
        if run:
            gaps.append((len(run), run[0]))
        run = [h]
if run:
    gaps.append((len(run), run[0]))
print("gap count", len(gaps), "longest:", sorted(gaps, reverse=True)[:8])
print("reports per year", sorted(collections.Counter(x.year for x in t).items()))
print("sample", rows[0]["metar"][:90])
