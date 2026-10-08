"""Extent of the placeholder corruption in the February and March 2020 VRA files.

Reconstructed from inline commands run in the session (they were not saved as
files at the time).
"""

import pandas as pd
from _common import vra_path

PLACEHOLDER = "Microsoft.SqlServer.Dts.Pipeline.BlobColumn"

for m in (2, 3):
    fn = vra_path(2020, m)
    with open(fn, encoding="utf-8-sig") as fh:
        print(fh.readline().strip())
    df = pd.read_csv(
        fn, sep=";", skiprows=1, dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )
    t = df.columns[6:11]
    print(
        f"2020-{m:02d} rows",
        len(df),
        "| distinct full rows",
        len(df.drop_duplicates()),
        "| time/status cols distinct values:",
        {c: df[c].nunique() for c in t},
        "| rows where all five == BlobColumn placeholder:",
        (df[t] == PLACEHOLDER).all(axis=1).sum(),
    )
    print(
        "   multiplicity of identical rows (top):",
        df.groupby(list(df.columns)).size().value_counts().sort_index().head(6).to_dict(),
    )
    just = df[df.columns[11]]
    vc = just.value_counts()
    na = vc.get("N/A", 0)
    print(
        "   justificativa: N/A",
        na,
        f"({na / len(df):.2%}) distinct",
        len(vc),
        "top",
        vc.head(6).to_dict(),
    )
