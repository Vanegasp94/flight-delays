"""Round-1 profile of the July 2026 VRA file (second pass): timestamp shapes, null patterns, outliers.

Note: the delay statistics at the end exclude rows whose scheduled time has the
.100000000 suffix, because strptime %f accepts at most six digits.
"""

import collections
import csv
import datetime as dt
import re

from _common import vra_path

f = open(vra_path(2026, 7), encoding="utf-8-sig", newline="")
f.readline()
r = csv.reader(f, delimiter=";")
hdr = next(r)
rows = list(r)
I = {h: i for i, h in enumerate(hdr)}
T = ["Partida Prevista", "Partida Real", "Chegada Prevista", "Chegada Real"]
shape = collections.Counter()
exs = {}
for row in rows:
    for h in T:
        s = re.sub(r"\d", "9", row[I[h]])
        shape[(h, s)] += 1
        exs.setdefault((h, s), row[I[h]])
for k, v in sorted(shape.items()):
    print(k, v, "e.g.", exs[k])
pat = collections.Counter()
for row in rows:
    pat[(row[I["Situação Voo"]],) + tuple("null" if row[I[h]] == "null" else "val" for h in T)] += 1
print("situacao x (PP,PR,CP,CR):")
for k, v in pat.most_common():
    print("  ", k, v)
# DI x null scheduled
c = collections.Counter(
    (row[I["Código Autorização (DI)"]], row[I["Partida Prevista"]] == "null") for row in rows
)
print("DI x sched-null:", sorted(c.items()))
c = collections.Counter(
    row[I["Código Autorização (DI)"]]
    for row in rows
    if row[I["ICAO Aeródromo Origem"]] == row[I["ICAO Aeródromo Destino"]]
)
print("orig==dest by DI", c)
c = collections.Counter(
    row[I["Código Autorização (DI)"]] for row in rows if not row[I["Número Voo"]].isdigit()
)
print(
    "non-numeric flight no by DI",
    c,
    collections.Counter(re.sub(r"\d", "9", row[I["Número Voo"]]) for row in rows),
)


def p(s):
    for fm in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s, fm)
        except:
            pass


iss = collections.Counter()
ex = collections.defaultdict(list)
dep = []
arr = []
yrs = collections.Counter()
for row in rows:
    P = [p(row[I[h]]) for h in T]
    for h, v in zip(T, P):
        if v:
            yrs[(h, v.strftime("%Y-%m"))] += 1

    def flag(k):
        iss[k] += 1
        if len(ex[k]) < 3:
            ex[k].append(row)

    if P[1] and P[3]:
        d = (P[3] - P[1]).total_seconds() / 60
        if d < 0:
            flag("actual arr < actual dep")
        elif d == 0:
            flag("actual arr == actual dep")
        elif d > 20 * 60:
            flag("actual block > 20h")
        elif d < 10:
            flag("actual block < 10 min")
    if P[0] and P[2]:
        d = (P[2] - P[0]).total_seconds() / 60
        if d < 0:
            flag("sched arr < sched dep")
        elif d == 0:
            flag("sched arr == sched dep")
        elif d > 20 * 60:
            flag("sched block > 20h")
    if P[0] and P[1]:
        d = (P[1] - P[0]).total_seconds() / 60
        dep.append(d)
        if abs(d) > 24 * 60:
            flag("|dep delay| > 24h")
        elif d < -60:
            flag("departed > 60 min early")
        elif d > 12 * 60:
            flag("dep delay 12-24h")
    if P[2] and P[3]:
        d = (P[3] - P[2]).total_seconds() / 60
        arr.append(d)
        if d < -120:
            flag("arrived > 120 min early")
for k, v in iss.most_common():
    print(k, v)
    [print("    ", e) for e in ex[k]]
print("month distribution per time column:")
[print("  ", k, v) for k, v in sorted(yrs.items()) if not k[1] == "2026-07"]
import statistics as st

for nm, a in (("dep", dep), ("arr", arr)):
    a = sorted(a)
    print(
        nm,
        "n",
        len(a),
        "min",
        a[0],
        "p1",
        a[len(a) // 100],
        "med",
        st.median(a),
        "p99",
        a[len(a) * 99 // 100],
        "max",
        a[-1],
        "share>15min",
        sum(x > 15 for x in a) / len(a),
    )
full = collections.Counter(tuple(r) for r in rows)
d = [(k, v) for k, v in full.items() if v > 1]
print("exact dup groups", len(d))
[print("   ", v, k) for k, v in d[:3]]
