# HACK-008 — Interactive Local Scientific Council

**Created during the Meta Hackathon, without Muse Code.** This module connects a local Edge UI to actual Meta Model API calls, rather than displaying a prerecorded simulation.

## What is implemented

- `src/local_council_server.py`: standard-library HTTP server bound to `127.0.0.1` only, ephemeral anti-CSRF token, explicit consent to share screened evidence with Meta and approve potentially billed calls.
- `ui/hack008.html`: French question entry, source inspection, consent controls, progress and structured results.
- `tests/test_local_council_server.py`: synthetic tests for successful 4-call sequence, block on unsupported claim, failed call, abstention and missing key.
- Uses the real HACK-004 screened Boké evidence JSON from **local Documents only**.
- Flow: Spark mining perspective → Spark environment perspective → Wonder independent critique → Spark revision. Every step has the HACK-003 independent citation-and-exact-finding verification gate.
- Journals each attempt to `$HOME\Documents\TerraCouncil-Hack008-Sessions`, with no credentials. No automatic retries. A browser refresh does not itself start a new run.
- 4 calls **maximum per expressly authorized run** (can incur charges), none when page loads.
- A failed/blocked step stops later calls; result is not presented as a scientific endorsement.

## Setup in Windows VS Code

1. Download the **latest** ZIP from [TerraCouncil-Meta-Hackathon-2026](https://github.com/gamamou/TerraCouncil-Meta-Hackathon-2026), extract completely and open that folder in VS Code.
2. Verify `boke_screened_evidence.json` is available under `$HOME\Documents\TerraCouncil-Scientific-Inputs`.
3. Open a new PowerShell terminal and load your Meta Model API key **locally** if absent:

```powershell
$secret = Read-Host 'Cle Meta Model API' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try { $env:MODEL_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
```

4. Start the localhost server:

```powershell
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$server = Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw 'HACK-008 absent; extract latest ZIP' }
$evidence = Join-Path $HOME 'Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json'
if (-not (Test-Path $evidence)) { throw 'HACK-004 screened evidence not found' }
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

The terminal will remain occupied while the local server runs. Open `http://127.0.0.1:8765` in Edge. Inspect source records, submit a question and check both authorization boxes only if you accept sending the data to Meta and the potential cost. The first browser load makes **zero API calls**. Don't paste your key into the web page or share it in chat.

Stop the local server using **Ctrl+C** in the PowerShell terminal.

## Current scientific and product limitations

- The pilot uses **two actual agent perspectives** (mining and environment) with Wonder critique and Spark synthesis. It does NOT yet execute agriculture, energy, communities, governance or a complete eight-stakeholder council.
- Source data are screened but `NOT_FIELD_VALIDATED`. WorldPop does not measure mining exposure; WorldCover 2021 does not establish 2026 land-cover change or biodiversity status.
- Model responses are subject to strict JSON, exact finding copy and known citation ID checks. A passing check **does not** mean a claim is scientifically true. Freeform suggestions remain unverified, and human review is mandatory.
- Browser-local API has no authentication for remote distribution. Never bind this development server to a public interface or expose its port outside localhost.
- This isn't a deployed product; live external API behavior needs participant-side testing and possible request-format adjustments. No promise of completed live HACK-008 runs before execution.
- Older audio/PDF and previous TerraCouncil exploration remain separate pre-hackathon work.

## Tests (no API key and no remote calls)

```powershell
$root = $server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root 'tests') -p 'test_*.py' -v
```

Tests use fake model answers and a temporary private folder.

## Next

Validate the new web UI in Edge, review the first actual 4-step session and errors, then improve user-facing structured disagreements and the authoritative decision-support dossier. Preserve metadata and the distinction between simulated stakeholder perspectives and real stakeholders.
