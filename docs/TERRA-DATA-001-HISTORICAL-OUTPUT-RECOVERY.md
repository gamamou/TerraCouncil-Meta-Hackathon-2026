# TERRA-DATA-001 — FAITH historical output recovery register (28 Oct 2026)

Purpose: **locate and reuse previous FAITH scientific outputs, not recompute them**. This ledger is a documented hackathon recovery effort, not proof that the original computations occurred during the hackathon. Source rights and governance restrictions remain in force.

## Retrieval findings — already located with exact links

| ID | What exists | Accessible artifact | Status / guard |
|---|---|---|---|
| FAITH-MAUS-SRC | Original `global_mining_polygons_v2.gpkg` present on participant Windows Desktop `Guinea_Mining_Restoration_Workflow/00_raw/maus_mining_footprint/`. Participant reports SHA256 exactly `6936e2743a21ba952b4de3e4b6f77099a0aa4479f7e2639d9d1b0787876a3ea1`; SQLite integrity OK; `mining_polygons` 44,929 features, Guinea ISO GIN 128, declared 231.34315495659 km2. | FAITH source contract https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/data-sources/maus-global-mining-polygons-v2.md | **LOCAL_SOURCE_FOUND_AND_HASH_MATCHED**. Reference polygon != active mine. |
| FAITH-CADASTRE-DESKTOP | Local `official_guinea_cadastre_all_layers_raw.geojson` and `official_guinea_cadastre_final_clean.geojson`, each 572 polygons; participant inspected fields, commodities, duplicate GUID counts (572 non-null, 567 unique). Geographic region metadata blank. These 572 are **not** the 22,430 canonical historical CPDM shapes. | `Guinea_Mining_Restoration_Workflow/00_raw/cadastre/` and `02_processed/cadastre/` | **LOCAL_SOURCE_FOUND_STRUCTURAL_AUDIT**; file license/provenance, true GeoJSON bounds and exact relation to historical snapshot not yet verified. |
| FAITH-CPDM-NATIONAL | Historical CPDM snapshot `20260716_232803_UTC`: 22,430 shapes, 22,427 scored; 1,012 `has_observed_footprint` rows; source 1,010 unique shape UID projected in FSMI. | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min080/minerestore-v2-reproduction-baseline-v0.1.md | **HISTORICAL_OUTPUT_DOCUMENTED**; legacy footprint reference flags cannot be equated with 1,012 independent verified geometric joins. |
| FAITH-MIN006-IDENTITY | Exact national identity reconciliation recorded: 22,430 shapes, 22,428 mapped, 2 quarantined, 4,910 GUIDLICENSE / 17,520 CODETYPE, accepted two-run reconciliation digest `e092f8d931a70ee305aee923ff7d53a3ec6700ce05369c931c79d7944f2e0e2c`. | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min006_decision_map_product_attribute_read_model_v0.1.md | **HISTORICAL_IDENTITY_METHOD_AND_RESULTS_FOUND**. This reconciles canonical cadastral identities, NOT a verified MAUS polygon-to-permit overlay. |
| FAITH-MIN080-FIXTURE | **18-row historical MineRestore data CSV** with `shape_uid`, score, class, national rank, evidence weight, footprint flags and spectral counts. | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/data/mining/minerestore/min080_boundary_case_fixture.csv | **EXACT_SMALL_OUTPUT_FOUND** (do not inflate to 22,430 rows). |
| FAITH-MIN082-COMPARISON | **18-row read-only output CSV**: historical score-to-class and confidence-policy comparison; 18/18 matches of class and confidence policies. Numerical full-score/rank replay 0/18 because upstream producer artifacts inaccessible. | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/data/mining/minerestore/min082_boundary_output_comparison.csv | **EXACT_SMALL_OUTPUT_FOUND**; `HISTORICAL_NUMERICAL_REPRODUCTION_NOT_ESTABLISHED`. |
| FAITH-MIN081-METHOD | Seven read-only component replay functions and documented control weights/thresholds. | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min081/implementation-evidence-v0.1.md | **METHOD_FOUND**, no new execution. |
| FAITH-CHENG-MIN085 | Cheng et al. 2026 functional mining land use reference; seven-class mapping (open pit, waste dumping, disturbed land, water, facility, bare soil, vegetation). | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min085/functional-land-use-source-ontology-v0.1.md | **REFERENCE_AND_ONTOLOGY_FOUND**. Neither Guinea classification raster nor site-class area table independently located yet; source dataset commercial reuse rights unresolved. |
| FAITH-CHENG-MIN087 | Sentinel-2 indices / TanDEM-X DCM and Random Forest reproduction contract, not full executed classifier. | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min087/functional-land-use-feature-model-contract-v0.1.md | **METHOD_FOUND_EXECUTION_NOT_VERIFIED**. |
| FAITH-MAUS-DRIVE | Two concrete Google Drive training artifacts: `maus2019_train_maus-site-1000m-d198541b349d99cf_features.tif` (~10.5 MB), `maus2019_train_maus-site-1000m-d198541b349d99cf_mask.tif` (~4 kB). | https://drive.google.com/drive/folders/1rFz97JW9xo1dtCBk6NtgbNYKocQFKXne and https://drive.google.com/drive/folders/14ZFKUKXzw8KiuXst7tS5FSSwoLIbmxa7 | **DRIVE_FILES_EXIST_METADATA_ONLY**. These are training raster candidates, not Cheng classes or national overlay. |
| FAITH-MIN006-OSM | `guinea-260819.osm.pbf` snapshot: historical download SHA256 `caebba2ac3a86d7ea38c96e067c3a73a729c60b9059c1ace91696403441678fc`. | https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min-006-pilot-source-freeze-v0.1.md | **HISTORICAL_SOURCE_FINGERPRINT_FOUND**, binary not yet located. |
| FAITH-MIN006-HYDRO | `HydroRIVERS_v10_af_shp.zip`: historical SHA256 `1dd2da2c288f1a7f9e1bd38fcf3c945e9f88dce71264c7851c8edb1854faa2a3`. | Same MIN-006 source freeze above | **HISTORICAL_SOURCE_FINGERPRINT_FOUND**, binary not yet located. |
| FAITH-MIN006-GHSL | `GHS_POP_E2020_GLOBE_R2023A_4326_3ss_V1_0_R8_C18.zip`: SHA256 `1d2198e9f1a8c0b1c627ed2fdcd53f64d2a70b8a2495018bf7654d397c3ed786`. | Same MIN-006 source freeze above | **HISTORICAL_SOURCE_FINGERPRINT_FOUND**, binary not yet located. |
| TERRA-010HI-HJ | Private user Windows files `010HI_evidence.json`, `010HJ_spatial_qa.json` and `boke_screened_evidence.json` located under Documents. | User reported local scanner inventory `FAITH-DATA-001.json` | **LOCAL_SOURCE_FOUND**; original values, dates and status require existing importer QA, not fresh raster computations. |

