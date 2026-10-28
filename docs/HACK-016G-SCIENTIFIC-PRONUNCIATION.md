# HACK-016G — Safe scientific pronunciation, less manual voice preparation

This release improves the dynamic council voice experience without generating or translating scientific claims. The original model interventions and FSDC evidence are preserved.

## What is implemented
- src/scientific_pronunciation.py — reversible, deterministic spoken expansions for recognized tokens: PM10 → P M dix, PM2.5 → P M deux virgule cinq, AERMOD → A E R M O D, FSDC → F S D C and ESG → E S G.
- No blind numeral-to-words conversion. Unknown numbers, percentages, dates, formulas, English fragments and non-speech symbols still cause review rather than silent reinterpretation.
- src/dynamic_oral_audit.py now differentiates recognized scientific acronym pronunciation from an unreviewed change in the scientific meaning.
- src/dynamic_voice_plan.py uses the pronunciation-rendered speech payload while preserving the exact original investigation, abstention, model name and evidence IDs in the verified session.
- /api/dynamic-voice-preview?id=... returns a zero-API-call preview with per-turn source text, spoken text and allowed substitutions.
- Edge dynamic voice panel adds **Aperçu vocal sans appel payant**. Separate consent remains required to send any text to ElevenLabs. No automatic paid model or voice requests.
- tests/test_hack016g_pronunciation.py checks normalization, rejection of unknown numerical values, English rejection, and source-preserving dynamic narration.

## Windows no-cost verification
Stop the prior localhost server, download the latest GitHub ZIP and extract it to a fresh directory. In VS Code PowerShell:

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Updated local server missing" }
$root=$server.Directory.Parent.FullName
if (-not (Test-Path (Join-Path $root "src\scientific_pronunciation.py"))) { throw "HACK-016G missing" }
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p test_hack016g_pronunciation.py -v
if ($LASTEXITCODE -ne 0) { throw "Pronunciation checks failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

Open http://127.0.0.1:8765, use **Historique dynamique** and open a completed HACK-016B session. In its dynamic audio panel, select **Aperçu vocal sans appel payant**. If the script is eligible, the screen displays the spoken text and the exact replacements; no paid Meta or ElevenLabs call occurs. If blocked, inspect the reported error. The preview requires the two voice IDs to be configured in the PowerShell environment running the server, but the ElevenLabs key is not required for a free preview.

Only separately and after the eligible preview and appropriate authorization should a user choose to generate a potentially billed ElevenLabs voice. Do not click a second time after an error; check the saved attempt ledger first.

## Scientific limitations
This is a *pronunciation* layer, not multilingual translation and not independent scientific validation. It does not certify any generated claim as scientifically accurate or field-validated. Numerical exposure or air quality concentrations remain unavailable without actual matching FSDC measurements. The current normalization whitelist is deliberately small. More lexical terms and semantically tested French translation should be introduced only with reference-backed QA.
