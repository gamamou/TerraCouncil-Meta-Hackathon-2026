# TERRA-DATA-002L — Scientific Council Integration (existing HACK-016 Edge runtime)

Date: 2026-10-28. Scope: **actual pre-existing TerraCouncil scientific debate interface**, not a second prototype.

## Implemented

1. `src/local_council_server.py` now uses `attach_environmental_context(attach_regional_context(plan_question(...)))` consistently for **both** `/api/dynamic-preview` and `/api/dynamic-run`. This fixes the earlier gap: 002K context was prepared in the offline `002H` case but had not reached the interactive Edge live debate. Same question, evidence and environmental context must be present in the consent-bound plan fingerprint. Current `plan_sha256` binding is preserved.
2. The preview returns source identifiers, scientific statuses, geographic relation and source path even when contextual entries have **no public source URL**. Earlier code assumed every regional_context record contained `source_url`; this was false for 002K's FAITH historic entries and would have crashed Edge preview.
3. `src/dynamic_runtime.py` prompt rules now explicitly keep source-coverage COUNTS (MAUS FIDs, Hansen zones, Cheng historical classes, CPDM reference records) separate from pilot observations. Wonder is instructed to challenge source-scope transfer and identify the key unresolved disagreement; Spark final synthesis must prioritize falsifiable investigations and preserve dissent.
4. `tests/test_faith_scientific_council_002l.py` creates **synthetic test evidence only**, attaches the real source-context registry, and simulates a HACK-016 Spark/Wonder sequence using mocked model calls to verify the context enters model payloads without being promoted to AOI observations. It verifies preview/run source-path parity and plan fingerprint changes. **No Meta or ElevenLabs calls are made by these tests.**

## Safeguards

- The live paid model requests remain protected by separate `consent` and `share` booleans. No previous authorization is silently reused when the scientific context changes, since `regional_context_sha256` is included in `plan_sha256`.
- `plan.evidence`: only actual source-checked AOI findings. `plan.regional_context`: documentary plus historical national FAITH science, each scoped and caveated.
- Historical counts for Guinea are **not** findings of local mine damage in the Boké rectangular pilot. In particular, 640 Hansen zone records ≠ 640 field sites, 707 Cheng classifications ≠ 707 active mines, 1012 CPDM screening rows ≠ 1012 confirmed polygon overlaps.
- The input evidence file supplied when launching the existing local server determines how many actual pilot observations are available. Updated server code does NOT transform the original two-record private file into the six-record version: load the newly prepared file if broader indicator citations are desired.
- A model's successful structural FSDC checks still require human review and do not validate scientific source correctness or legal permission to share material with Meta.

## One consolidated Windows QA session, later

Open the latest GitHub ZIP in VS Code PowerShell, then:

```powershell
$ErrorActionPreference="Stop"
$module=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $module) { throw "Latest TerraCouncil version absent" }
$root=$module.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p test_faith_scientific_council_002l.py -v
if ($LASTEXITCODE -ne 0) { throw "002L tests failed" }
python -X utf8 -m unittest discover -s "$root\tests" -p test_hack016i_real_debate_readiness.py -v
if ($LASTEXITCODE -ne 0) { throw "HACK016I regression failed" }
```

Tests are committed, **not yet executed on the user's Windows runtime**. After QA, use Edge dynamic preview first, verify the selected evidence and contexts and separately authorize the exact Meta calls if rights allow. Do not claim an actual new debate has occurred until its trace is saved.

## Next decision

The desired scientific milestone is an **actual audible source-bound debate in French** and a scrutinizable decision matrix, not more metadata-only modules. Source-wide historic context can enrich scientific questioning, but it does not substitute for exact new Boké AOI observations. The original 002J MAUS GeoPackage spatial crosswalk and proper source licensing remain pending before local mining indicators can be promoted.
