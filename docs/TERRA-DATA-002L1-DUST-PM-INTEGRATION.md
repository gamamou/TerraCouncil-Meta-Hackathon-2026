# TERRA-DATA-002L1 — Dust, PM10, PM2.5 and meteorological evidence in TerraCouncil

Source inspection: **2026-10-28**, connected FAITH/FSMI Base44, read-only. No new CAMS, weather, AERMOD or external API request. Existing 002K Edge preview/run science adapter now attaches three extra dust context items to `regional_context` when the question contains a recognized dust topic.

## Actually recovered existing source outputs

| Original data | Stored sample population | Source scientific boundary |
|---|---:|---|
| `public/fmri/guinea-cams-air-quality-september-2026.json` | 10 noncanonical cadastral box-center model points × 30 days / 720 hourly model samples per point, September 2026 | CAMS global model via Open-Meteo, ~45 km grid, no site air sensor, no mine-source attribution |
| `public/fmri/guinea-hourly-wind-september-2026.json` | 10 historic reference points × 720 hourly modeled wind/weather values | Regional modeled wind at 10m, not site dispersion-ready meteorology; no verified emission inventory or exposure |
| `public/fmri/fsmi095-official-aermod-benchmark.json` | 587 ranked and 6 highest-value numeric matches to US EPA AERMOD reference | US reference pollutant SO2, **not** a validated Guinea PM10/PM2.5 model or calibration |

**Illustrative source-record context, not measured mine impact:** a source point `[-14.181477, 10.905188]` lies within the exploratory bounding rectangle `[-14.5,10.5,-14.0,11.0]` but is only a simplified cadastral screening-center location. Its September 2026 CAMS modeled means of daily means were PM10 **9.25 µg/m³**, PM2.5 **5.20 µg/m³**, dust **6.12 µg/m³**. These figures cannot be labeled mine emissions, personal exposure, localized receptor concentration or legal compliance. This model point has approximate 45-km grid resolution.

## Changes in GitHub

- `data/faith_dust_atmospheric_context_002l1.json`: source-checked metadata + one illustrative model-point value with geospatial caveats; no company IDs or raw hourly timeseries.
- `src/faith_dust_context_002l1.py`: fail-closed source-status checks and a dust-topic contextual adapter, never creates new AOI `evidence` or changes missing dust measurement topics.
- `src/faith_environmental_context_002k.py`: after attaching MAUS/Hansen, Cheng, CPDM historical source context, now calls dust adapter. Because 002L previously updated both `/api/dynamic-preview` and `/api/dynamic-run` to use the 002K adapter, **both interactive paths receive the same dust-science context and updated consent-bound plan fingerprint**.
- `tests/test_faith_dust_context_002l1.py`: no local sensor claim, no promotion to AOI evidence, source benchmark SO2 distinction and plan hash integrity. Tests committed; Windows end-to-end execution pending.

## Required decision evidence for future on-site atmospheric risk

Collect/crosscheck site emission source inventory and PM10/PM2.5 baselines; surveyed site and community receptor coordinates; onsite or appropriate AERMET meteorology with calibration; valid AERMOD deposition/dispersion setup and uncertainty analysis; monitor-based QA; and legal and scientific review of any compliance decision. AERMOD's US SO2 smoke test is solely engineering readiness.

## Demonstration integration

Load the original private `boke_screened_evidence.json` or updated six-indicator private file into the **existing** local server. In Edge ask a question mentioning `poussière` and `Boké`, preview source IDs and verify three dust context source names. Local evidence may permit a contextual debate via some *other* screened AOI observation; it must still abstain from claiming measured mining dust for the pilot. The paid model and data-sharing consent remains separate and explicit.

There is no need to download another ZIP now. Consolidate the next Windows QA session with 002L and 002J later, as requested.
