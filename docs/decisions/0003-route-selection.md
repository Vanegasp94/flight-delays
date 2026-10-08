# 0003. Route selection: SFO-LAX first, LGA-ORD as candidate second route

- **Status:** Accepted
- **Date:** 2026-10-08

## Context

v0 is an end-to-end tool for one selected route (see
[0002](0002-tool-first-delivery-with-historical-baseline.md)), so a route has to
be chosen before v0 starts.

### Route profiling results

Source for every number in this section:
[`notebooks/01_bts_otp_route_profile.ipynb`](../../notebooks/01_bts_otp_route_profile.ipynb),
section 4 (tables 4a, 4b and 4c). The data is BTS Marketing Carrier On-Time
Performance, flights from 2023-01-01 to 2026-07-31 (1,308 days). Each direction
of an airport pair is profiled separately, and all four directions below
operated on every day of the period.

Volume and carriers:

| Direction | Rank | Flights | Flights per day | Marketing carriers | Operating carriers |
|---|---|---|---|---|---|
| LAX→SFO | 1 | 42,204 | 32.27 | 7 (AA AS B6 DL F9 UA WN) | 9 (AA AS B6 DL F9 OO QX UA WN) |
| SFO→LAX | 2 | 42,141 | 32.22 | 7 (AA AS B6 DL F9 UA WN) | 10 (AA AS B6 DL F9 MQ OO QX UA WN) |
| LGA→ORD | 5 | 39,202 | 29.97 | 4 (AA DL NK UA) | 7 (9E AA DL NK OO UA YX) |
| ORD→LGA | 6 | 39,200 | 29.97 | 4 (AA DL NK UA) | 7 (9E AA DL NK OO UA YX) |

Delay, cancellation and diversion rates. The delay percentages are of flights
where the BTS flag is reported (cancelled flights have no departure or arrival
flag; diverted flights have no arrival flag). Cancelled, diverted and null tail
number are shares of all rows of the direction.

| Direction | Departure delayed 15+ min | Arrival delayed 15+ min | Cancelled | Diverted | Null `Tail_Number` |
|---|---|---|---|---|---|
| LAX→SFO | 24.33% | 30.11% | 0.81% | 0.18% | 0.261% |
| SFO→LAX | 23.42% | 22.87% | 0.90% | 0.04% | 0.273% |
| LGA→ORD | 20.68% | 24.35% | 3.30% | 0.27% | 1.092% |
| ORD→LGA | 24.41% | 26.30% | 3.16% | 0.53% | 0.997% |

Delay minutes by cause, as minutes and as a share of the five causes' total:

| Direction | Carrier | Weather | NAS | Security | Late aircraft | Total |
|---|---|---|---|---|---|---|
| LAX→SFO | 167,310 (22.7%) | 10,959 (1.5%) | 336,288 (45.7%) | 483 (0.1%) | 220,786 (30.0%) | 735,826 |
| SFO→LAX | 155,795 (26.1%) | 8,115 (1.4%) | 92,990 (15.6%) | 388 (0.1%) | 338,527 (56.8%) | 595,815 |
| LGA→ORD | 199,218 (24.5%) | 46,222 (5.7%) | 238,821 (29.4%) | 493 (0.1%) | 328,661 (40.4%) | 813,415 |
| ORD→LGA | 208,328 (26.0%) | 34,783 (4.3%) | 255,676 (31.9%) | 578 (0.1%) | 303,249 (37.8%) | 802,614 |

### What the cause categories mean (BTS definitions)

The cause columns have to be read with the official definitions, quoted here.

**Source A:** BTS, "Understanding the Reporting of Causes of Flight Delays and
Cancellations", dated Monday, April 15, 2024,
<https://www.bts.gov/topics/airlines-and-airports/understanding-reporting-causes-flight-delays-and-cancellations>
(page text read on 2026-10-08).

**Source B:** BTS TranStats, "Airline On-Time Statistics and Delay Causes",
<https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp> (page text read on
2026-10-08).

The five categories, from Source A:

> **Air Carrier:** The cause of the cancellation or delay was due to
> circumstances within the airline's control (e.g. maintenance or crew problems,
> aircraft cleaning, baggage loading, fueling, etc.).
>
> **Extreme Weather:** Significant meteorological conditions (actual or
> forecasted) that, in the judgment of the carrier, delays or prevents the
> operation of a flight such as tornado, blizzard or hurricane.
>
> **National Aviation System (NAS):** Delays and cancellations attributable to
> the national aviation system that refer to a broad set of conditions, such as
> non-extreme weather conditions, airport operations, heavy traffic volume, and
> air traffic control.
>
> **Late-arriving aircraft:** A previous flight with same aircraft arrived late,
> causing the present flight to depart late.
>
> **Security:** Delays or cancellations caused by evacuation of a terminal or
> concourse, re-boarding of aircraft because of security breach, inoperative
> screening equipment and/or long lines in excess of 29 minutes at screening
> areas.

Weather recorded under Weather versus under NAS, from Source A:

> That category consists of extreme weather that prevents flying. There is
> another category of weather within the NAS category. This type of weather
> slows the operations of the system but does not prevent flying. Delays or
> cancellations coded "NAS" are the type of weather delays that could be reduced
> with corrective action by the airports or the Federal Aviation Administration.
> During 2020, 45.8% of NAS delays were due to weather. NAS delays were 33.4% of
> total delays in 2020.

