# HACK-005 — First live Meta Spark pilot (opt-in, one call)

Built during hackathon. **No Muse Code**.

The new `src/live_pilot.py` uses the previously imported Boké screened evidence and calls `muse-spark-1.3` **at most once**, then submits the response to the independent HACK-003 verification gate. **It does not claim a full multi-agent deliberation or field validation**; that comes only after a successful first pilot and Wonder integration.

## Before any model call

- Confirm source dataset provenance, licensing and your authorization to transmit *derived* source findings to Meta. The preliminary Boké study includes WorldPop 2026 population estimates and ESA WorldCover 2021 land-cover percentages for a rectangular area; not an affected-population count, not field-validated, not mining causation.
- Keep `boke_screened_evidence.json` and all outputs outside the public GitHub repository. Don't publish API keys or private files.
- Read Meta Model API Standard mode data-processing terms and billing. The current official API base is `https://api.meta.ai/v1`. Model: `muse-spark-1.3`.
- No automatic retries. If an API request fails, it may still be billed; examine its saved trace and your Meta console before a new run.
- Run only if you accept a potentially billable external request. `--send-to-meta` and `--i-reviewed-sharing` are both required.

## Windows: retrieve latest repository and run

In VS Code open the **latest** extracted `TerraCouncil-Meta-Hackathon-2026-main` folder. The following command must find `live_pilot.py`. The input `boke_screened_evidence.json` should already be located under `$HOME\Documents\TerraCouncil-Scientific-Inputs` from HACK-004.

```powershell
$ErrorActionPreference = 'Stop'
$src = Get-ChildItem . -Recurse -File -Filter live_pilot.py | Select-Object -First 1
if (-not $src) { throw 'Download and extract the latest GitHub ZIP' }
$inputs = Join-Path $HOME 'Documents\TerraCouncil-Scientific-Inputs'
$evidence = Join-Path $inputs 'boke_screened_evidence.json'
if (-not (Test-Path $evidence)) { throw 'HACK-004 data missing' }
$question = 'Quelles investigations scientifiques prioriser pour le developpement minier a Boke ?'
$dryOut = Join-Path $inputs ('HACK005-dry-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
python -X utf8 $src.FullName --question $question --evidence $evidence --out $dryOut
if ($LASTEXITCODE -ne 0) { throw 'Dry run failed' }
```

Expected: `READY_EXPLORATORY_NO_MODEL_CALL`, `CALLS_ATTEMPTED: 0`.

## First real Meta call (only after human review)

```powershell
$secret = Read-Host 'Votre cle Meta Model API (pas ElevenLabs)' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try { $env:MODEL_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
$liveOut = Join-Path $inputs ('HACK005-Spark-live-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
python -X utf8 $src.FullName --question $question --evidence $evidence --out $liveOut --send-to-meta --i-reviewed-sharing
if ($LASTEXITCODE -ne 0) { throw 'Live pilot failed; do not retry automatically' }
Write-Host "Trace privee : $liveOut"
```

The printed `STATUS` will be `FIRST_META_RESPONSE_PASSED_STRUCTURAL_GATES`, `FIRST_META_RESPONSE_BLOCKED` or `CALL_FAILED_DO_NOT_RETRY_BLINDLY`. Only the first confirms a structurally acceptable response, not a scientifically validated result. A failed or blocked run requires review before any further external calls. If sharing the trace with an assistant, redact confidential model inputs and source data first.

## Local tests

```powershell
$root = $src.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root 'tests') -p 'test_*.py' -v
```

These tests use synthetic fixtures, no Meta calls.

## Next goal

After the first live Spark response passes the independent checks, run a controlled Muse Wonder scientific critique and a Spark revision, with persistent snapshots between calls and human review. Avoid an immediate six-call uninspected run.
