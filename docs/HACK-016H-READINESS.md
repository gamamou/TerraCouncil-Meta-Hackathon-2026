# HACK-016H — Edge readiness and first end-to-end real debate

The previous screenshot showed **MODEL_API_KEY absent** and **no HACK-016 dynamic sessions in the active server folder**. These are two different conditions. A loaded web interface proves only that the local application is running; it does not demonstrate successful Spark/Wonder model calls.

## Implemented

- src/dynamic_readiness.py: zero-network inspection of current process credential presence (boolean only), selected WorldPop/WorldCover evidence, PM10 abstention, and separate HACK-008 vs HACK-016 history counts.
- GET /api/dynamic-readiness: authenticated local diagnostic; reports the actual active session directory and missing conditions, never the API key.
- Edge diagnostic panel shows the scientific question examples and a click-to-fill control. Filling does not auto-launch paid model calls.
- Meta and ElevenLabs consent checkboxes reset on each page load.
- tests/test_hack016h_readiness.py: mocked scientific inputs, missing dust, old vs dynamic history, no-cost checks.

## Windows no-cost check

Stop the previous server, extract the latest GitHub ZIP, open the extracted folder in VS Code PowerShell:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$server = Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Latest server missing" }
$root = $server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_hack016h_readiness.py" -v
if ($LASTEXITCODE -ne 0) { throw "Readiness tests failed" }
$evidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

Open http://127.0.0.1:8765 and choose **Vérifier la configuration**. Verify whether the current Python server process has the Meta key, which directory holds its dynamic sessions, and which evidence is available for each example question.

If a Meta key has been authorized and configured previously, you must launch this Python process from the terminal where `MODEL_API_KEY` is set. Keys in a different PowerShell or VS Code terminal do not automatically carry over. Never paste keys in a chat, screenshot or repository. Starting a session requires separate Meta cost and sharing consent. If you do not want to run a paid debate yet, the readiness and evidence preview require no key.

If an earlier dynamic run exists in a *different* folder, restart the server with `--out-dir` pointed to its **parent HACK008 session folder**. The server expects dynamic session files under `<out-dir>/Dynamic-HACK016/`. The diagnostic prints the actual directory being used. This avoids pretending that old saved sessions were deleted.

This milestone does not ingest new external FSDC sources or claim PM10 measurements. The evidence-gated Meta debate, dynamic narration, PDF and optional paid audio paths are preserved as previous milestones.

## What the UI does not certify

Presence of a key only proves a nonempty environment variable in the server process, not validity, permission, quota, supported model or provider connection. Numeric estimates in WorldPop and WorldCover remain SCREENED_NOT_FIELD_VALIDATED and cannot establish causal mining impacts or exposed individuals.

No real Meta or ElevenLabs calls were made by the development code changes. User-side Windows test confirmation is pending.
