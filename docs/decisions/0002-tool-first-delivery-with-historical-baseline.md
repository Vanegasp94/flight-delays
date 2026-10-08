# 0002. Tool-first delivery, starting with a historical baseline

- **Status:** Accepted
- **Date:** 2026-10-08

## Context

The project's purpose is a tool: the user inputs route, airline, date and time
and gets a risk level (green / amber / red) with an explanation. The roadmap
ends with a predictive model and comparisons across airlines and departure time
slots, but the project needs to decide what to build first and how a later
version earns its place.

## Decision

Deliver a working end-to-end tool first, and improve it in versions:

- **v0** is an end-to-end tool for one selected route that uses only historical
  rates. It is the baseline.
- **v1** adds historical METAR and live TAF, with operational explanations of
  the risk level.
- **v2** adds a predictive model. It is adopted only if it beats the baseline
  on a held-out period, and its calibration is measured.
- **v3** compares options across airlines and departure time slots.

Later versions must beat the baseline to be adopted.

## Alternatives considered

- **Starting with the predictive model.** Not chosen: the first version uses
  only historical rates, and the model comes later.
- **Adopting a model without comparing it with a baseline.** Not chosen: a
  model is adopted only if it beats the baseline on a held-out period.

No other alternatives were recorded when this decision was made.

## Consequences

- A usable tool exists from v0, for one route, before any weather data or
  model is added.
- The baseline has to be kept and measurable, because v2 is judged against it.
- A held-out period has to be set aside for the v2 comparison, and calibration
  has to be measured.
- The predictive model may not be adopted: if it does not beat the baseline,
  the tool stays on the earlier approach.
- The first version covers a single route, so route selection (Phase 0) comes
  before v0.
