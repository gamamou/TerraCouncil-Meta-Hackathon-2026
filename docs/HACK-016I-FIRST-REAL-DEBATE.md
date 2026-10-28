# HACK-016I — First real dynamic debate integrity hardening

This milestone prepares a *real* question-specific Spark/Wonder debate with no hidden or automatic paid requests. Existing HACK-008 through HACK-016H sessions remain untouched.

## Corrected behavior

- src/dynamic_council.py: a plan_sha256 fingerprint now covers the exact user question, geography, sector, source SHA256, requested topics, selected agents and missing evidence.
- Local server: /api/dynamic-preview returns that plan ID and the maximum intended Meta calls; /api/dynamic-run requires both the exact original evidence fingerprint and the plan fingerprint. A changed question with the same WorldCover record cannot reuse consent to an old preview.
- src/dynamic_runtime.py: clearer mandatory four-key JSON instructions for the models. Each verified observation must reproduce the exact evidence ID and finding from FSDC, while hypotheses, investigations and abstentions remain separate. No undocumented numerical facts or claims of field validation.
- Edge: preview displays 0 calls actually consumed and up to six calls expected for the chosen council. It submits the plan fingerprint when the user explicitly authorizes real Meta calls. Consents are reset after accepting the request; no automatic repeat.
- tests/test_hack016i_real_debate_readiness.py: two different questions with the same evidence must have different plan hashes; mock model positions and critiques must pass the FSDC check; unsupported dust PM10 questions abstain.

## Test without Meta billing

In latest extracted GitHub repository, VS Code PowerShell:

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Missing server" }
$root=$server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p test_hack016i_real_debate_readiness.py -v
if ($LASTEXITCODE -ne 0) { throw "HACK-016I regression failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

In Edge, choose a question about WorldCover land cover, run **Aperçu dynamique des preuves et agents**, verify selected source IDs and maximum calls. Only after verifying the exact plan may the user separately authorize the paid Meta execution. The model may still return an invalid response; such a run stops and is journaled, never retried automatically. The structural checker is not independent scientific or field validation.

No provider calls or live Windows tests were performed while developing this milestone. The next demonstration should assess an actual completed HACK-016 session in the Edge history before generating audio.
