# CLAUDE.md

Rules for any session working in this repository.

## Purpose

A personal flight delay recommendation tool. The user inputs route, airline,
date and time; the tool returns a risk level (green / amber / red) with an
explanation.

- Scope: US flights, using BTS On-Time Performance data plus aviation weather
  (METAR/TAF).
- Brazil (ANAC VRA) is a possible later extension. Existing research is in
  `docs/research/brazil-vra.md`.
- No scope additions without a decision record in `docs/decisions/`.

The phases are in `docs/roadmap.md`.

## Architecture layers and boundaries

| Layer | Where | Responsibility |
|---|---|---|
| Ingestion | `ingestion/` (Python) | Downloads raw data |
| Transformation | `dbt/` (dbt on DuckDB) | Staging, intermediate and marts models |
| Model | training and scoring code | Training and scoring |
| App | `app/` (Streamlit) | Display |

The app only reads prepared outputs and displays them. It never computes
features or business logic.

See `docs/decisions/0001-layered-architecture-app-display-only.md`.

## Workflow

- Never commit to `main`.
- One branch per task, with small focused changes.
- Push the branch and stop. The owner reviews and merges the pull request;
  do not open or merge pull requests.
- No attribution or `Co-Authored-By` lines in commits or pull requests.

## Code

- `uv` for dependencies, `ruff` for lint and format, `pytest` for tests.
- Type hints on public functions.
- New code comes with tests.
- dbt models come with dbt tests.

## Data

- Never commit data files.
- Never silently clean, drop or adjust data. Flag inconsistencies and report
  them.
- Anything not verified must be marked as not verified.

## Reserved for the owner

Do not implement these unless explicitly asked:

- METAR/TAF parsing logic.
- The risk level (traffic light) logic.

Reviewing them, or writing tests for them, is fine when asked.

## Research scripts

Scripts in `research/` are kept as-is for reproducibility. They are not part of
the product code.

## When finishing a task

- List every file changed.
- Explain any choice that was not specified in the request.
