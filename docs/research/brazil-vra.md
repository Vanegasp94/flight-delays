# Flight-level on-time data in Latin America, and an evaluation of Brazil's ANAC VRA

Research carried out on 2 October 2026 in two rounds:

1. **Round 1** - data availability check for Brazil (ANAC), Colombia (Aerocivil),
   Chile (JAC) and Mexico (AFAC).
2. **Round 2** - five follow-up checks on Brazil's VRA dataset.

Nothing in the data was cleaned, dropped or adjusted. Scripts are in
[`research/brazil_vra/scripts/`](../../research/brazil_vra/scripts/); the script
or query behind each number is named next to it. No data files are stored in
this repository.

## Open questions

These come only from items explicitly marked as not verified below.

1. Which version of Creative Commons Attribution applies to the VRA dataset?
   The portal gives no version number.
2. What does ANAC's own VRA data dictionary say when read directly? The field
   descriptions, including "em horário de Brasília", were obtained through a
   fetch tool's reading of the metadata page, not the raw page.
3. Is the VRA archive complete for every month from 2000? Only January 2000 and
   June/July 2026 were opened in round 1; round 2 downloaded 103 months, none
   before July 2010.
4. Does the VRA JSON version match the CSV? It was not opened, apart from the
   first 900 bytes of the February and March 2020 files.
5. Do VRA times follow Brasília legal time at DST transitions other than 2018
   and 2019? Only those were tested.
6. Are the Chilean flight log's timestamps correct? The UTC cross-check assumes
   they are.
7. Were actual times in 2010-2015 copied from the schedule when no alteration
   was reported? This is a reading of the data, not a documented rule.
8. What do the `D` and `E` values of `Código Autorização (DI)` mean? No
   definition was found.
9. Does the SIROS Z-prefix rule cover "flights unique in UTC but duplicated on
   the Brasília date"? That wording was seen only in a search snippet.
10. What does the ANAC "portaria" of August 2026 on delay and cancellation cause
    codes contain? It was seen only in a search snippet and was not opened.
11. What are the coverage, limits and access conditions of REDEMET's METAR
    history? DECEA's hosts could not be reached.
12. Does Iowa State Mesonet actually hold data back to the archive start dates
    in its station metadata? Only SBGR from 2019 was downloaded.
13. Mexico: what is inside the AFAC punctuality files (airline and cause
    breakdown?), and do AFAC files newer than 2019 exist? No file could be
    opened and datos.gob.mx was not searched directly.
14. Colombia: what do the "Cumplimiento Aerocomercial" files and the "Licencia
    Abierta.pdf" contain? Neither was opened.
15. Chile: what do the quarterly punctuality PDFs and the two Power BI
    dashboards contain? Neither was opened. The update frequency of the flight
    log was relayed by a fetch tool, not read raw.

---

## Round 1 - Data availability

**Only Brazil publishes true flight-level on-time data (scheduled and actual
times per flight).** Chile has a flight-level movement log with tail number and
aircraft type but no scheduled times, and Colombia and Mexico are aggregated
only.

| Country | Flight-level, scheduled + actual | Tail number | Aircraft type | Delay / cancellation reason |
|---|---|---|---|---|
| Brazil (ANAC VRA) | Yes | No | No | Column exists, but 100% `N/A` in the July 2026 file |
| Chile (JAC) | Actual times only, one row per take-off/landing | Yes | Yes | No |
| Colombia (Aerocivil) | No, monthly aggregates | No | Type only, in an aggregate | No |
| Mexico (AFAC) | No, per-airport aggregates, stale | No | No | Not verified |

### Brazil: ANAC VRA

- **URL:** <https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Voo%20Regular%20Ativo%20%28VRA%29/>
- **Date range:** year folders run 2000 to 2026, and the latest populated month
  is July 2026 (August onward is empty). January 2000 and June/July 2026 were
  opened, not every month. *(Query: directory listings of the URL above.)*
- **Update frequency:** monthly, about four weeks after month end (the July file
  is stamped 28 Aug 2026). Older months get regenerated; the July 2023 file says
  "Atualizado em: 2026-09-28".
- **Format:** one CSV and one JSON per month. The CSV is semicolon-delimited,
  quoted, UTF-8 with BOM.