## Historical outputs not yet located as files

From MIN-080 explicit blocker:
- `cadastre_shape_master.geojson` — original national geometry binary; historical SHA256 `3915e6491cddab094645d55d569be657d8622cdf7d99744750b1f353709491fd`.
- Notebook 03 full integrated MAUS–cadastre producer table.
- Notebook 04 `restoration_priority_score_v2.csv` and `restoration_priority_spectral_features_v2.csv`.
- Cheng actual Guinea class rasters/results if execution occurred; MIN-085/087 methods do not establish execution.
- FSMI local AERMOD real inputs/output files.
These are to **locate** before considering recalculation or public re-download.

## Next controlled recovery action

On the participant Windows PC, search **by exact expected basename**, not by generic broad filename terms, including preserved .ZIP members and local repo/FAITH directories. Produce only metadata: path, size and source SHA; no source extraction, no scientific recomputation, no installs and no API/model calls. Review any discovered results and only then decide safe/private handoff to the Council; no raw FAITH files pushed to public hackathon GitHub.

## Meta hackathon novelty and provenance

Pre-existing scientific output stays credited to FAITH with its historical date. Newly authored recovery software, exact-asset location, API acquisition, harmonization and evidence-based council integration are hackathon activities with separate execution timestamps. Never rewrite old status, Git history, or claim pre-existing calculations were created during the competition.
