# TERRA-DATA-GATEWAY-001 — FAITH-first scientific evidence pipeline

## Binding decision, 2026-10-28
For the Meta hackathon, **recover existing FAITH datasets and executed analyses first**. Only re-download missing inputs when legally available; then add open APIs; organize data processing by AOI, indicator and stakeholder rather than by arbitrary separate product scripts. Future FSDC AWS S3 Data Lake remains separate; no premature migration. Reuse canonical FAITH source records read-only, no public repo commits of commercial/private data.

## Phase sequence
1. **RECOVER_EXISTING**: Search already materialized FMI / FSMI / FEI / FAI outputs (MAUS/Cheng/CPDM, CHIRPS, WorldPop/WorldCover, OSM, AERMOD, DynamicWorld/Hansen/JRC TMF/WaPOR). Record exact paths, source hashes, execution logs and scientific status. Known CPDM historic snapshot: 22,430 shapes, 1,012 rows flagged observed footprint; FSMI projection 1,010 distinct shape_uid. Local MAUS source: 128 polygons but its initial load created 0 permit links. Do **not** treat the 1,012 as distinct validated geometric overlays. Cheng MIN-085/087 ontology and feature-engineering exist; **Guinea classified results not verified**.
2. **LOCATE_MISSING**: if derived result exists and raw data are lost, retain verifiable output with provenance; attempt official-source re-acquisition only if necessary and license permits. Do not recreate values from the result narrative.
3. **API_DISCOVERY**: NASA POWER, OpenAQ, WEkEO/CAMS, STAC Earth Search, OSM, WaPOR, CHIRPS. Discover metadata/coverage before bulk downloads. For air pollution, separate modeled CAMS/MERRA2, sensors OpenAQ, and AERMOD local simulations (not equivalent).
4. **RAW_DOWNLOAD**: small, bounded, explicitly authorized source requests, private Drive or local staging. Save original provider JSON and SHA256. Never upload keys or raw private files to public GitHub.
5. **QA_VALIDATION**: assess license, spatial bounds, coordinate reference, period, variable description, unit, resolution, missingness, coverage and analytical constraints.
6. **INDICATOR_HARMONIZATION**: one AOI-period-indicator record per source. No automatic promotion of unreviewed API payload.
7. **MULTISOURCE_RECONCILIATION**: compare equivalent metrics on identical AOI, dates, units and definitions. Document correlated sources (two Sentinel-derived outputs are not necessarily independent).
8. **QUESTION_EVIDENCE_SELECTION**: filter scientific records according to the question and stakeholders, preserve precise quotes and evidence IDs; abstain where source unavailable.
9. **AGENT_DEBATE**: role-driven Spark positions, Wonder critical response, revised synthesis, with explicit approved paid model calls and independent verification.
10. **AUDIT_AND_EXPORT**: scientific comparison between baseline and expanded evidence, no prewritten disagreements.

## Six interface work areas
- **Situation & AOI** — problem, polygons, period and scenario; no assumed buffer impact.
- **Sources FAITH** — existing dataset inventory, earlier analysis results, hash/path and recovery status.
- **Scientific Connectors** — available API providers, secret-safe readiness, last actual metadata fetch, quota/licensing notes.
- **Indicators & QA** — indicator × AOI × source × date matrix, spatial/temporal comparability and quarantine controls.
- **Stakeholder Council** — evidence common ground; stakeholder-specific questions, critical debate and runtime trace.
- **Deliverables** — decision matrix, dissenting perspectives, uncertainty, citations, saved oral/audio and PDF.

## Implemented first executable API adapters
`src/terra_data_gateway.py` offers:
- NASA POWER daily grid point: T2M, WS10M, RH2M, PRECTOTCORR.
- OpenAQ v3 station **discovery**, 25 km radius; real measurements require a later station/sensor connector; API key required.
- Earth Search STAC **collection catalogue**, not yet satellite item discovery or download.

The default is **dry run**; `--execute` performs one HTTP request with 30 second timeout and no retry, saves raw JSON + fingerprint to a new private file, and leaves scientific status `DOWNLOADED_UNVALIDATED`. The script is **not** called automatically from the debate UI, nor does it use Meta/ElevenLabs.

## Windows use from extracted latest ZIP
```powershell
$scanner = Get-ChildItem . -Recurse -File -Filter terra_data_gateway.py | Select-Object -First 1
if (-not $scanner) { throw "Missing TERRA-DATA-GATEWAY-001" }
$root = $scanner.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_terra_data_gateway_001.py" -v
python -X utf8 $scanner.FullName --list
python -X utf8 $scanner.FullName --provider nasa-power --latitude 10.75 --longitude -14.25
```
For a real, explicit scientific data acquisition request:
```powershell
$private = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
New-Item -ItemType Directory -Force -Path $private | Out-Null
$out = Join-Path $private ("NASA_POWER_RAW_" + (Get-Date -Format yyyyMMdd-HHmmss) + ".json")
python -X utf8 $scanner.FullName --provider nasa-power --latitude 10.75 --longitude -14.25 --start 20250101 --end 20250107 --execute --out $out
```
This fetches **one gridded point** near the center of the exploratory rectangular AOI, not AOI-averaged weather or proof of local conditions. Remote service availability is not guaranteed. For OpenAQ, set `$env:OPENAQ_API_KEY` privately before explicit `--execute`, and recognize that no stations may be found.

## Current acceptance and limitations
- **Completed**: canonical staging source/agent/indicator mapping, initial API request validation, controlled raw capture adapter and offline test suite committed.
- **Pending**: user-side Python tests, live API execution, complete dataset recovery, QA of prior FAITH assets, geospatial comparison, scientific promotion into Council, interface wiring and fresh Spark/Wonder debate.
- Do not conflate API availability with verified measurements. No results have been fabricated. Relevant old FAITH code is separate from hackathon-bounded new code.
