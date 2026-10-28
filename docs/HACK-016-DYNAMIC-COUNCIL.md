# HACK-016 — Dynamic evidence-driven FAITH Council

The first dynamic runtime slice is now committed. It does not claim that all FAITH datasets are indexed or that investment decisions are autonomous.

## Files
- src/dynamic_council.py: identify question themes, choose registered FAITH agents, retain only matching local FSDC observations, list missing themes and record evidence hashes.
- src/dynamic_debate.py: new Spark analytical positions, Wonder criticism, Spark revision, structural source gate after each model call.
- src/ask_dynamic_council.py: no-cost preview by default; opt-in paid run with a unique persisted output journal and no silent overwrite.
- src/local_council_server.py and ui/hack008.html: local dynamic-plan preview without new model calls.
- tests/test_hack016_dynamic.py: source selection, distinct fingerprints, unsupported dust abstention, simulated four-to-six step debate.

## Windows no-cost test
Extract the latest GitHub ZIP and open it in VS Code PowerShell:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$script = Get-ChildItem . -Recurse -File -Filter ask_dynamic_council.py | Select-Object -First 1
if (-not $script) { throw "HACK-016 missing" }
$root = $script.Directory.Parent.FullName
$evidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p test_hack016_dynamic.py -v
if ($LASTEXITCODE -ne 0) { throw "HACK-016 tests failed" }
python -X utf8 $script.FullName --question "Quelles concentrations PM10 de poussière à Boké ?" --sector mining --evidence $evidence
python -X utf8 $script.FullName --question "Que montre l'occupation du sol à Boké ?" --sector mining --evidence $evidence
```

Expected: dust-only question abstains because dust concentration evidence is missing; land-cover question finds existing WorldCover evidence. All preview steps consume zero paid calls.

## Honest limitations
This is transparent keyword matching on locally supplied screened data, not a complete semantic/scientific search. No invented dust measurements, no inferred impact and no field validation. The old Edge debate launch is still HACK-008 fixed Boké; the new Edge preview is HACK-016 dynamic. The old fixed oral text and PDF V3 cannot truthfully represent a new dynamic debate. Connecting the dynamic run, new source-grounded oral script and genuinely dynamic brief inside Edge is the next integration milestone. These code commits have not yet been executed on the user's Windows PC.
