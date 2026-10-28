# TERRA-DATA-001B — FSMI live-application recovery audit (28 Oct 2026)

## Scope and method
Read-only examination of connected Base44 app "SustainAfrica Mining Restoration Intelligence Platform" (`6a5be6f55fca166df3f5f96b`), published staging pages and source files. **No new acquisition, geospatial recomputation or model run.** This is an audit of existing scientific artifacts, not a claim that they are all field-validated or publicly redistributable.

## Why 35 is not the national MAUS answer
- Desktop historical legacy **v1** file `maus_v2_overlap_by_license.csv`: 572 rows, 35 marked `has_maus=Yes`, 537 `No`, 567 distinct `guidLicense`. Its SHA is `ed6ac8947539afb4fbf146494f449a3beac03fc682b81d7c8874dee7599dd73b`. **35 relates only to this particular 572-row local v1 workflow**.
- In Base44 national CPDM history the `MiningPermit` read-model snapshot reports 22,430 shapes, 22,427 scored, **1,012 observed-footprint reference rows**. `public/fmri/guinea-observed-footprint-screening.json` has `record_count=1012` and deliberately `geometry_in_payload=false`.
- `PermitFootprintRelation` records exist in the connected Base44 entity. Their short footprint keys can be reconciled with `MiningFootprint` historical snapshot-prefixed keys under the canonical FSDC procedure. One record was sampled without data changes. **No current national geometric overlay was rerun or individually verified.** The relationship between 35 and 1,012 must not be inferred by directly dividing the counts; they refer to distinct populations, snapshots and producer pipelines.
- `guinea-cheng-evidence-chain.json` has 1,078 screened historical shapes, 71 party-context shape links, and `verified_cheng_to_permit_count=0`; this is a documented **unverified** link status, not evidence that there are no coincident mining footprints.

## Existing FSMI calculation/data outputs found

| Scientific rail | Materialized artifact in Base44 | Recorded content / status |
| --- | --- | --- |
| FSMI-RESTORATION-096 / FSMI-SCIENCE-101 | `public/data/fsmi/maus_evidence_640_v101.csv`; `src/lib/fsmiEnvironmentalEvidenceIntake.js` | **128 MAUS fids × 5 zones = 640** records; Hansen v1.13 status: **312 FULL**, **254 NEAR_FULL**, **74 REVIEW**; the source/parser enforces these counts. Exactly 1,280 zone×threshold indicators reported by the UI. Incomplete coverage requires cautious treatment; the observed MAUS source is not attributed to a specific company. |
| Cheng historic land-use | `public/fmri/guinea-cheng-landuse-index.json` and `public/fmri/guinea-territorial-cheng-proximity.json` | **707** historical class observations and **199** source sites. Classes recorded 2017–2022. `area_estimate_authorized=false` and `company_attribution_verified=false`. Ten regional screening centers are approximate cadastral bounding-box centers, not approved mine locations. |
| Historical source geometry triage | `public/fmri/guinea-overlap-review.json` | Recorded `source_archive_spatial_qa_overlap_pairs=977`. **This is polygon/source geometry QA, not 977 cadastral permit intersections.** |
| Atmosphere FSMI-091D | `public/fmri/guinea-cams-air-quality-september-2026.json`, `scripts/acquire-fsmi-cams-air-quality.py`, `src/lib/fsmiCamsDustEvidence.js` | **10** acquired CAMS regional context records via Open-Meteo Air Quality API, 30 days × 720 hourly samples per record, SHA-256 response fingerprints. Modeled PM2.5/PM10/dust/AOD; **no station measurements, no mine attribution, no approved site AOIs**. This source already exists: do not represent a repeat acquisition as first-time novelty. |
| Meteorology | `public/data/fsmi/guinea_34_nasa_power_2001_2025_v01.json` | Existing historical NASA POWER/MERRA-2 point-derived context for **34 approximate prefectural reference points** over 2001–2025; not prefectural averages. A new NASA API call must only be for a demonstrably new question, geography, variable or temporal interval. |
| Enterprise results | `src/hooks/useFSMICompanyAnalytics.js`, `public/fmri/guinea-company-party-context.json`, `public/fmri/guinea-cadastre-candidates.json`, `public/fmri/guinea-observed-footprint-screening.json` | **714 company index rows** in FSMI; regression script `scripts/verify-fsmi-real-screening.mjs` targets **35 source-candidate company dossiers**; these 35 are NOT the 35 `has_maus=Yes` historical v1 rows unless an independently documented bridge proves equality. |
| Source inventory | `config/fsdc/fsmi_scientific_inventory_v0.1.json`, `docs/fsdc/manifests/FSMI-FSDC-SCI-002_v0.2.json` | Existing manifests list scientific source paths, owners, QA and integration restrictions. Read them before adding new connectors. |

## Historic status cautions
- Base44 source file and screenshot display is **not** a guarantee of scientific field validation, legal title status, causality, external API current availability or redistribution rights.
- The FSMI company dashboard mixes documentary candidate matches, regional model estimates and observed raster processing; trust gates must remain distinct.
- Different datasets and counts must keep their universe and computation methods: **35 / 572 local historical MAUS v1**, **1,012 / 22,430 CPDM historic footprint references**, **128 MAUS Guinea source footprints**, **707 Cheng observations / 199 source sites**, **640 Hansen zone rows**, **714 company index entries**. None are interchangeable denominators.

## Revised build decision
**Pause new acquisition / duplicate calculations until existing FSMI data and methods are catalogued and provisioned read-only to TerraCouncil.** Reuse current CAMS and NASA POWER records first. For a genuinely new API acquisition during the hackathon, choose only a source/variable/geography/period that fills a verified gap and record the actual request date, SHA-256, QA and Council use. Do not publish private raw FAITH sources or proprietary code into the hackathon repo.

Next read-only inventory targets: Hansen CSV header/row sample/QA tests, Cheng class-year source, all CAMS provenance, and environmental outputs across FSMI Climate/ESG/Restoration. This audit does **not** declare new test executions or data promotion.
