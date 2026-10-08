# dbt project

dbt-core project using the dbt-duckdb adapter. It was created with `dbt init`;
the example models were removed and there are no models yet.

Model folders:

- `models/staging/` - one model per raw source, light renaming and typing (views)
- `models/intermediate/` - joins and reusable transformations (views)
- `models/marts/` - analysis-ready tables

Run dbt from the repository root so the default database path
(`data/flight_delays.duckdb`) resolves:

```bash
uv run dbt debug --project-dir dbt --profiles-dir dbt
```
