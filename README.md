# flight-delays

A personal project for analysing and predicting flight delays. The intended main
scope is US flights, using BTS On-Time Performance data and aviation weather
(METAR/TAF). Brazil (ANAC VRA) is a possible later extension.

## Status

This repository is at the exploration stage. There is no modelling, prediction,
dbt model or app code yet. What exists today:

- project tooling and folder structure;
- an ingestion script for BTS On-Time Performance monthly files
  (`ingestion/bts_otp.py`), loading raw rows into the local DuckDB database;
- one exploration notebook profiling the busiest domestic airport pairs
  (`notebooks/01_bts_otp_route_profile.ipynb`);
- an empty dbt project (no models);
- research notes and scripts from a data-availability check of Latin American
  on-time performance sources, mainly Brazil's ANAC VRA
  (see [docs/research/brazil-vra.md](docs/research/brazil-vra.md)).

## Layout

| Path | Purpose |
|---|---|
| `src/flight_delays/` | Python package (currently only configuration) |
| `ingestion/` | Ingestion scripts (`bts_otp.py`) |
| `dbt/` | dbt project on DuckDB: `models/staging`, `models/intermediate`, `models/marts` (empty) |
| `notebooks/` | Exploration notebooks |
| `app/` | Streamlit app (empty) |
| `tests/` | pytest tests |
| `research/` | Research scripts; `research/brazil_vra/` holds the VRA evaluation |
| `docs/decisions/` | Architecture decision records and their template |
| `docs/research/` | Research write-ups |
| `data/` | Local raw and intermediate data. Git-ignored; never committed |

## Setup

Requirements: [uv](https://docs.astral.sh/uv/). uv installs the Python version
pinned in `.python-version`.

```bash
uv sync
```

Optional local configuration:

```bash
cp .env.example .env
```

The variables and their defaults are listed in `.env.example`. None are secret.
To use the file, prefix commands with `uv run --env-file .env`.

## Common commands

Lint and format:

```bash
uv run ruff check .
uv run ruff format .
```

Tests:

```bash
uv run pytest
```

Check the dbt connection (run from the repository root; creates
`data/flight_delays.duckdb` if it does not exist):

```bash
uv run dbt debug --project-dir dbt --profiles-dir dbt
```

Download BTS On-Time Performance data (January 2023 to the latest published
month, about 1.5 GB of zip files) and load it into DuckDB:

```bash
uv run python ingestion/bts_otp.py
```

Re-run the exploration notebook against the local database:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/01_bts_otp_route_profile.ipynb
```

## Data policy

Downloaded datasets and anything derived from them stay out of git. `data/`,
`_rescue/` and common data file types (`*.csv`, `*.parquet`, `*.duckdb`, ...)
are ignored in `.gitignore`. Scripts download what they need from the original
sources.

## Decisions

Architecture decisions are recorded in `docs/decisions/`. Start from
[`0000-template.md`](docs/decisions/0000-template.md).
