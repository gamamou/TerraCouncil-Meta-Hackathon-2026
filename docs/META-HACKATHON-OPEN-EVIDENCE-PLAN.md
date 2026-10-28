# META Hackathon 2026 — Open evidence demonstration / decision gate

## Architecture decision — 28 October 2026
**FAITH FSDC AWS S3 Data Lake is a separate post-hackathon architecture milestone.** The hackathon prioritizes a dynamic, evidence-grounded multi-agent Spark/Wonder Council using open science, a small Boké AOI, and a dedicated Google Drive working folder. Existing FAITH datasets must be reused where admissible; no new files are assumed scientifically validated by copying them.

Private Google Drive root (owner connected):
https://drive.google.com/drive/folders/12IY3bsJlNH2wORjO1ppOzc44cKy21SlN

Subfolders:
1. Sources publiques et références — https://drive.google.com/drive/folders/16gXZB0JJNOSjK7qEn9JAXhnSqL4XuHCx
2. Données Boké validées pour démo — https://drive.google.com/drive/folders/1Tcx6MAlX5CpPuKye2nFZgRGbbex3tXl8
3. QA, provenance et comparaisons — https://drive.google.com/drive/folders/1PORtSBdkpRu9YbxoddU-fLgd2jXxvb9-

## Confirmed file staging
Copies of two already existing FAITH Guinea rasters, **not freshly downloaded external data**, were placed in Sources publiques et références:
- `CANDIDATE_DynamicWorld_Guinea_2025_tile.tif`, 355,844 bytes, copied from FAITH_DynamicWorld_Guinea original.
- `CANDIDATE_JRC_TMF_Guinea_2025_tile.tif`, 2,318,046 bytes, copied from FAITH_JRC_TMF_Guinea original.

Both are UNCHECKED: must inspect true CRS, bounds, bands, nodata, pixel resolution, units, provenance, license and coverage intersection with the rectangular pilot AOI [-14.5,10.5,-14.0,11.0]. Do not move into folder (2) until validated. Google Drive file names are not sufficient evidence of contents or temporal period.

## Open-source priority
- Geofabrik Guinea OSM: https://download.geofabrik.de/africa/guinea.html, ODbL 1.0, attributing OSM contributors and complying with database terms.
- UCSB CHIRPS v3: https://www.chc.ucsb.edu/data/chirps3, 0.05 degree, monthly rainfall and 1981–present. Verify product preliminary/final, license and date.
- Existing FAITH DynamicWorld / Hansen / JRC TMF rasters and WaPOR: collect original tile metadata and derive **only** validated AOI metrics.
- Prefer small, reproducible AOI subsets over massive nationwide downloads.
- The older OSM/FAITH recovery workflow and S3 build are not prerequisites for a hackathon scientific debate.

## Measurable demonstration (do not add new superficial screens)
1. One new non-WorldPop/WorldCover **AOI-matched** science layer verified by CRS, date, license, SHA256, numerical interpretation and QA.
2. A before/after source diff for the exact same question with source IDs and validation limits.
3. A separately user-authorized new Spark/Wonder session with recorded disagreement, criticism and justified revision.
4. Compare actual propositions vs. baseline; if unchanged, state it.
5. A single source-grounded report containing the evidence matrix and genuine differences, not predetermined script or invented effects.

## Status
Open sources researched, private Drive folders created/read back, two old FAITH raster tiles copied/read back into staging and public GitHub registry written: data/meta_hackathon_open_evidence_registry.json.
**No new external science dataset has yet been downloaded and scientifically ingested for Boké. No new model debate executed, and no model output/cost has been incurred.**
