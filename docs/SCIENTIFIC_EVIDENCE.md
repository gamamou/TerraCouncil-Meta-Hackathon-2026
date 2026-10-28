# TerraCouncil — scientific evidence and multi-source data registry

## Rule of scientific admission
Existing FAITH calculations should be found and reused. If source lost, reacquire from the official archive where rights permit, and verify provenance. Newly acquired API responses are **raw inputs** until independent scientific QA accepts a specific indicator for the specific AOI.

## Available records and limitations
| Family | Lead source | Status on 2026-10-28 | User-facing scientific restriction |
| --- | --- | --- | --- |
| Mining geometry | MAUS v2 global GPKG / Guinea 128 references | Known source file on user desktop; not yet rehashed in this workstream | External footprint, not permit rights or current operation |
| Cadastre | Guinea official layers / CPDM snapshot | Desktop file candidates and historical 22,430/1,012 CPDM result reported | Historical flags != independently verified geometry joins |
| Mining functional | Cheng 2026 seven-class ontology and MIN-087 stack | FAITH code/method verified; actual Guinea class output not found | Never invent open pit/dump hectares; verify rights before external redistribution |
| Cover / people | WorldCover 2021, WorldPop 2026 and TerraCouncil 010HI | Historical screened metrics / source hashes available, re-verification pending | Not field validated, years do not align |
| Vegetation / water | Existing FAITH Hansen, JRC TMF, DynamicWorld, WaPOR Drive rasters | File presence confirmed; tile metadata unchecked | No causal attribution from mapped classes |
| Dust | FSMI AERMOD reference / CAMS / OpenAQ / MERRA-2 | Local output not found; external APIs planned | Separate measured PM, modeled regional PM, AOD and simulated local PM; do not claim a station |
| Climate | CHIRPS, ERA5 and NASA POWER | Some historical reference; new NASA point API adapter committed | Point meteorology != AOI-average; one CHIRPS day != flood trend |
| Community / infrastructure | OSM and WorldPop | Prior evidence and future Overpass/Geofabrik connector | Building != population count or exposure |
| Local content and economy | Company declarations and official reports | Gaps to identify | Missing economic figures may not be fabricated |

## Workbench and principal source references
- Recovery code `src/faith_asset_recovery_001.py`; its private output must stay outside public GitHub.
- Provider manifest `config/terra_data_gateway_001.json`.
- Raw API capture `src/terra_data_gateway.py`; executed calls must be separately authorized and do not automatically enter agent evidence.
- Existing FAITH source: https://github.com/SustainAfrica/faith-mining-data-core
- Scientific source contract Cheng: https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min085/functional-land-use-source-ontology-v0.1.md
- Explicitly separate **same variable different measurement approach** from **different variable** and **correlated data products**. None of these automatically establishes contradiction.
- Private Drive staging: https://drive.google.com/drive/folders/12IY3bsJlNH2wORjO1ppOzc44cKy21SlN

## AOI indicator QA contract
Each accepted observation must carry `aoi_id, geometry_hash, indicator_id, source_id, producer, source_version, observed_period, retrieved_at, method, unit, crs, source_resolution, missing_fraction, value, license, sha256, scientific_status, uncertainty, interpretation_limits`.
Derive indicators at the appropriate spatial aggregation. Do not sum non-additive gridded metrics or interpret a point as a national average. For multi-source comparison: require aligned AOI, year/season, unit and definition, and document source dependencies.

## Hackathon contribution
Acquiring **new public API data during the event** is part of the hackathon work, provided the actual retrieval timestamp, raw source fingerprint, processing and admission trace can be shown. The pre-existing FAITH science keeps its original provenance.
