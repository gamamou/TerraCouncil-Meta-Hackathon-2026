# TERRA-DEMO-001 — First integrated FAITH science debate in Edge

Milestone date: 2026-10-28. This milestone uses the EXISTING Meta Spark/Wonder runtime, scientific citations, decision matrix and human-reviewed oral/ElevenLabs system. It does not start an API call from GitHub.

## What's now connected

1. **Direct original local scientific input:** `src/local_council_server.py` now accepts `--hi <010HI_evidence.json> --qa <010HJ_spatial_qa.json>` as an alternative to the legacy `--evidence <screened list>`. It reuses `import_boke_010hi.build` via the source-checked six-indicator builder (`faith_indicator_expansion_002g.expand`) and conditionally adds genuinely verified CHIRPS AOI observations from the guarded original source. It does this **in memory**, never overwrites or publishes scientific originals.
2. **Edge live question preview/run:** both use the same HACK-016 planner, regional published context, FAITH environmental context (MAUS/Hansen/Cheng/CPDM) and CAMS/wind/AERMOD dust context. Dust items remain contextual and only genuine source-checked pilot measurements enter `evidence`.
3. **Dust explanation visible in Edge:** `ui/hack008.html` now renders the four investigation questions, required missing inputs, proposed methods and decisions they could inform, plus the clear notice that no mine-specific dust exposure has been validated.
4. **Actual runtime:** `dynamic_runtime.execute_dynamic` sends the same consent-bound plan to Spark and Wonder. Human scientific review remains mandatory after all structural checks; independent source limitations and debate dissent must be preserved.
5. **Decision and oral:** the pre-existing `dynamic_decision_matrix`, dynamic brief, oral narration, approval and ElevenLabs voice endpoints are not replaced. Spoken output is reconstructed/editorial, non-verbatim, and requires review/consent.

## First consolidated Windows validation and demonstration

Extract the LATEST repository ZIP, open its topmost project folder in VS Code, and run this PowerShell sequence. It works with nested GitHub ZIP structures:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$server = Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Telecharger la derniere archive TerraCouncil" }
$root = $server.Directory.Parent.FullName
foreach($test in @(
  "test_faith_indicator_expansion_002g.py",
  "test_faith_chirps_aoi_guard_002i.py",
  "test_faith_environmental_context_002k.py",
  "test_faith_dust_context_002l1.py",
  "test_faith_dust_debate_002m.py",
  "test_faith_scientific_council_002l.py",
  "test_terra_demo_001_direct_original_sources.py",
  "test_terra_demo_001_integrated_edge.py"
)) {
  python -X utf8 -m unittest discover -s "$root\tests" -p $test -v
  if ($LASTEXITCODE -ne 0) { throw "Echec scientifique : $test" }
}
$inputs = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
$hi = Join-Path $inputs "010HI_evidence.json"
$qa = Join-Path $inputs "010HJ_spatial_qa.json"
if (-not ((Test-Path $hi) -and (Test-Path $qa))) {
  throw "Fichiers originaux 010HI et 010HJ absents : conserver leur emplacement prive"
}
python -X utf8 $server.FullName --hi $hi --qa $qa --port 8765
```

If all validation passes, open the **printed** `http://127.0.0.1:8765` in Edge. Do not run with a stale 8765 server already listening; stop it first. Ask:

> Comment concilier extraction minière, poussières, forêt, eau et communautés à Boké, et quelles mesures faut-il prioriser avant une décision industrielle ?

Then click **Aperçu dynamique des preuves et agents**. Check the individual AOI source IDs, regional context entries, three dust sources, four dust scientific questions, missing PM10/PM2.5 site observation status, proposed number of potentially billed Meta calls and precise question. This preview uses 0 model calls.

Only after reviewing permitted content and costs, select the required checkboxes and trigger the **dynamic** debate. The server logs a unique local HACK-016 session in `Documents\TerraCouncil-Hack008-Sessions\Dynamic-HACK016`. Avoid a second trigger while a request is running or its result is uncertain.

After a COMPLETED and structurally checked trace, inspect the agent exchange and Wonder's objections, open **Matrice décisionnelle** and **Indicateurs FSDC**, review the editorial oral script, then explicitly approve voice synthesis if acceptable. Audio and model requests may be billed; no automatic generation or silent upload.

## Crucial limitations

- At most six prepared AOI indicator records from two underlying source families (WorldCover, WorldPop) unless real local CHIRPS source validation passes. National MAUS/Hansen/Cheng/CPDM and regional CAMS are separate scientific context and are **not** admitted as local AOI facts.
- A real new dynamic council debate has NOT been run by this milestone. The previous finished 2026-10-28 session remains unchanged. The new code and fixture-based QA are committed to GitHub, but test execution in the user's Windows environment and new recorded scientific debate are pending.
- Do not expose original private source data, local keys or recordings by uploading them publicly.
