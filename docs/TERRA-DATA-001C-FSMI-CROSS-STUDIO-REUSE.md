# TERRA-DATA-001C — FSMI cross-studio recovery and reuse (2026-10-28)

This is a **read-only audit of the pre-existing FAITH/FSMI scientific asset inventory**, performed during hackathon development for TerraCouncil. Source of truth: Base44 app `SustainAfrica Mining Restoration Intelligence Platform` `6a5be6f55fca166df3f5f96b`; inventory `config/fsdc/fsmi_scientific_inventory_v0.1.json` dated 2026-10-21. No live API call, model execution or scientific recalculation was performed in this audit.

## Already materialized data and computations

| Family | Existing FSMI artifact | Scientifically justified reuse |
| --- | --- | --- |
| Nationwide climate | `public/data/fsmi/guinea_34_nasa_power_2001_2025_v01.json` | Historical NASA POWER / MERRA-2 2001–2025 point-based climatology for 34 prefectural approximate centroids; **not area-mean or observed site** |
| FEI cross-product climate | `public/data/fsmi/fei_kankan_regional_reference_v01.json` | CHIRPS monthly rainfall and SPI3/SPI6; ERA5-Land and Sentinel-2 context; **Kankan only, computed-unreviewed** |
| Kankan forest and land cover | `public/data/fsmi/guinea_kankan_landscape_metrics_v01.json` | Hansen canopy/loss 2001–2025, JRC TMF degradation, Dynamic World cropland candidate; source definitions differ and must not be summed |
| MAUS/Hansen national restoration | `public/data/fsmi/maus_evidence_640_v101.csv`; `src/lib/fsmiEnvironmentalEvidenceIntake.js` | 128 MAUS fid × 5 zones = 640 rows; Hansen QA 312 FULL, 254 NEAR_FULL, 74 REVIEW; two canopy thresholds (30/50), 1,280 zone×threshold indicators. No verified enterprise attribution |
| Cheng historical land use | `public/fmri/guinea-cheng-landuse-index.json` | 707 historical class observations, 199 source-site IDs, no authorized area inference, no verified company or permit connection |
| Cheng territorial proximity | `public/fmri/guinea-territorial-cheng-proximity.json`, `public/fmri/guinea-cheng-evidence-chain.json` | 10 approximate cadastral bbox centers sampled; evidence chain has 1,078 screened shapes, 71 party-link shapes, **zero verified Cheng→permit links**; proximity is not geospatial identity |
| CAMS atmospheric models | `public/fmri/guinea-cams-air-quality-september-2026.json` | 10 regional model records; 30 days of 720 hourly values for PM2.5, PM10, dust, AOD per location, with response SHA-256. Not ground PM or mine-source dispersion |
| Wind and rainfall context | `public/fmri/guinea-hourly-wind-september-2026.json`, `public/fmri/guinea-wind-context-september-2026.json` | 10 regional modeled meteo contexts; no onsite anemometers, no AERMOD input validation |
| Communities and buildings | `public/fmri/guinea-worldpop-buildings-buffers.json` | 10 exploratory point/buffer records. WorldPop 2020 estimated population; OSM mapped buildings from 2024, completeness not assured; no affected population estimate |
| OSM spatial context | `public/fmri/guinea-ohsome-territorial-aggregates.json` | Historical OSM via ohsome, snapshot 2024-01-01, 10 locations. No company impact proof |
| EPA atmospheric engine benchmark | `public/fmri/fsmi095-official-aermod-benchmark.json`, `docs/fsmi/FSMI-095-EPA-OFFICIAL-RUNTIME-BENCHMARK.md` | AERMOD official v26135, historical US SO2 reference test; FSMI inventory records matching 587 of 587 ranked concentrations and 6 of 6 high reference values. **Not a Guinea PM10/PM2.5 mine model** |
| Legacy MAUS/cadastre v1 | User-local `maus_v2_overlap_by_license.csv` | 572 historic lines, 35 has_maus=Yes; this is only the legacy 572-row universe, not a national MAUS footprint-to-permit match count |
| CPDM national legacy reference | `public/fmri/guinea-observed-footprint-screening.json`; Base44 `PermitFootprintRelation` records | 1,012 reference footprint records in 22,430-form snapshot, not asserted 1,012 independent verified spatial intersections |

## QA and access caveats

The 2026-10-21 Base44 inventory records successful tests for national climate, public studio UI, official EPA benchmark, restoration handoff and dust readiness, but also **failures** in company scope (Node import attributes), shared scope (Node import attributes), navigation-count assertion, and a legacy climate JSX assertion. A build passed. These are **historical manifest statements**; they were not re-executed in this audit.

The manifest further records that some public `/data/fsmi/` URLs returned `HTTP 200 text/html` SPA fallback rather than JSON on 2026-10-21. **Source file present in app sandbox does not mean public API available.** The data access bridge for TerraCouncil should use controlled, explicit versioned ingestion and verify actual Content-Type/JSON, not fetch a page masquerading as data.

Current governance: source ownership remains with FMI/FSMI/FEI/FAI; commercial redistribution, site identity, pollutant causality and boundary validation are independent gates. Synthetic MineLand scenario data are **not scientific observations**.

## Development implication for hackathon

1. Finish a reference-only inventory and identify specific **Boké-relevant** source assets.
2. Build a read-only FAITH evidence import boundary; preserve raw hashes and provenance, never add raw private files to public GitHub.
3. Only after existing climate, dust, vegetation, mining and community assets are selected, call external APIs for genuinely missing variable, geography or period. Differentiate historic collection dates from new API retrieval dates.
4. Reuse existing audio and Spark/Wonder orchestration for the first truly evidence-driven multi-stakeholder debate, with no invented observations.

**No recomputation, data promotion, app modification or new API acquisition was executed in this milestone.**