Weather inside the late-aircraft category, from Source A:

> A true picture of total weather-related delays requires several steps. First,
> the extreme weather delays must be combined with the NAS weather category.
> Second, a calculation must be made to determine the weather-related delays
> included in the "late-arriving aircraft" category. Airlines do not report the
> causes of the late-arriving aircraft but an allocation can be made using the
> proportion of weather related-delays and total flights in the other
> categories.

The 15-minute threshold, from Source B:

> A flight is considered delayed when it arrived 15 or more minutes than the
> schedule (see definitions in Frequently Asked Questions). Delayed minutes are
> calculated for delayed flights only. When multiple causes are assigned to one
> delayed flight, each cause is prorated based on delayed minutes it is
> responsible for.

In the loaded data, the five cause columns are filled on no row whose arrival
flag `ArrDel15` is not 1, and 4 rows with `ArrDel15` = 1 have no cause minutes
(notebook section 3, checks `cause_minutes_without_arr_del15` and
`arr_delayed_15_without_cause_minutes`).

**Not verified:**

- The "Frequently Asked Questions" / "Delay Cause Definition" page that Source B
  links to was not opened.
- The TranStats field descriptions for the columns `CarrierDelay`,
  `WeatherDelay`, `NASDelay`, `SecurityDelay`, `LateAircraftDelay` and
  `ArrDel15` were not opened, so the link between the 15-minute threshold and
  these specific columns rests on Source B's general statement and on the data
  check above.
- The underlying rule (Source A cites Rule OST 2000-8164 on Regulations.gov) was
  not opened.
- The 2020 percentages in the quote are BTS's national figures; they were not
  recomputed and say nothing about the two routes here.

## Decision

- **SFO-LAX in both directions is the first route.** v0 is built for it.
- **LGA-ORD is the candidate second route**, to test whether the approach
  generalises.

SFO-LAX was chosen for three reasons. First, volume: about 32 flights per day in
each direction over the whole period, enough to build stable historical rates by
airline and time slot. Second, comparability: 7 marketing carriers, which makes
the airline comparison in v3 meaningful. Third, a measurable question for v1:
the share of delay minutes coded as NAS is 45.7% for LAX to SFO against 15.6%
for SFO to LAX. Given that BTS includes non-extreme weather within NAS, this
difference can be tested against METAR data in v1. No explanation for the
difference is assumed here.

## Alternatives considered

The other pairs in the top 30 by flight volume. The top 30 directions are 15
airport pairs in both directions; the 13 not chosen are below, with values given
as first direction / reverse direction. Source: the same notebook, tables 4a
and 4b.

| Pair (first direction) | Flights per day | Marketing carriers | Arrival delayed 15+ min | Cancelled |
|---|---|---|---|---|
| OGG→HNL | 31.11 / 31.10 | 3 / 3 | 15.55% / 13.76% | 1.20% / 1.03% |
| JFK→LAX | 27.59 / 27.59 | 4 / 4 | 20.63% / 20.27% | 1.11% / 1.19% |
| LAX→LAS | 27.30 / 27.27 | 8 / 8 | 24.35% / 23.73% | 0.94% / 0.90% |
| BOS→DCA | 25.94 / 25.94 | 3 / 3 | 21.68% / 23.00% | 2.64% / 2.73% |
| PHX→DEN | 25.54 / 25.47 | 4 / 4 | 21.41% / 24.66% | 1.01% / 1.00% |
| MCO→ATL | 23.79 / 23.78 | 4 / 4 | 25.94% / 28.78% | 1.20% / 1.22% |
| LIH→HNL | 22.80 / 22.80 | 3 / 3 | 15.75% / 14.52% | 1.30% / 1.17% |
| DEN→LAS | 22.19 / 22.18 | 4 / 4 | 26.70% / 24.59% | 1.10% / 1.29% |
| ATL→LGA | 21.78 / 21.78 | 6 / 6 | 23.44% / 21.41% | 2.38% / 2.46% |
| DEN→SLC | 21.52 / 21.50 | 4 / 4 | 23.50% / 23.02% | 0.72% / 0.80% |
| KOA→HNL | 21.40 / 21.40 | 3 / 3 | 14.65% / 13.71% | 1.10% / 0.97% |
| LGA→BOS | 20.93 / 20.93 | 3 / 4 | 20.75% / 18.94% | 3.60% / 3.89% |
| DEN→LAX | 20.85 / 20.80 | 6 / 6 | 21.88% / 17.67% | 0.81% / 0.84% |

Pairs outside the top 30 were not profiled.

## Consequences

- v0 covers SFO→LAX and LAX→SFO only.
- LGA-ORD is a candidate, not a commitment: it is used later to test whether
  the approach generalises.
- Weather data for v1 is needed first for SFO and LAX, and for LGA and ORD if
  the second route is taken up.
- By the BTS definitions above, the `WeatherDelay` minutes cover only extreme
  weather. Non-extreme weather is recorded under NAS, and weather that delayed
  an earlier flight of the same aircraft is recorded under late-arriving
  aircraft. The weather column therefore cannot be read as all weather-related
  delay.
- The cause columns hold minutes only for flights that arrived 15 or more
  minutes late, so they say nothing about shorter delays, cancellations or
  diversions.
