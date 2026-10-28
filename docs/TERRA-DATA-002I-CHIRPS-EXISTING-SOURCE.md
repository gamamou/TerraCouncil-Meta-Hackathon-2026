# TERRA-DATA-002I — CHIRPS first independent source admission guard

## Actual findings from source inspection, 28 October 2026

The TerraCouncil source importer `src/import_boke_010hi.py` already performs cross-source hash and QA checks on 010HI and 010HJ and emits WorldPop/ESA WorldCover results. Its `water_climate` branch presently verifies a `evidence_json_sha256` CHIRPS reference against the QA input-hash table, but does not extract a numerical AOI rainfall observation. A hash is NOT a precipitation measurement.

The connected FSMI Base44 application contains 12 monthly CHIRPS v3 Pentad 2025 readings and SPI metrics in `public/data/fsmi/fei_kankan_regional_reference_v01.json`; scope is explicitly `PREFECTURE_KANKAN_ONLY` and the record is `COMPUTED_UNREVIEWED_DEMO_ONLY`. It must **never be represented as Boké observation**, despite its reuse value elsewhere in FAITH.

## Code implemented and connected to the existing Council

- `src/faith_chirps_aoi_guard_002i.py`: always runs the original 010HI/J hash, AOI and source-status validator before reading the CHIRPS section. It emits a new record only when the actual original source supplies a numeric precipitation field, exact authorized *rectangular* AOI, date/period, HTTPS source and declared license. No external source requests or recomputation occur. Otherwise the output explicitly explains its abstention (hash-only, incomplete provenance, wrong AOI, bad data).
- `src/faith_multisource_case_002h.py` now calls the new guard and includes a CHIRPS record **conditionally**, without hardcoding a new scientific value. The independent dataset count remains 2 unless CHIRPS actually passes, in which case it is 3. Regional documentary sources and the outside-pilot NASA point remain separate.
- `tests/test_faith_chirps_aoi_guard_002i.py`: five mocked-fixture guard tests. `tests/test_faith_multisource_case_002h.py` adapted to preserve historical no-measurement behavior.

## Run once during next consolidated Windows verification

From the most recent extracted GitHub ZIP, in VS Code PowerShell:

```powershell
$guard=Get-ChildItem . -Recurse -File -Filter "faith_chirps_aoi_guard_002i.py" | Select-Object -First 1
if (-not $guard) { throw "Actualiser le depot GitHub avant le test" }
$root=$guard.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p "test_faith_chirps_aoi_guard_002i.py" -v
if ($LASTEXITCODE -ne 0) { throw "CHIRPS gate tests failed" }
python -X utf8 -m unittest discover -s "$root\tests" -p "test_faith_multisource_case_002h.py" -v
if ($LASTEXITCODE -ne 0) { throw "Council integration tests failed" }
$dir=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
$hi=Join-Path $dir "010HI_evidence.json"
$qa=Join-Path $dir "010HJ_spatial_qa.json"
if (-not ((Test-Path $hi) -and (Test-Path $qa))) { throw "Original source files missing" }
python -X utf8 $guard.FullName --hi $hi --qa $qa
```

If `REFERENCED_NOT_QUANTIFIED`, the next step is to inspect the original privately retained source result referenced by `water_climate.evidence_json_sha256`, not to infer or request rainfall. If `SCREENED_AOI_CHIRPS_MEASUREMENT`, 002H can admit the exploratory finding for the existing HACK-016 debate, subject to external permission review. User-side real-source execution of this milestone has **not** yet been observed.

**No automatic upgrade:** a successful structural gate is not an independent validation of CHIRPS science, licensing, border definitions, mining causality or field measurements.
