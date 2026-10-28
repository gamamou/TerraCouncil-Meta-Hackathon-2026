# TERRA-DATA-002J — Spatial identity gate for existing MAUS/Hansen results

**28 October 2026.** This hackathon milestone adds one geospatial *identity and coverage check* using prior FAITH outputs. It does not re-estimate forest loss, Dynamic World, JRC, mining surface area or source attribution.

## Evidence actually inspected from connected FSMI

Read-only materialized source files in existing SustainAfrica FSMI Base44:

| Existing dataset | Verified stored population | Scientific limitations |
|---|---:|---|
| `public/data/fsmi/maus_evidence_640_v101.csv` | 640 zone records, **128 MAUS source FIDs × 5 zones** | 312 FULL / 254 NEAR_FULL / 74 REVIEW Hansen QA rows; 239 populated 30% loss-rate fields and 178 populated 50% fields; 5 populated Dynamic World tree-share fields; no verified permit/company connection |
| `public/fmri/guinea-cheng-landuse-index.json` | 707 classification observations, 199 historical source sites | historical classifications, no authorized hectares or proven permit identity |
| `public/fmri/guinea-cheng-evidence-chain.json` | 1078 CPDM screened shapes, 71 party-linked shapes | `verified_cheng_to_permit_count=0`; no credible Cheng↔permit legal attribution |
| `public/fmri/guinea-observed-footprint-screening.json` | 1012 historical reference records | geometry absent; **not** 1012 verified MAUS intersections |
| `public/fmri/guinea-territorial-cheng-proximity.json` | 10 approximate screening points, distances 1/5/10/20 km | bbox screening centers, not mine locations; model says company/site attribution unverified |

The MAUS global source originally recovered on the user's Windows device has 44,929 polygons, 128 in Guinea, WGS84/EPSG:4326 and SHA256:
`6936e2743a21ba952b4de3e4b6f77099a0aa4479f7e2639d9d1b0787876a3ea1`.

**Do not confuse** the 128 national MAUS source FIDs, the older 572-row permit overlap universe (35 historical Yes), and the 1012 CPDM source-reference records. They describe different populations.

## New code

- `src/faith_maus_hansen_spatial_crosswalk_002j.py` reads the **original local global MAUS GeoPackage** read-only through SQLite, decodes its GPKG WKB shapes and uses local Shapely to check exact intersection of each of the **128 original source polygons** with the existing TerraCouncil exploratory rectangle `[-14.5,10.5,-14.0,11.0]`.
- It first requires the 640-row Hansen table to include exactly five zones for every source FID; refuses invented/modified causal, permit or company statuses; optionally pins the original GeoPackage SHA256.
- It reports matching FIDs and source checksums, but **never** claims whole-MAUS Hansen-zone statistics are clipped to the AOI, never estimates source-wide totals from the subset and never automatically generates Council evidence records.
- `tests/test_faith_maus_hansen_spatial_crosswalk_002j.py` creates **synthetic** GeoPackage geometries for geometry-engine regression, including two synthetic intersections, strict hash and attribution guard. Those numbers are solely test fixtures and never appear as real Guinea results.

## What is not yet completed

The user's authentic GeoPackage has **not yet been executed** against the authentic FSMI 640-row CSV in the user's Windows runtime. Thus the number of MAUS footprints intersecting the exploratory rectangle is **not yet known**. Retrieval and licensing of the raw FSMI Hansen CSV into the user's private input folder also remain separate. The source may be read through the connected FSMI developer app, but source availability does not imply permission to publish or forward raw payloads.

After the original geospatial match is locally confirmed, decide how to admit a narrowly scoped factual overlap finding with documented review and rights, while leaving source metrics that belong to a larger MAUS polygon in a distinct context lane.

## No need to run now

The user prefers consolidated milestones and one final Windows QA session near the next demo, rather than repeated ZIP tests. Continue wiring scientific attribution and source rights before the next manual run.

When testing later, locate the nested Python script and package test folder recursively in latest GitHub extraction; never run `unittest discover -s .` from ZIP extraction root.