- **Columns (12):** `ICAO Empresa Aérea`, `Número Voo`,
  `Código Autorização (DI)`, `Código Tipo Linha`, `ICAO Aeródromo Origem`,
  `ICAO Aeródromo Destino`, `Partida Prevista`, `Partida Real`,
  `Chegada Prevista`, `Chegada Real`, `Situação Voo`, `Código Justificativa`.
- **Licence:** "Licença: Creative Commons Attribution", from
  <https://dados.gov.br/dados/conjuntos-dados/dadosabertos-areas-de-atuacao-voos-e-operacoes-aereas-voo-regular-ativo-vra>.
  No version number is given.
- **Reason codes over time (round 1 sample):** in a sample of the first ~10,000
  rows of each July file, codes are populated in 2010, 2015 and 2019 (e.g. `XN`,
  `AT`, `HD`) and all `N/A` in 2021, 2023, 2025 and 2026.
  *(Script: `justif_sample.py`. Superseded by round 2, check 3.)*

#### July 2026 file (`VRA_20267.csv`)

*(Scripts: `prof.py`, `prof2.py`.)*

**Row count:** 89,517 flights (86,793 `REALIZADO`, 2,724 `CANCELADO`).

**Null rate per column** (nulls are the literal string `null`; there are no
empty strings):

| Column | Null count | Rate |
|---|---|---|
| `Partida Prevista`, `Chegada Prevista` | 2,576 each | 2.88% |
| `Partida Real`, `Chegada Real` | 2,724 each | 3.04% |
| `Código Justificativa` | 89,517 (literal `N/A`) | 100% |
| The other seven columns | 0 | 0% |

The scheduled-time nulls are all flights flown without a schedule; the
actual-time nulls are exactly the cancelled flights.

**Values that look inconsistent:**

- **Extra first line:** line 1 is `Atualizado em: 2026-08-28`, ahead of the
  header row.
- **Mixed timestamp formats:** 6,834 rows have scheduled times like
  `2026-07-17 11:00:00.100000000`; the rest have no fractional part.
- **Duplicates:** 11 exact duplicate rows. Round 1 also reported "764 rows
  repeating the same airline, flight number, origin, destination and departure
  time". **That figure was wrong; see the correction in round 2, check 4.**
- **Origin equals destination:** 367 rows, almost all unscheduled; 20 of them
  have under 10 minutes between actual departure and arrival.
- **Flight numbers:** 2,529 have a `Z` prefix (e.g. `Z0506`).
- **Authorisation codes:** `Código Autorização (DI)` mixes digits with the
  letters `D` and `E`.
- **Impossible date:** one actual arrival is in 2027 (ARU Z0920, departs
  2026-07-15 10:05, arrives 2027-07-15 15:05).
- **Very early departures:** 5 flights left more than 60 minutes early,
  including TAP 0028 about 10 hours early and TAP 0110 about 20 hours early.
- **Very long delays:** one of about 27.5 hours (AEA 0084) and 12 of 12 to 24
  hours.
- **Month boundary:** 6 scheduled departures fall in August and 4 actual
  departures in June.
- **Schema drift:** the January 2000 file uses `dd/mm/yyyy HH:MM` and empty
  strings instead of `null`. *(Query: HTTP range request for the first 700
  bytes of `2000/01 - Janeiro/VRA_20001.csv`.)*

### Chile: JAC

- **Punctuality reports (aggregated):**
  <https://www.jac.gob.cl/estadisticas/informes-estadisticos-de-regularidad-y-puntualidad/>
  has quarterly PDFs per airport, and
  <https://www.jac.gob.cl/informes-calidad-de-servicio/> has quarterly PDFs
  through Q2 2026. No licence statement was found on jac.gob.cl.
- **Flight log (movement-level):** "Bitácora de Vuelos" at
  <https://datos.gob.cl/dataset/operaciones-aeronaves> is one row per take-off,
  landing or overflight, so a domestic flight appears twice.
- **Date range:** January 2000 to 31 Aug 2026, 11,117,690 rows.
- **Update frequency:** "Mensualmente, aproximadamente los días 10" (as relayed
  by the fetch tool from the JAC docs at
  <https://jac-mtt.github.io/jac-docs/docs/series/operaciones_aeroportuarias>,
  not read raw).
- **Format:** a single 138 MB Parquet file.
- **Columns (12):** `dt_operacion`, `aeropuerto_oaci`, `tipo_operacion`,
  `aeropuerto_dgac_orig_dest`, `aerolinea_dgac`, `numero_vuelo`,
  `actividad_cod`, `matricula`, `modelo_avion`, `modelo_avion_desc`,
  `es_internacional`, `pmd`.
