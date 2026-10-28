# TERRA-DATA-002 — FAITH Scientific Evidence Bridge (source-safe)

## Goal and integration boundary
Reuse **existing** FMI/FSMI science, read-only, before acquiring a new public API dataset. TerraCouncil's \`src/verification.py\` requires exact evidence geography, explicit provenance, observational method, license and validation status. The bridge does **not** auto-mark historical screening as \`ADMISSIBLE\` or create \`READY_EXPLORATORY\` debate records without verified AOI/rights.

## What is implemented
\`src/faith_scientific_evidence_bridge_002.py\`: Python standard library, no external API, model call, GeoPandas, Base44 mutation or recomputation. Supported file families:

- \`FSMI_HANSEN_640\` — \`maus_evidence_640_v101.csv\`, 640 row MAUS×zones source
- \`FSMI_CHENG_CLASSES\` — \`guinea-cheng-landuse-index.json\`, 707 class observations/199 source sites (not surface hectares)
- \`FSMI_CAMS_REGIONAL\` — \`guinea-cams-air-quality-september-2026.json\`, 10 regional modeled atmospheric contexts
- \`FSMI_WORLDPOP_OSM\` — \`guinea-worldpop-buildings-buffers.json\`, 10 screening populations/building contexts
- \`CPDM_FOOTPRINT_REFS\` — \`guinea-observed-footprint-screening.json\`, 1,012 legacy reference records (not 1,012 verified MAUS intersections)
- \`FSMI_WIND_HOURLY\` — \`guinea-hourly-wind-september-2026.json\`, 10 model meteorology contexts
- \`MAUS_LEGACY_572\` — \`maus_v2_overlap_by_license.csv\`, 572 rows from historic v1 workflow, distinct from 22,430 national CPDM

**Read-only output**: immutable file SHA256, source size, expected row count, geography *as described by source*, preservation of source status and an explicit \`QUARANTINED_UNTIL_AOI_AND_LICENSE_REVIEW\` guard. No source contents or personal records copied into output. Initial SHA256 capture is **not** proof of prior canonical identity unless the manifest declares an independently verified hash.

## Usage in the latest downloaded repository
From VS Code Windows PowerShell:
~~~powershell
$bridge = Get-ChildItem . -Recurse -File -Filter "faith_scientific_evidence_bridge_002.py" | Select-Object -First 1
if (-not $bridge) { throw "Download current GitHub repository version first" }
$repo = $bridge.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $repo "tests") -p "test_faith_scientific_evidence_bridge_002.py" -v
python -X utf8 $bridge.FullName --list
~~~

Create a private input pointer file (outside the public repository) after obtaining a legitimate local copy or approved export of these Base44 source artifacts:
~~~powershell
$private = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
New-Item -ItemType Directory -Force -Path $private | Out-Null
$source = Join-Path $private "FSMI-READ-ONLY"
$manifest = Join-Path $private "FAITH-BRIDGE-INPUTS.json"
$report = Join-Path $private ("FAITH-BRIDGE-REPORT-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".json")
@{
  "FSMI_HANSEN_640" = @{
    path = (Join-Path $source "maus_evidence_640_v101.csv")
  }
  "FSMI_CHENG_CLASSES" = @{
    path = (Join-Path $source "guinea-cheng-landuse-index.json")
  }
} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifest -Encoding utf8
python -X utf8 $bridge.FullName --manifest $manifest --out $report
~~~
**The example expects real source files under \`$source\`.** It does not create or download them, and must fail if missing. Do not enter an empty placeholder file and call it scientific acquisition. Original Base44 files may be retained in controlled app storage; exports/access rights require review before local copies.

## Next scientific work required before paid council dialogue
1. Read source files from the controlled Base44 app or approved immutable private export, including their scientific manifest.
2. Pin verified source hashes and version, compare traceability and source rights.
3. Identify a real, independently verified **Boké AOI** and specific indicators whose source footprint covers it. National statistics or approximate bbox-point data cannot silently become Boké-specific observations.
4. Create factual \`evidence_id\` records consistent with existing \`src/verification.py\` without bypassing source status, then run \`plan_question\` in zero-model mode and inspect which domains must abstain.
5. Invoke the existing Spark/Wonder discussion and human-reviewed audio only when exact source findings, agent-specific sources and rights are accepted.

## Jury-facing provenance
This bridge and its tests are **hackathon code**; FAITH/FSMI data and scientific methods were produced earlier. Commit dates are not source acquisition dates. Record exact passing test output before claiming execution. The bridge is a **source intake milestone**, not proof of completed Council scientific ingestion.

## User-executed acceptance checkpoint — 2026-10-28 (Windows PowerShell)

Execution location: `TerraCouncil-Meta-Hackathon-2026-main (24)` with Python `-X utf8`.

Command: `python -X utf8 -m unittest discover -s (Join-Path $repo "tests") -p "test_faith_scientific_evidence_bridge_002.py" -v`

Observed test report supplied directly by the participant: **Ran 7 tests in 0.115s — OK (skipped=1)**. Six passed: Cheng class and attribution quarantine, historical MAUS 572-row separation, CAMS malformed input rejection, empty-input no-success policy, expected source inventory, and unknown asset rejection. Symlink exclusion test **skipped due to lack of Windows symlink creation privileges**; this control has not been verified on that workstation. Do not label this 7/7 pass.

The `--list` command separately completed, enumerating all seven source families with the expected scientific status codes.

**Acceptance scope:** local software/tests and registry listing ONLY. No real Base44/FSMI science asset imported, no source hash checked by this bridge, no Boké AOI promotion, no Meta calls or scientific debate during this acceptance.
