# 0001. Layered architecture with the app limited to display

- **Status:** Accepted
- **Date:** 2026-10-08

## Context

The project is a personal flight delay recommendation tool: the user inputs
route, airline, date and time, and the tool returns a risk level
(green / amber / red) with an explanation. It uses BTS On-Time Performance data
plus aviation weather (METAR/TAF).

Producing that answer involves several kinds of work: downloading raw data,
transforming it, training and scoring, and showing the result. The project needs
a rule for where each kind of work lives, and in particular for what the app is
allowed to do.

## Decision

The project has four layers, each with one responsibility:

1. **Ingestion** - Python. Downloads raw data.
2. **Transformation** - dbt on DuckDB, in staging, intermediate and marts
   models.
3. **Model** - training and scoring.
4. **App** - Streamlit.

The app only reads prepared outputs and displays them. It never computes
features or business logic.

## Alternatives considered

- **Letting the app compute features or business logic itself.** Not chosen:
  the app is limited to reading prepared outputs and displaying them.

No other alternatives were recorded when this decision was made.

## Consequences

- Features and business logic must be produced in the transformation or model
  layer before the app can show them. A change to either never happens in the
  app.
- The app depends on prepared outputs existing; it has nothing to show until
  the earlier layers have run.
- dbt models come with dbt tests, and new code comes with tests, so each layer
  is tested where its logic lives.
- METAR/TAF parsing logic and the risk level (traffic light) logic are reserved
  for the project owner. This record says which side of the app boundary they
  sit on (not in the app), not who writes them.