- **Licence:** "Creative Commons CCZero", from the dataset page above.
  *(Query: `https://datos.gob.cl/api/3/action/package_show?id=operaciones-aeronaves`.)*
- **Limits:** no scheduled times and no cancellations, so on-time performance
  cannot be computed from it alone.

#### August 2026 slice

*(Script: `chile.py`.)*

**Row count:** 43,362 (20,131 departures, 20,130 arrivals, 3,101 overflights).

**Null rate per column:** `numero_vuelo` 11,736 (27.07%); every other column 0%.

**Values that look inconsistent:**

- **Time zone:** the docs describe `dt_operacion` as UTC, but the file types it
  as `America/Santiago`.
- **Same airport both ends:** 9,969 rows have the reporting airport equal to
  the origin/destination field.
- **Airline codes:** a mix of 2- and 3-character DGAC codes (e.g. `6I`, `18P`),
  not ICAO.
- **Registrations:** no hyphen, length 4 to 6 (e.g. `CCBER`).
- **Take-off weight:** 2 rows have `pmd` ≤ 0.
- **Timestamps:** minute resolution only.
- **Duplicates:** none.

### Colombia: Aerocivil

Aggregated only.

- **datos.gov.co:** the catalogue API returns three Aerocivil air-traffic
  datasets, all monthly counts. Searches for `cumplimiento itinerarios`,
  `puntualidad aerolineas`, `demoras vuelos` and `vuelos cancelados` returned
  zero results. *(Query:
  `https://api.us.socrata.com/api/catalog/v1?domains=www.datos.gov.co&q=<terms>`.)*
  - `jh8x-n6h6`, operations by airport, origin, destination, operator and
    flight type.
  - `gb6w-ynu4`, origin-destination traffic by airline.
  - `djjf-g4q4`, traffic by equipment type, which carries `Tipo de Equipo` and
    `Número de Vuelos`.
- **Itinerary compliance:** "Cumplimiento Aerocomercial" monthly XLSX and PPTX,
  2014 to July 2026, at
  <https://www.aerocivil.gov.co/centro_pensamiento/publicaciones/2962/>. The
  per-airline, per-month aggregation comes from the fetch tool's summary; the
  files were not opened.
