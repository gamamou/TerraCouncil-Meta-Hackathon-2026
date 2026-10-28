# HACK-016C — Question-specific French oral draft

This is the next step toward autonomous debate narration. Every script is now extracted from the actual verified HACK-016B session instead of the fixed Boké four-paragraph text.

New files:
- src/dynamic_narration.py — builds one oral turn per recorded position, critic and final synthesis. Draws directly from actual saved investigations and abstentions, checks the original source fingerprint and verifies each original observation.
- /api/dynamic-oral?id=... — localhost token-protected endpoint; no Meta/ElevenLabs calls.
- Edge dynamic session panel — 'Voir le scénario oral dynamique' button renders every actual spoken turn and its evidence identifiers.
- tests/test_hack016c_narration.py — simulated two-question regression and tamper/incomplete record rejection.
- src/dynamic_runtime.py — asks future Spark/Wonder responses to write free-form investigations and abstentions in natural French, while retaining exact original FSDC observation findings even if they are English.

Important: original historical HACK-016B sessions may contain English prose. The extractive draft preserves it faithfully instead of pretending to translate automatically. These turn drafts are not automatically approved for paid voice production; language anomalies, digits and excessive total length require editorial adaptation. Automatic source-faithful translation and speech synthesis remain future work. No new Meta/ElevenLabs calls are made to view oral drafts.

Windows check:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Updated server absent" }
$root=$server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p test_hack016c_narration.py -v
if ($LASTEXITCODE -ne 0) { throw "Narration regression failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

In Edge open the dynamic session history, reopen a completed HACK-016B debate and click **Voir le scénario oral dynamique**. The actual text is drawn from that session, not from the HACK-008 standard pilot.

Scientific caveat: A source match is not scientific field validation, automatic semantic equivalence verification or investment authorization. In this stage the oral draft is available for examination; automatic speech/audio is still gated.
