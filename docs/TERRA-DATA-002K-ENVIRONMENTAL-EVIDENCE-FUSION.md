# TERRA-DATA-002K — Environmental Evidence Fusion for Spark–Wonder

Date: 2026-10-28. Inputs were retrieved **read-only** from the existing connected SustainAfrica FSMI Base44 source. This milestone adds a new context pathway, **not newly calculated scientific indicators**.

## Implemented

- `data/faith_fsmI_environmental_snapshot_002k.json`: minimal curated, existing **national or noncanonical historical source metadata**, with real source paths, source numbers, scientific statuses, lack of spatial attribution and QA limitations. No raw confidential permit list, company identity payload or scientific source rights are silently copied to GitHub.
- `src/faith_environmental_context_002k.py`: validates exactly five source identities and their scoped statuses and counts. It converts the national scientific source metadata into the **already existing HACK-016 `regional_context` input lane**, not `evidence`. Topic filtering selects relevant sources for mining/land/climate/governance questions. Source hashes of the selected context are included in the exact plan fingerprint, preventing authorization reuse after context changes.
- `src/faith_multisource_case_002h.py`: now calls both the existing documentary context adapter and the environmental scientific context adapter after classifying authentic screened AOI WorldCover/WorldPop (plus conditional CHIRPS) evidence. Original evidence statuses and sources are never rewritten.
- `tests/test_faith_environmental_context_002k.py`: tests five candidate sources, zero falsely admitted AOI records, geographic exclusion, source-status immutability and zero verified Cheng-permit relationships.

## Specific original FAITH/FSMI facts preserved

- MAUS/Hansen: **128** Guinea mining source FIDs, **640** FID × five-zone records. Hansen QA 312 FULL / 254 NEAR_FULL / 74 REVIEW. Of 640 records, 239 populated threshold-30 forest loss-rate fields and 178 populated threshold-50 fields; **these are data-presence counts, not total quantified forest losses**. Five Dynamic World tree-share fields populated. MAUS↔permit/company and causal attribution unverified.
- Cheng historical classification index: **707** class observations from **199** source sites (2017–2022); source display geometry simplified; counts do not represent hectares or verified site-company relationships.
- Historical CPDM reference screening: **1012** source rows, no polygon geometry. Distinct from the 572-row legacy MAUS permit universe and from 128 MAUS footprints.
- Cheng–CPDM party context: **1078** screened shapes / **71** party-linked shapes, but **0 verified Cheng-to-permit polygon matches**.
- Historical Cheng proximity: **10** noncanonical cadastral screening centers, radii 1/5/10/20 km. These are not surveyed mine locations or exposure zones.

## Critical Council separation

`plan.evidence` contains only original screened AOI records with exact verified source findings, kept under HACK-016's existing structural gate. `plan.regional_context` may include the **five additional national scientific records**, as contextual claims **not attributable to the AOI**; additional documentary records remain separately labeled inside the same context lane. No context record can become an observation merely through fusion.

The existing `dynamic_runtime.py` tells Spark and Wonder that regional context cannot enter `observations` and requires fact IDs to be copied exactly for AOI observations. It may be used to propose additional tests and challenge over-generalization in *hypotheses/investigations*. Human scientific approval, source permissions and explicit paid API data-sharing consent remain required for a live run.

This is **not a claim of five extra independent Boké field observations**. The user-side QA has not yet been run. The geometry crosswalk in 002J needs a later actual source execution to determine which MAUS FIDs physically intersect the pilot rectangle; rates from entire MAUS source zones cannot be interpreted as clipped values.

## One consolidated test at next planned Windows demo

In an updated extracted repository root:

```powershell
$ErrorActionPreference = "Stop"
$module = Get-ChildItem . -Recurse -File -Filter "faith_multisource_case_002h.py" | Select-Object -First 1
if (-not $module) { throw "Last GitHub source version not found" }
$root = $module.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p "test_faith_environmental_context_002k.py" -v
if ($LASTEXITCODE -ne 0) { throw "002K scientific QA failed" }
python -X utf8 -m unittest discover -s "$root\tests" -p "test_faith_multisource_case_002h.py" -v
if ($LASTEXITCODE -ne 0) { throw "002H regression failed" }
$dir = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
$hi = Join-Path $dir "010HI_evidence.json"
$qa = Join-Path $dir "010HJ_spatial_qa.json"
$out = Join-Path $dir "boke_multisource_case_002k.json"
if (-not ((Test-Path $hi) -and (Test-Path $qa))) { throw "Missing original 010HI/J source files" }
if (Test-Path $out) { throw "Preserve previous scientific report; choose a new output" }
python -X utf8 $module.FullName --hi $hi --qa $qa --out $out
```

This is a deferred, consolidated validation; do not prompt the user to download a separate package for each milestone.
