# HACK-016E — Automated editorial fidelity gate

This milestone does not make final scientific or investment decisions and does not trigger paid TTS.

## Implemented

- src/dynamic_oral_audit.py: reconstructs the oral draft from the original dynamic session and checks every turn against source-bound investigation, scientific abstention, stage index, agent model, evidence IDs and session fingerprint. Any change of meaning-bearing text requires review, not a silent AI rewrite.
- Flags possible English, technical symbols, numerals and scripts exceeding the single-call TTS character budget.
- Returns statuses EXACT_EXTRACTION_CHECK_PASSED or REVIEW_REQUIRED. An exact match is a structural/extractive check, **never** external scientific validation or semantic verification.
- New localhost GET /api/dynamic-oral-audit?id=... and Edge button **Contrôle automatique de fidélité**. Both require an existing completed HACK-016B session.
- tests/test_hack016e_fidelity.py uses synthetic FSDC input and mocked Meta calls to test source preservation, editorial changes and tampering.

## Windows quick check

Stop the old localhost server, download and extract the latest GitHub ZIP, then open that folder in VS Code PowerShell.

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Latest TerraCouncil server not found" }
$root=$server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_hack016e_fidelity.py" -v
if ($LASTEXITCODE -ne 0) { throw "Fidelity test failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

Open http://127.0.0.1:8765 and use **Historique dynamique** to open an existing completed HACK-016B session. Then click **Voir le scénario oral dynamique** followed by **Contrôle automatique de fidélité**. Neither operation makes Meta or ElevenLabs calls.

## Next scientific/engineering gate

A true French translation/paraphrase engine must prove semantic consistency with original source-linked claims; lexical matching alone cannot establish such consistency. Safe automated conversion to speech also needs a separate account-authorized cost/sharing policy, voice-identity mapping for variable agent counts, and verified timestamps per source turn. Until such functionality is tested, HACK-016E never auto-authorizes paid speech.

Legacy HACK-015 remains separate and functional. HACK-016D PDF remains distinct from the original V3 pilot. HACK-016E source is committed but final Edge testing is pending.
