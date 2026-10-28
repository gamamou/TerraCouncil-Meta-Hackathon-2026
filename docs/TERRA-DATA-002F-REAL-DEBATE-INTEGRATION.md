# TERRA-DATA-002F — Existing FAITH evidence to actual HACK-016 debate preview

**Development date:** 28 October 2026. **Original scientific data:** pre-existing FAITH/FSMI. New contribution: binding to the existing TerraCouncil HACK-016 planner without recalculation.

Implemented:
- `src/faith_real_debate_preview_002f.py` calls the existing `dynamic_council.plan_question` on the *original local Boké screened evidence list*. It does not replace, rewrite or duplicate the source observations.
- Supports land-use, multidisciplinary and climate questions. The planner's own metadata/source/geography gate determines the number of usable observations and missing topics.
- Retrieves the already recovered FAITH Boké NASA POWER modeled point from `faith_boke_context_guard_002e.py` **only as separately labeled context**. The reference point is outside the exploratory Boké rectangle; it **never enters** the pilot's admissible evidence list.
- Does not invoke Meta, ElevenLabs, Base44 or an API and does not add new geospatial calculations.
- `tests/test_faith_real_debate_preview_002f.py` checks abstention without evidence, geographical exclusion, three question options and invalid input. Tests are published, **Windows execution still pending**.

Windows, after updating the GitHub ZIP:

```powershell
$module = Get-ChildItem . -Recurse -File -Filter faith_real_debate_preview_002f.py | Select-Object -First 1
if (-not $module) { throw "Version GitHub trop ancienne" }
$root = $module.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p test_faith_real_debate_preview_002f.py -v
if ($LASTEXITCODE -ne 0) { throw "Tests echoues" }
$source = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
if (-not (Test-Path $source)) { throw "Missing original evidence file" }
python -X utf8 $module.FullName --evidence $source --scenario multidomain
```

The result lists HACK-016's usable evidence count, explicitly missing topics and an isolated, non-citable climate context. A positive evidence count is possible only from the existing screened WorldCover/other original records that pass the pre-existing HACK-016 gate, not from the catalog, the NASA point or synthetic values.

**For actual dynamic Spark–Wonder execution:** continue using the existing local server/UI HACK-016I preview, which requires explicit paid API authorization and produces a session-specific scientific trace. Existing completed HACK-016J sessions and dialogue audio are preserved. This module is a factual readiness integration, **not** a live Meta debate.
