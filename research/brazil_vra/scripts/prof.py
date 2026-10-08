"""Round-1 profile of the July 2026 VRA file (first pass).

Kept as run. Known flaws, documented in docs/research/brazil-vra.md: the literal
string 'null' is treated as a present value, so the 'CANCELADO with an actual
time' and 'unparseable datetime' counts are artefacts, and the near-duplicate key
collapses unscheduled flights (the 764 figure). prof2.py and item4.py supersede it.
"""

import collections
import csv
import datetime as dt

from _common import vra_path

f = open(vra_path(2026, 7), encoding="utf-8-sig", newline="")
first = f.readline().strip()
print("line1:", first)
r = csv.reader(f, delimiter=";", quotechar='"')
hdr = next(r)
print(hdr)
n = 0
empty = collections.Counter()
na = collections.Counter()
badlen = 0
cnt = {h: collections.Counter() for h in hdr}
rows = []
for row in r:
    if len(row) != len(hdr):
        badlen += 1
        continue
    n += 1
    rows.append(row)
    for h, v in zip(hdr, row):
        s = v.strip()
        if s == "":
            empty[h] += 1
        elif s.upper() in ("N/A", "NA", "NULL", "NAN", "NONE"):
            na[h] += 1
        if h not in (
            "Partida Prevista",
            "Partida Real",
            "Chegada Prevista",
            "Chegada Real",
            "Número Voo",
        ):
            cnt[h][v] += 1
print("rows", n, "badlen", badlen)
for h in hdr:
    print(
        f"{h:28s} empty={empty[h]:6d} ({empty[h] / n:.2%})  literalNA={na[h]:6d} ({na[h] / n:.2%})"
    )
for h in ("Código Autorização (DI)", "Código Tipo Linha", "Situação Voo", "Código Justificativa"):
    print(h, cnt[h].most_common(40))
for h in ("ICAO Empresa Aérea", "ICAO Aeródromo Origem", "ICAO Aeródromo Destino"):
    print(
        h,
        "distinct",
        len(cnt[h]),
        "top",
        cnt[h].most_common(8),
        "odd",
        [k for k in cnt[h] if len(k) not in ((3,) if "Empresa" in h else (4,))][:20],
    )
I = {h: i for i, h in enumerate(hdr)}


def p(s):
    try:
        return dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except:
        return None


sit = collections.Counter()
issues = collections.Counter()
ex = collections.defaultdict(list)
months = collections.Counter()
dep = []
arr = []
keys = collections.Counter()
full = collections.Counter()
for row in rows:
    pp, pr, cp, cr = [
        row[I[h]].strip()
        for h in ("Partida Prevista", "Partida Real", "Chegada Prevista", "Chegada Real")
    ]
    s = row[I["Situação Voo"]]
    j = row[I["Código Justificativa"]]
    pat = "".join("1" if x else "0" for x in (pp, pr, cp, cr))
    sit[(s, pat)] += 1
    P = [p(x) if x else None for x in (pp, pr, cp, cr)]
    for x, v in zip((pp, pr, cp, cr), P):
        if x and v is None:
            issues["unparseable datetime"] += 1
            ex["unparseable datetime"].append(row)
    ref = P[0] or P[1]
    if ref:
        months[ref.strftime("%Y-%m")] += 1

    def flag(k):
        issues[k] += 1
        if len(ex[k]) < 3:
            ex[k].append(row)

    if P[1] and P[3]:
        d = (P[3] - P[1]).total_seconds() / 60
        if d < 0:
            flag("actual arrival before actual departure")
        elif d == 0:
            flag("actual arr == actual dep")
        elif d > 20 * 60:
            flag("actual block time > 20h")
    if P[0] and P[2]:
        d = (P[2] - P[0]).total_seconds() / 60
        if d < 0:
            flag("sched arrival before sched departure")
        elif d == 0:
            flag("sched arr == sched dep")
        elif d > 20 * 60:
            flag("sched block time > 20h")
    if P[0] and P[1]:
        d = (P[1] - P[0]).total_seconds() / 60
        dep.append(d)
        if abs(d) > 24 * 60:
            flag("|dep delay| > 24h")
        elif d < -60:
            flag("departed >60 min early")
    if P[2] and P[3]:
        d = (P[3] - P[2]).total_seconds() / 60
        arr.append(d)
        if abs(d) > 24 * 60:
            flag("|arr delay| > 24h")
    if row[I["ICAO Aeródromo Origem"]] == row[I["ICAO Aeródromo Destino"]]:
        flag("origin == destination")
    if s == "CANCELADO" and (pr or cr):
        flag("CANCELADO with an actual time")
    if s == "REALIZADO" and not (pr and cr):
        flag("REALIZADO missing an actual time")
    if s == "REALIZADO" and not (pp and cp):
        flag("REALIZADO missing a scheduled time")
    full[tuple(row)] += 1
    keys[(row[0], row[1], row[4], row[5], pp or pr)] += 1
print("situacao x present(PP,PR,CP,CR):")
[print("  ", k, v) for k, v in sorted(sit.items(), key=lambda x: -x[1])]
print("months by sched(or actual) dep:", sorted(months.items()))
print(
    "exact duplicate rows:",
    sum(v - 1 for v in full.values() if v > 1),
    " dup key(airline,flt,orig,dest,dep):",
    sum(v - 1 for v in keys.values() if v > 1),
)
for k, v in issues.most_common():
    print(k, v)
    for e in ex[k][:2]:
        print("    ", e)
import statistics as st

for nm, a in (("dep delay min", dep), ("arr delay min", arr)):
    a = sorted(a)
    print(
        nm,
        "n",
        len(a),
        "min",
        a[0],
        "p1",
        a[len(a) // 100],
        "median",
        st.median(a),
        "p99",
        a[len(a) * 99 // 100],
        "max",
        a[-1],
    )
nv = collections.Counter()
for row in rows:
    v = row[I["Número Voo"]]
    nv["numeric" if v.isdigit() else "non-numeric"] += 1
print(
    "Número Voo",
    nv,
    [row[I["Número Voo"]] for row in rows if not row[I["Número Voo"]].isdigit()][:10],
)
