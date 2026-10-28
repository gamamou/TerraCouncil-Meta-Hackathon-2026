# TERRA-DATA-002G — Give Spark/Wonder more FAITH source-linked indicators

**Problem:** the existing local `boke_screened_evidence.json` exposes just 2 records, even though its original ESA WorldCover finding contains **five separate area-weighted classes** and the WorldPop record contains a separate population raster sum. This limits how narrowly models can cite findings.

**Implementation:** `src/faith_indicator_expansion_002g.py` calls the original, established `import_boke_010hi.build` (same 010HI/010HJ QA, original input SHA agreement, source file SHA, same exact rectangle and no validation promotion). It materializes:
1. WorldPop 2026 modeled raster population sum.
2. ESA WorldCover 2021 tree cover class 10.
3. ESA WorldCover 2021 cropland class 40.
4. ESA WorldCover 2021 built-up class 50.
5. ESA WorldCover 2021 permanent water class 80.
6. ESA WorldCover 2021 mangroves class 95.

**Caution:** 6 individually referenced indicator statements arise from only **2 independent geospatial datasets**. This is finer citation granularity, not 4 new scientific acquisitions or independently replicated studies. Coverage is the rectangular AOI [-14.5, 10.5, -14.0, 11.0] only; no claim of contemporary 2026 land change or mine attribution. Dust remains missing as AOI-admitted measurement. License and right to forward full records to Meta remain a separate requirement.

This exporter writes a **new private file** and refuses to overwrite an existing one. The original two-record file remains intact. Nothing is committed to public GitHub from the user's private raw source inputs.

## Windows validation and new six-indicator file

Download/extract the latest GitHub main. From its VS Code PowerShell root:

```powershell
$ErrorActionPreference="Stop"
$module=Get-ChildItem . -Recurse -File -Filter "faith_indicator_expansion_002g.py" | Select-Object -First 1
if (-not $module) { throw "Latest GitHub version missing" }
$root=$module.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p "test_faith_indicator_expansion_002g.py" -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
$inputs=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
$hi=Join-Path $inputs "010HI_evidence.json"
$qa=Join-Path $inputs "010HJ_spatial_qa.json"
if (-not ((Test-Path $hi) -and (Test-Path $qa))) { throw "Original 010HI/J inputs missing" }
$out=Join-Path $inputs "boke_screened_indicators_002g.json"
if (Test-Path $out) { throw "Output already exists, preserved for scientific integrity" }
python -X utf8 "$($module.FullName)" --hi "$hi" --qa "$qa" --out "$out"
if ($LASTEXITCODE -ne 0) { throw "Evidence derivation failed" }
$preview=Join-Path $root "src\faith_real_debate_preview_002f.py"
python -X utf8 "$preview" --evidence "$out" --scenario multidomain
```

Expected: **6** screened indicator records from **2** underlying sources (assuming the local 010HI/010HJ are the same source files previously screened). HACK-016 should select 6 relevant records, still show dust missing, and execute zero model calls. User-side real-file test not yet observed at time of commit.

## Connect to an actual debate (existing UI)

Once approved, supply `boke_screened_indicators_002g.json` as the evidence path to the **existing HACK-016 local server**, preview the exact question and set of six evidence IDs, review privacy/license, and separately authorize a Meta Spark–Wonder run. The existing `src/dynamic_runtime.py` uses exact source citations and a scientific critic. Do not mark a preview as a completed real debate. HACK-016's structural verification remains distinct from external scientific validation.

## What would add INDEPENDENT sources, not just indicators?

- Import vetted CHIRPS water/climate AOI observations from original private 010HI/J raw evidence when available under a documented source contract.
- Geospatially verify the existing MAUS/Hansen/Cheng and regional CAMS source records against the pilot rectangle with appropriate source geometry, rights and temporal coverage.
- Existing literature and regional reports can be included as **labeled scientific context** via `fsdc_evidence_expansion.py`, not misrepresented as spatially measured PM10.

No redundant API downloads or scientific recomputations are authorized by this module.
