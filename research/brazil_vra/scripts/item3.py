"""Count non-N/A Codigo Justificativa rows in every full monthly file, 2019-01 to 2026-07."""

import os

import pandas as pd
from _common import vra_path

print("month | rows | non-N/A justificativa rows | % N/A | top non-N/A codes | distinct values")
for y in range(2019, 2027):
    for m in range(1, 13):
        fn = vra_path(y, m)
        if not os.path.exists(fn):
            if (y, m) <= (2026, 7):
                print(f"{y}-{m:02d} MISSING")
            continue
        df = pd.read_csv(
            fn,
            sep=";",
            skiprows=1,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
            usecols=[10, 11],
        )
        df.columns = ["sit", "just"]
        vc = df.just.value_counts()
        na = vc.get("N/A", 0)
        print(
            f"{y}-{m:02d} | {len(df)} | {len(df) - na} | {na / len(df):.2%} | {vc.drop('N/A', errors='ignore').head(4).to_dict()} | {len(vc)} | canc={int((df.sit == 'CANCELADO').sum())}"
        )
