"""Profile the most recent month of Chile's JAC flight log (Bitacora de Vuelos)."""

import pyarrow.parquet as pq
from _common import CHILE_PARQUET

pf = pq.ParquetFile(CHILE_PARQUET)
print("total rows", pf.metadata.num_rows)
print(pf.schema_arrow)
df = pf.read().to_pandas()
t = df["dt_operacion"]
print("range", t.min(), t.max())
ym = t.dt.strftime("%Y-%m")
vc = ym.value_counts().sort_index()
print("first months", vc.head(3).to_dict(), "last months", vc.tail(4).to_dict())
last = vc.index[-1]
# use last complete month
m = df[ym == last].copy()
print("PROFILE MONTH", last, "rows", len(m), "max dt", m.dt_operacion.max())
for c in m.columns:
    s = m[c]
    nul = s.isna().sum()
    emp = (s.astype(str).str.strip() == "").sum() if s.dtype == object else 0
    print(f"{c:28s} null={nul:6d} ({nul / len(m):.2%}) empty={emp} distinct={s.nunique()}")
for c in ["tipo_operacion", "actividad_cod", "es_internacional"]:
    print(c, m[c].value_counts(dropna=False).head(15).to_dict())
for c in ["aerolinea_dgac", "modelo_avion", "aeropuerto_oaci", "aeropuerto_dgac_orig_dest"]:
    print(
        c,
        m[c].value_counts(dropna=False).head(8).to_dict(),
        "lens",
        m[c].astype(str).str.len().value_counts().to_dict(),
    )
print(
    "matricula samples",
    m.matricula.dropna().sample(8, random_state=1).tolist(),
    "len dist",
    m.matricula.astype(str).str.len().value_counts().head(8).to_dict(),
)
print(
    "numero_vuelo samples", m.numero_vuelo.dropna().astype(str).sample(8, random_state=1).tolist()
)
print("exact dup rows", m.duplicated().sum())
print(
    "same airport as orig/dest",
    (m.aeropuerto_oaci == m.aeropuerto_dgac_orig_dest).sum(),
    m[m.aeropuerto_oaci == m.aeropuerto_dgac_orig_dest].tipo_operacion.value_counts().to_dict(),
)
print("pmd describe", m.pmd.describe().to_dict(), "pmd<=0", (m.pmd <= 0).sum())
print(
    "seconds dist",
    t[ym == last].dt.second.value_counts().head(3).to_dict(),
    "minute==0 share",
    (t[ym == last].dt.minute == 0).mean(),
)
print(
    "modelo null by actividad",
    m[m.modelo_avion.isna()].actividad_cod.value_counts().head(5).to_dict(),
)
print(
    "numero_vuelo null by actividad",
    m[m.numero_vuelo.isna()].actividad_cod.value_counts().head(5).to_dict(),
)
print(m.head(5).to_string())
