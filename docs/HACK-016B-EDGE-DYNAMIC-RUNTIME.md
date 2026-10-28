# HACK-016B — Dynamic scientific debate in Edge

HACK-016B is a new execution path alongside the stable legacy HACK-008/HACK-015 demo. For the current pilot, the evidence catalogue is still local Boké FSDC JSON, not an AWS-wide scientific discovery service.

## Added
- src/dynamic_runtime.py: saves a private dynamic session JSON and durable checkpoint **before each potentially billed Meta model call**. It never retries a failed request. Independent FSDC verifier runs after every model step and must pass before another step executes.
- src/local_council_server.py: protected POST /api/dynamic-run and GET /api/dynamic-sessions, /api/dynamic-status. Each new question creates an HACK016 session in Documents/TerraCouncil-Hack008-Sessions/Dynamic-HACK016.
- ui/hack008.html: dedicated dynamic conversation panel with a unique question-to-evidence preview binding, explicit data sharing and cost consents, progress, agent interventions, session history and retrieved summaries.
- src/dynamic_council.py: unrecognized questions abstain rather than substituting unrelated data; unsupported dust measurements cannot be inferred from WorldCover.
- tests/test_hack016b_runtime.py: simulated Spark and Wonder, step preservation, false-claim block and dust abstention checks. The tests do not use external APIs.

## Windows PowerShell — tests first
Stop any older TerraCouncil server, extract the current GitHub ZIP into a new folder, and open the folder in VS Code.

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$server = Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Serveur TerraCouncil introuvable" }
$root = $server.Directory.Parent.FullName
if (-not (Test-Path (Join-Path $root "src\dynamic_runtime.py"))) { throw "HACK-016B absent" }
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_hack016b_runtime.py" -v
if ($LASTEXITCODE -ne 0) { throw "HACK-016B tests failed" }
$evidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

In Edge open http://127.0.0.1:8765. Enter a question, click **Aperçu dynamique des preuves et agents**, inspect the source IDs and missing topics. An unsupported dust-only question should not enable a paid run.

Only if the preview passes, you may tick both **dynamic** checkboxes and click **Déclencher le débat dynamique**. This explicitly authorizes a fresh set of potentially billed Meta calls (up to six in the current registry). No ElevenLabs calls occur, and no fixed script or fixed PDF is presented as a product of the dynamic run.

The dynamic history button can reopen a saved result without new Meta calls. On a network failure or verifier block, the session remains STOPPED_DO_NOT_RETRY_BLINDLY; inspect it and account history before considering another attempt.

## Honest status
- GitHub source committed; Windows tests and real user-facing dynamic Meta run have not yet been verified.
- The evidence classifier is keyword-based and the dataset catalogue limited to loaded local records.
- Spark and Wonder generate novel content on each run and are independently checked for exact quoted observations, but hypotheses/investigations remain nonvalidated inferences.
- The legacy PDF V3 and voice script are fixed-pilot-only, and deliberately remain separate from HACK-016B. Dynamic written and spoken briefs must derive directly from this saved new trace during subsequent HACK-016C/D work.
