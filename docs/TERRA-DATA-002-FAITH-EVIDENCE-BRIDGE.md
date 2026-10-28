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

## First real-source local acceptance (28 October 2026)

The user's actual Windows PowerShell output confirms a successful read-only ingestion of the pre-existing 572-row MAUS v1 overlap CSV after locally removing UTF-8 BOM from the private input manifest. The bridge reported `AUDITED_ASSETS=1`, `SCIENTIFIC_STATUS=RECOVERY_INTAKE_NOT_SCIENCE_ADMISSION`, and `COUNCIL_EVIDENCE_GENERATED=0`. The recovery report was stored privately under Documents; no file contents were committed. This does **not** establish scientific admissibility or a completed live council input.

The permanent BOM-handling patch and its regression test were separately committed after the download used for this run. They were not part of this executed local acceptance.

## Cross-studio inventory linked

The new machine-readable `config/faith_fsmi_existing_sources_002.json` catalogs 12 source rails already present or documented in FSMI, with precise file paths, real source universes and explicit Boké geography/rights gates. These are provenance pointers, **not** data downloaded or incorporated into agent evidence. This work is hackathon source integration engineering; the original historical science remains attributed to FAITH.

## TERRA-DATA-002D — Question-to-source trace (28 October 2026)

Implemented in `src/faith_question_source_selection_002.py` and tested in `tests/test_faith_question_source_selection_002.py` (tests committed; **execution pending**).

This function reuses the existing `HACK-016` question classifier and planner, matching topics against the existing twelve-source FSMI/FAITH catalog. It reports which source pointers are thematically relevant and which are geographically excluded or need AOI validation. It also invokes `plan_question(question, [])` with **zero evidence** to confirm scientific abstention rather than silently elevate catalog metadata into observations. It performs no network calls, no model calls and no scientific recalculation.

Windows latest GitHub checkout:
~~~powershell
$script = Get-ChildItem . -Recurse -File -Filter "faith_question_source_selection_002.py" | Select-Object -First 1
if (-not $script) { throw "Actualiser TerraCouncil depuis GitHub" }
$root = $script.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_faith_question_source_selection_002.py" -v
python -X utf8 $script.FullName --question "Comment concilier extraction minière, poussière, forêt, eau et communautés à Boké ?" --geography "Boké, Guinea"
~~~
An expected **`ABSTAIN`** status means only that this source discovery pass does not yet have admitted Boké observations; it is **not a failure of source discovery**. Do not interpret pointers as geolocated source observations. The next scientific step is approved private source access and exact AOI crosswalk, not new source acquisition.
