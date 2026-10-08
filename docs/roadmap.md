# Roadmap

The tool takes a route, airline, date and time and returns a risk level
(green / amber / red) with an explanation. It is built in phases; each version
is a working end-to-end tool. See
[decision 0002](decisions/0002-tool-first-delivery-with-historical-baseline.md).

| Phase | Summary | Status |
|---|---|---|
| Phase 0 | Repo setup, route profiling, route selection | Done |
| v0 | End-to-end tool on historical rates for the selected route (baseline) | Not started |
| v1 | Historical METAR and live TAF, with operational explanations | Not started |
| v2 | Predictive model, adopted only if it beats the baseline | Not started |
| v3 | Compare options across airlines and departure time slots | Not started |

## Phase 0: setup and route selection

**Status:** Done

**Goal.** Have a working repository and enough knowledge of the data to choose
one route to start with.

**Done when:**

- [x] The repository, tooling and conventions are in place
  (`CLAUDE.md`, [decision 0001](decisions/0001-layered-architecture-app-display-only.md)).
- [x] US domestic routes have been profiled from BTS On-Time Performance data
  (`notebooks/01_bts_otp_route_profile.ipynb`).
- [x] One route has been selected, and the selection is recorded:
  SFO-LAX in both directions, with LGA-ORD as the candidate second route
  ([decision 0003](decisions/0003-route-selection.md)).

## v0: historical baseline

**Status:** Not started

**Goal.** An end-to-end tool for the selected route that uses only historical
rates. This is the baseline that later versions are compared against.

**Done when:**

- For the selected route, the user can input airline, date and time and get a
  risk level (green / amber / red) with an explanation.
- The result is based only on historical rates.
- The whole chain runs end to end: ingestion, transformation, prepared outputs
  and the app.

## v1: weather

**Status:** Not started

**Goal.** Add historical METAR and live TAF, and explain the risk level in
operational terms.

**Done when:**

- Historical METAR is part of the prepared data.
- Live TAF is used when the tool is queried.
- The explanation of the risk level is operational.

## v2: predictive model

**Status:** Not started

**Goal.** A predictive model, adopted only if it beats the baseline on a
held-out period, with calibration measured.

**Done when:**

- A model has been trained and compared with the v0 baseline on a held-out
  period.
- Its calibration has been measured.
- The model is adopted only if it beats the baseline; the outcome is recorded
  either way.

## v3: comparing options

**Status:** Not started

**Goal.** Compare options across airlines and departure time slots.

**Done when:**

- For a route and date, the tool shows the risk level for alternative airlines
  and departure time slots side by side.
