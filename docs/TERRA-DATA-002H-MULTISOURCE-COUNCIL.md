# TERRA-DATA-002H — Multi-source debate case (source-separated)

Development milestone: 2026-10-28. This contribution **uses prior FAITH/FSMI and earlier TerraCouncil calculations without recomputation**.

The prior local council consumed only two broadly packaged `010HI/010HJ` AOI findings. This milestone connects:
- **AOI screened lane:** individual WorldCover 2021 cover-class indicators (5) and WorldPop 2026 population-cell estimate (1), derived by `faith_indicator_expansion_002g.expand` using the existing `import_boke_010hi.build` QA and source fingerprints.
- **Regional documentary lane:** existing `fsdc_evidence_expansion.attach_regional_context` records, including the peer-reviewed Kolie et al. 2024 abstract and historical GAC FODEL declaration when topics match; user-research CECIDE claim remains explicitly excluded.
- **Historic FAITH modeled point-context lane:** preserved NASA POWER Boké 2001–2025 point climatology, which is **outside the exploratory rectangle** and is **not inserted into AOI observations** or automatically forwarded to Meta.
- **CHIRPS source state:** original 010HI/010HJ references contain a matching CHIRPS hash but this alone is not a validated numerical finding. No fake CHIRPS observation is added. Similarly the existing FSMI CAMS ~45km sample is not a confirmed local mine dust concentration.

Added implementation: `src/faith_multisource_case_002h.py`, plus `tests/test_faith_multisource_case_002h.py`.

### Important counts and epistemic status

With the authentic source files used in the earlier 010HI/J ingestion, the AOI lane should contain **6 independently citable indicators from 2 independent datasets**. The exact regional documentary context count depends on the question and existing registry, and must be read from the actual output. A third documentary source family does not turn a national or regional statistic into a local geospatial impact. The HACK-016 plan may remain `READY_EXPLORATORY_MISSING_TOPICS` because the local PM10/dust measurement topic is still missing.

The generated file is an offline *case/preview only*; the original two-record screened file remains untouched. The case is not a completed Meta execution, not an automatic authorisation to transfer licensed data to Meta, and not scientific field validation. The UI runtime continues to require explicit source-sharing and paid model consent.

### Run once after the next consolidated GitHub update

```powershell
$module = Get-ChildItem . -Recurse -File -Filter faith_multisource_case_002h.py | Select-Object -First 1
if (-not $module) { throw "Latest GitHub module absent" }
$root = $module.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p "test_faith_multisource_case_002h.py" -v
if ($LASTEXITCODE -ne 0) { throw "Validation failed" }
$dir = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
$hi = Join-Path $dir "010HI_evidence.json"
$qa = Join-Path $dir "010HJ_spatial_qa.json"
if (-not ((Test-Path $hi) -and (Test-Path $qa))) { throw "Pre-existing scientific source files missing" }
$out = Join-Path $dir "boke_multisource_case_002h.json"
if (Test-Path $out) { throw "Do not overwrite an existing scientific snapshot" }
python -X utf8 $module.FullName --hi $hi --qa $qa --out $out
```

Subsequent implementation priority is **not** to generate more summary sources, but to inspect the actual authorized CHIRPS measurement payload and approved MAUS/Hansen geometries, then attach verified new independent AOI observations to the established council gate. Use the original evidence files, source permissions, matching spatial footprint and source hashes. Maintain a separate regional-context lane for approximated or documentary sources.

This milestone was committed to GitHub; execution of the tests with the user's local scientific files is pending.