- **Licence:** `jh8x-n6h6` metadata says "Creative Commons Attribution | Share
  Alike 4.0 International" (<https://www.datos.gov.co/api/views/jh8x-n6h6.json>).
  Aerocivil's open data page says data is available "de forma libre y gratuita,
  sin restricciones de uso"
  (<https://www.aerocivil.gov.co/publicaciones/3900/datos-abiertos/>).

### Mexico: AFAC

Aggregated only, and stale.

- **URL:** <https://www.gob.mx/afac/acciones-y-programas/demoras-indice-de-puntualidad>
- **Content:** XLSX files of delays and punctuality index, one per airport (61
  airports) plus all-airport yearly files, covering 2016 to Q2 2019. The page is
  dated 28 Aug 2020.
- **Licence:** none stated. The only notice is "La legalidad, veracidad y la
  calidad de la información es estricta responsabilidad de la dependencia".

### Round 1 - not verified directly

- **Brazil licence version and dictionary:** the CC Attribution version is
  unknown. ANAC's own metadata pages were CAPTCHA-blocked or rate-limited for
  raw access, so the field descriptions (including that times are Brasília
  time) come from the fetch tool's reading of the ANAC metadata page.
- **Brazil reason codes:** the cut-off between 2019 and 2021 is from samples,
  not full files, and the exact month was not pinned down. *(Round 2, check 3
  counted full files; see there.)*
- **Brazil JSON:** the JSON version was not opened.
- **Mexico file contents:** gob.mx served a bot challenge to direct download,
  so no AFAC file could be opened; everything about that page comes from the
  fetch tool's summary. The recollection that these files break delays out by
  airline and cause within each airport could not be confirmed.
- **Mexico newer data:** datos.gob.mx was not searched directly. Two web
  searches found no AFAC punctuality files newer than 2019, which does not
  prove none exist.
- **Colombia compliance files:** contents and the "Licencia Abierta.pdf" text
  were not opened.
- **Chile PDFs and dashboards:** the quarterly PDFs and the two Power BI
  dashboards linked from <https://www.jac.gob.cl/datos-y-estadisticas/> were not
  opened.

---

## Round 2 - Five checks on ANAC VRA

Headline results:

- **Time zone:** the four time columns are in Brasília legal time, including
  daylight saving before 2019.
- **Actual times before 2020:** largely not independent measurements.
- **Reason codes:** `Código Justificativa` is 100% `N/A` from April 2020 onward.
- **February and March 2020:** both files are corrupted.
- **Correction:** the "764 near-duplicates" reported in round 1 were mostly an
  artefact of the grouping key.

### 1. Time zone

**Conclusion: Brasília legal time (UTC−3; UTC−2 while DST was in force). High
confidence.**

Documentary evidence:

- **IAC 1504** (30 Apr 2000, read directly from the PDF at
  <https://pergamum.anac.gov.br/pergamum/vinculos/IAC1504.pdf>) defines
  departure and arrival as "(Hora Legal de Brasília – DF)".
- **ANAC's VRA metadata page**
  (<https://www.anac.gov.br/acesso-a-informacao/dados-abertos/areas-de-atuacao/voos-e-operacoes-aereas/voo-regular-ativo-vra/62-voo-regular-ativo-vra>)
  says "em horário de Brasília" for all four fields. This was obtained through
  the fetch tool's reading of the page, not the raw page.
- **SIROS manual** (<https://siros.anac.gov.br/SIROS/Conta/lib/manual.pdf>,
  p. 8-10, read directly): airlines file schedules in UTC ("Os horários devem
  ser informados em UTC"), so ANAC converts.

Empirical evidence, July 2026 file:

- **Congonhas curfew:** SBSP has zero actual departures between 23:00 and
  04:59, which rules out UTC. *(Script: `tz1.py`, part A.)*
- **Block-time symmetry:** scheduled block is 235 min SBGR→SBEG versus 230 min
  back, and 205 versus 200 for SBBR↔SBRB. Local times at each end would produce
  gaps of 2 and 4 hours. *(Script: `tz1.py`, part B.)*
- **Through flights:** for the same airline and flight number arriving then
  departing at SBRB (36 cases), SBPV (50) and SBCY (12), every gap is positive
  (22 to 130 min). SBEG has 1 negative in 195. *(Script: `through_flights.py`.)*
- **Cross-check against Chile's flight log:** for Brazil-Chile flights, VRA
  actual arrival minus the Chilean log's UTC landing time has a median of −172
  min; 1,098 of 1,110 matches round to −3 h. *(Script: `chx.py`.)*

Behaviour around DST (files for Feb 2018, Oct-Nov 2018, Feb 2019):

| Period | VRA minus UTC (median, arrivals into Chile) | Matches at that hour |
|---|---|---|
| 1-16 Feb 2018 (DST) | −113 min | 174 of 180 at −2 h |
| 19-28 Feb 2018 | −174 min | 104 of 105 at −3 h |
| 5-30 Nov 2018 (DST) | −114 min | 453 of 463 at −2 h |
| 1-15 Feb 2019 (DST) | −113 min | 343 of 348 at −2 h |
| 18-28 Feb 2019 | −172 min | 257 of 264 at −3 h |

*(Script: `chx.py`.)*

- **Flights spanning a transition** carry the clock jump: median actual block
  is +56 min versus the route median at DST start (4 Nov 2018, n=214) and −56
  min at DST end (17 Feb 2019, n=235). An ordinary Sunday control shows 0.
  *(Script: `dst.py`.)*
- **Skipped hour:** 00:00-00:59 on 4 Nov 2018 should not exist, yet it holds 21
  actual departures and 24 actual arrivals (37 and 55 a week later).
  *(Script: `dst.py`.)*
- **Repeated hour:** 23:00-23:59 on 16 Feb 2019 holds 95 actual departures
  versus 65 a week earlier, with nothing to tell the two passes apart.
  *(Script: `dst.py`.)*
- **TAM anomaly, 1-3 Nov 2018:** TAM's actual times are one hour late. All 14
  matched TAM arrivals sit at −2 h while other airlines are at −3 h, and TAM
  3944 (scheduled 16:55) shows actual 18:53, 17:51, 17:49 on 1-3 Nov, then
  16:55 on 5 Nov. TAM was at −3 h throughout October.
  *(Scripts: `dst_tam.py`; October figures from `dst.py`.)*

Not verified: only the 2018 and 2019 transitions were tested, and the
cross-check assumes the Chilean log's timestamps are correct.

### 2. Actual equals scheduled exactly (REALIZADO rows, July each year)

*(Scripts: `item2.py`, `item2b.py`.)*

Denominator is REALIZADO rows with both a scheduled and an actual time.
Comparison is at minute level; the `.100000000` suffix on some scheduled times
is ignored (on raw strings, 2026 departures are 6.0% and 2025 are 5.5%).

| Month | REALIZADO | With both dep times | Dep exact | Arr exact |
|---|---|---|---|---|
| 2010-07 | 87,722 | 81,817 | 72.6% | 72.0% |
| 2011-07 | 98,220 | 93,425 | 65.5% | 64.0% |
| 2012-07 | 102,566 | 97,425 | 66.5% | 66.0% |
| 2013-07 | 99,606 | 93,766 | 72.5% | 72.2% |
| 2014-08* | 96,104 | 91,340 | 78.0% | 77.6% |
| 2015-07 | 99,289 | 92,767 | 65.6% | 64.1% |
| 2016-07 | 85,881 | 25,566 | 4.7% | 0.8% |
| 2017-07 | 87,223 | 27,361 | 4.8% | 0.9% |
| 2018-07 | 88,422 | 88,419 | 29.5% | 26.6% |
| 2019-07 | 84,259 | 84,259 | 22.1% | 19.6% |
| 2020-07 | 18,409 | 18,156 | 6.5% | 2.6% |
| 2021-07 | 53,251 | 51,500 | 5.8% | 3.0% |
| 2022-07 | 76,368 | 74,205 | 6.7% | 3.3% |
| 2023-07 | 82,831 | 79,788 | 6.6% | 3.0% |
| 2024-07 | 84,599 | 82,157 | 6.3% | 2.9% |
| 2025-07 | 85,441 | 83,200 | 5.8% | 2.5% |
| 2026-07 | 86,793 | 84,217 | 6.4% | 2.7% |

\* The June and July 2014 folders are empty on the ANAC server, so August 2014
was used.

- **2010-2015:** almost all exact-equal rows have justification `N/A` (e.g.
  58,847 of the 2010 ones). A reading of this (not a documented rule) is that
  actual times were copied from the schedule when no alteration was reported.
- **2016-2017:** 53,406 and 50,729 REALIZADO rows have scheduled times but no
  actual times at all, again almost all `N/A`.
- **2020 onward:** rates are stable at about 6% for departures and 3% for
  arrivals.

### 3. First month with `Código Justificativa` 100% N/A

**April 2020.** Full files were counted for every month from January 2019 to
July 2026. *(Script: `item3.py`.)*

- **January 2020:** 22,034 of 92,390 rows carry a code (76.15% `N/A`).
- **February and March 2020:** codes are still present (30.9% and 29.6% of
  rows), but both files are corrupted *(script: `corrupt_2020.py`)*:
  - All four time columns and `Situação Voo` contain the string
    `Microsoft.SqlServer.Dts.Pipeline.BlobColumn` in every row.
  - Row counts are 323,676 and 258,092, but only 19,492 and 15,366 rows are
    distinct; identical rows repeat in multiples of four.
  - The JSON versions show the same placeholder (first 900 bytes checked).
- **April 2020 to July 2026:** all 76 months have zero non-`N/A` rows.

A web search snippet mentions an ANAC "portaria" of August 2026 standardising
delay and cancellation cause codes. It was not opened.

### 4. Z-prefix, origin = destination, near-duplicates (July 2026)

*(Scripts: `item4.py`, `neardup_764.py`.)*

Official definitions:

- **`Código Tipo Linha`** (IAC 1504, read directly): "I" (Internacional), "N"
  (Nacional), "R" (Regional), "E" (Especial), "L" (Rede Postal), "H"
  (Sub-Regional), "C" (Cargueiro Doméstico), "G" (Cargueiro Internacional).
- **`Código Autorização (DI)`** (IAC 1504):

  | Code | Meaning | Code | Meaning |
  |---|---|---|---|
  | 0 | Regular | 6 | Serviço |
  | 1 | Extra com HOTRAN | 7 | Fretamento |
  | 2 | Extra sem HOTRAN | 8 | Conexão internacional |
  | 3 | Retorno | 9 | Charter |
  | 4 | Inclusão de etapa | A | Instrução |
  | 5 | Cargueiro não-regular | B | Experiência |

  The `D` and `E` values in the 2026 data are not in that list; no definition
  was found.
- **Z prefix** (SIROS manual p. 9, read directly): "Aceita-se inclusão do
  prefixo Z para correção de duplicidade de voos no mesmo dia". A search
  snippet elaborates that this covers flights unique in UTC but duplicated on
  the Brasília date; that wording was not seen directly.

**Z-prefix rows: 2,529.**

- **Status:** 2,527 are REALIZADO and 2,333 have no scheduled times.
- **Flight type:** DI 1 (664), 6 (469), 2 (373), 4 (370), 3 (328), 0 (196),
  9 (55), D (43), 7 (31).
- **Line type:** N 1,392, G 671, I 311, C 155.
- **Airlines:** AZU 654, TAM 388, GLO 382, LTG 310, LAE 166, ACN 145, LCO 133.
- **Same-day counterpart:** only 752 share airline, number and date with a
  non-Z row, so in practice Z mostly marks unscheduled operations.

**Origin = destination: 367 rows.**

- All are Z-prefixed, REALIZADO and without scheduled times.
- **Flight type:** DI 3 "Retorno" (328), DI 6 "Serviço" (38), DI 4 (1).
- **Line type:** N 334, I 27, C 4, G 2.
- **Airlines:** AZU 180, TAM 108, ACN 48, GLO 22, LAN 5.
- **Duration:** median actual block is 25 min.

**Near-duplicates: correction to round 1.**

- **What went wrong:** the first-pass key used the scheduled departure, which
  is the literal `null` for unscheduled flights. 752 of the 764 were therefore
  unscheduled flights with the same number and route on different dates (310
  groups of 2 to 22 rows). *(Script: `neardup_764.py`.)*
- **What differs in those groups:** `Partida Real` and `Chegada Real` in all
  310, DI in 6, line type in 1. They are not duplicates.
- **Who they are:** LTG 273, AZU 104, LAE 102, LCO 96, ETH 59; line type G 493,
  I 255, N 219, C 95.
- **Real duplicates:** keying on actual departure when scheduled is null leaves
  12 pairs. Eleven are fully identical rows (UAE, QTR, ITY; international cargo
  and passenger). One is AZU 9506 SBGR-SBPS on 9 July, with one row CANCELADO
  (DI 2) and one REALIZADO (DI 9). *(Script: `item4.py`.)*

### 5. Historical METAR

**Iowa State Mesonet: free, no key, covers 2019 onward.**

- **URL:** <https://mesonet.agron.iastate.edu/request/download.phtml?network=BR__ASOS>
- **Query used:**
  `https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=SBGR&data=metar&year1=2019&month1=1&day1=1&year2=2026&month2=10&day2=2&tz=Etc/UTC&format=onlycomma&report_type=3&report_type=4`
- **Archive start per station metadata**
  (`https://mesonet.agron.iastate.edu/api/1/network/BR__ASOS.json`): SBGR 2001,
  SBSP 1931, SBRJ 1938, SBBR 1960, SBEG 1977, SBRB 1983. Only SBGR from 2019
  was actually downloaded.
- **SBGR, 1 Jan 2019 to 1 Oct 2026:** 72,231 reports, and 67,902 of 67,944
  hours have at least one (99.94%). *(Script: `metar_gaps.py`.)*
- **Gaps:** 42 missing hours in 13 gaps. The longest is 23 hours from
  2021-10-04 17:00 UTC; the rest are 3 hours or less. By year: 2019 5, 2020 5,
  2021 26, 2022 4, 2024 2. *(Script: `metar_gaps.py`.)*

**REDEMET: not verified.** DECEA's hosts refused or reset connections. From a
search snippet only: the endpoint is
`https://api-redemet.decea.mil.br/mensagens/metar/{localidades}` with
`data_ini`/`data_fim`, history from 1 Jan 2003, and an API key requiring
registration.

### Round 2 - not verified directly

Collected from the marks above:

- **ANAC metadata page:** "em horário de Brasília" was obtained through the
  fetch tool's reading of the page, not the raw page.
- **DST:** only the 2018 and 2019 transitions were tested, and the cross-check
  assumes the Chilean log's timestamps are correct.
- **2010-2015 exact matches:** that actual times were copied from the schedule
  is a reading of the data.
- **JSON versions of February/March 2020:** first 900 bytes checked only.
- **August 2026 "portaria":** seen in a web search snippet; not opened.
- **DI values `D` and `E`:** no definition found.
- **Z-prefix elaboration** ("unique in UTC but duplicated on the Brasília
  date"): search snippet only.
- **Mesonet archive start dates:** from station metadata; only SBGR from 2019
  was downloaded.
- **REDEMET:** not verified; search snippet only.

---

## Reproduction

### Setup

```bash
uv sync
```

Choose a data directory (default `data/research/brazil_vra`, git-ignored) and
download the sources (about 1.4 GB: 103 VRA months, the Chile flight log, the
SBGR METAR file):

```bash
uv run python research/brazil_vra/scripts/download.py
```

To use another location, set `BRAZIL_VRA_DATA_DIR` first. The numbers in this
document were computed on files downloaded on 2 October 2026. ANAC regenerates
past months and the Chile and Mesonet files grow, so a fresh download can give
different numbers.

### Run order and expected output

Each script prints to the terminal and writes nothing. Run with
`uv run python research/brazil_vra/scripts/<name>.py`.

| # | Script | Input | Key lines to expect |
|---|---|---|---|
| 1 | `prof.py` | VRA 2026-07 | `rows 89517 badlen 0`; `Partida Prevista ... literalNA=  2576 (2.88%)`; `Partida Real ... literalNA=  2724 (3.04%)`; `exact duplicate rows: 11  dup key(airline,flt,orig,dest,dep): 764`; `origin == destination 367`. Its `unparseable datetime 24268` and `CANCELADO with an actual time 2724` lines are artefacts of treating `null` as a value |
| 2 | `prof2.py` | VRA 2026-07 | 6,834 rows with shape `9999-99-99 99:99:99.999999999`; patterns `REALIZADO val val val val 84217`, `CANCELADO val null val null 2724`, `REALIZADO null val null val 2576`; `actual block < 10 min 20`; `dep delay 12-24h 12`; `departed > 60 min early 5`; `exact dup groups 11` |
| 3 | `chile.py` | Chile flight log | `total rows 11117690`; `PROFILE MONTH 2026-08 rows 43362`; `numero_vuelo null= 11736 (27.07%)`; `tipo_operacion {'D': 20131, 'A': 20130, 'W': 3101}`; `same airport as orig/dest 9969`; `exact dup rows 0` |
| 4 | `justif_sample.py` | 7 VRA months | 2010-07, 2015-07, 2019-07 show codes (`XN`, `HD`, `AT`, ...); 2021-07, 2023-07, 2025-07, 2026-06 show only `N/A` |
| 5 | `tz1.py` | VRA 2026-07 | SBSP departure histogram with zeros for hours 0-4 and 23; `SBGR->SBEG (250, 235.0, 233.0) | SBEG->SBGR (245, 230.0, 229.0)`; `SBBR->SBRB (74, 205.0, 203.0) | SBRB->SBBR (75, 200.0, 185.0)` (values print wrapped as `np.float64(...)`; the tuple is n, scheduled median, actual median) |
| 6 | `through_flights.py` | VRA 2026-07 | `SBEG n 195 negative 1`; `SBRB n 36 negative 0 min 22.0 ... max 130.0`; `SBPV n 50 negative 0`; `SBCY n 12 negative 0` |
| 7 | `chx.py` | VRA 2026-07, 2018-11, 2018-02, 2018-07, 2019-02; Chile log | `2026-07: arrivals into Chile ...: n=1110 median VRA-UTC = -172 min` with 1,098 at −3.0; the five DST-table rows above (−113/174 of 180, −174/104 of 105, −114/453 of 463, −113/343 of 348, −172/257 of 264) |
| 8 | `dst.py` | VRA 2018-10, 2018-11, 2019-02, 2018-02; Chile log | `2018-11-04 00:00-00:59 ... pr_t: 21 rows; same hour one week later: 37`; `cr_t: 24 rows; ... 55`; `2019-02-16 23:00-23:59 ... pr_t: 95 rows; same hour one week earlier: 65`; `DST start ... n=214; ... median 56 min`; `DST end 2019-02-17 ... n=235; ... median -56 min`; `control ... median 0 min`; October table `TAM 0 2 239 1` |
| 9 | `dst_tam.py` | VRA 2018-10, 2018-11; Chile log | `A Nov 1-3 2018 airline x offset`: `TAM 0 0 14` (all at −2); TAM 3944 rows `01/11/2018 16:55  01/11/2018 18:53`, `02/11 ... 17:51`, `03/11 ... 17:49`, `05/11 ... 16:55` |
| 10 | `item2.py` | July 2010-2026 (Aug 2014) | One line per year; the table in check 2, e.g. `2010-07 | 95817 | 87722 | 81817 | 72.6% | 72.6% | 81808 | 72.0%` and `2026-07 | 89517 | 86793 | 84217 | 6.4% | 6.0% | 84217 | 2.7%` |
| 11 | `item2b.py` | same | `2010-07 ... just among exact-equal rows: {'N/A': 58847, ...}`; `2016-07 patterns {'1010': 53406, ...}`; `2017-07 patterns {'1010': 50729, ...}` |
| 12 | `item3.py` | every month 2019-01 to 2026-07 | 91 lines; `2020-01 | 92390 | 22034 | 76.15%`; `2020-02 | 323676 | 99932 | 69.13%`; `2020-03 | 258092 | 76324 | 70.43%`; `2020-04 | 7617 | 0 | 100.00%` and `0 | 100.00%` on all 76 lines from 2020-04 on |
| 13 | `corrupt_2020.py` | VRA 2020-02, 2020-03 | `2020-02 rows 323676 | distinct full rows 19492 | ... rows where all five == BlobColumn placeholder: 323676`; `2020-03 rows 258092 | distinct full rows 15366 | ... 258092`; multiplicities starting `{4: ..., 8: ..., 12: ...}` |
| 14 | `item4.py` | VRA 2026-07 | `== Z-prefix rows: 2529`; `Z rows whose airline+number(without Z)+Brasília date also exists as a non-Z row: 752 of 2529`; `== origin==destination rows: 367`; `== near-duplicate rows (all members of groups): 24 groups: 12 extra rows: 12`; `difference patterns (groups): {'IDENTICAL': 11, 'di+pr+cr+sit': 1}` |
| 15 | `neardup_764.py` | VRA 2026-07 | `rows in groups 1086 groups 322 extra rows 764`; `of the extra rows, scheduled dep == null: 752`; `null-sched groups: rows 1062 groups 310`; `columns differing within groups (groups count): {'di': 6, 'tl': 1, 'pr': 310, 'cr': 310, 'sit': 0}` |
| 16 | `metar_gaps.py` | SBGR METAR | `reports 72231 first 2019-01-01 00:00:00 last 2026-10-01 23:00:00`; `hours in span 67944 hours with >=1 report 67902 missing hours 42 0.062%`; `gap count 13 longest: [(23, datetime.datetime(2021, 10, 4, 17, 0)), ...` |

### Queries without a script

These round-1 facts came from one-off requests rather than scripts:

| Fact | Request |
|---|---|
| VRA folder structure, latest month, empty June/July 2014 folders | Directory listings under the VRA URL |
| Colombia dataset list and columns | `https://api.us.socrata.com/api/catalog/v1?domains=www.datos.gov.co&q=aerocivil` |
| Colombia licence for `jh8x-n6h6` | `https://www.datos.gov.co/api/views/jh8x-n6h6.json` |
| Chile dataset metadata and licence | `https://datos.gob.cl/api/3/action/package_show?id=operaciones-aeronaves` |
| Mesonet station metadata | `https://mesonet.agron.iastate.edu/api/1/network/BR__ASOS.json` |
| VRA licence | Page text of the dados.gov.br dataset page, read in a browser |
| IAC 1504 and SIROS manual quotes | Text extracted from the two PDFs |
| JSON placeholder in Feb/Mar 2020 | HTTP range request for the first 900 bytes of `VRA_20202.json` and `VRA_20203.json` |

### Notes on the scripts

- `tz1.py`, `chx.py`, `dst.py`, `item2.py`, `item2b.py`, `item3.py`, `item4.py`,
  `prof.py`, `prof2.py` and `chile.py` are the files run in the session, with
  paths replaced by the configurable data directory and formatting applied.
- `through_flights.py`, `dst_tam.py`, `neardup_764.py`, `corrupt_2020.py`,
  `metar_gaps.py` and `justif_sample.py` were run as inline commands in the
  session and were written out as files afterwards. `justif_sample.py` reads
  the first 1,500,001 bytes of local files where the session used HTTP range
  requests for the same bytes.
- `chx.py`, `dst.py` and `dst_tam.py` rebuild the Brazil-Chile subset of the
  Chilean log in memory instead of reading the cached `chile_br.pkl` the
  session used.
