# HACK-016C/D — New debate, new oral text and new decision report

This integration removes the prewritten Boké text from the **dynamic** session output path. The legacy HACK-008/HACK-015 demo remains separate.

## New outputs

- `src/dynamic_narration.py`: deterministic, extractive oral draft, one turn for each *actual* dynamic Spark/Wonder step. Uses the first original investigation and scientific abstention from that turn. Checks the session status, original FSDC snapshot hash and exact verified observations. The spoken draft varies when the actual model outputs vary.
- `GET /api/dynamic-oral?id=...`: displays dynamic script only for a completed HACK-016B session, without any paid request.
- `src/dynamic_brief.py`: PDF report generated from that session's question, source snapshot, agent arguments, Wonder critique, final Spark synthesis, missing topics and evidence provenance.
- `GET /api/dynamic-brief?id=...`: downloads the new session-specific PDF, not the fixed Boké Executive Brief V3.
- Edge has two new controls inside **HACK-016B · Délibération dynamique**: `Voir le scénario oral dynamique` and `Télécharger le brief dynamique`.
- `tests/test_hack016c_narration.py` and `tests/test_hack016d_brief.py` use mocked models, checking change of oral text between questions and rejection of modified evidence.

## Important scope and limits

The narration is genuinely source-dependent but presently **extractive**. Its French framing comes from a template; the quoted investigation and abstention remain in their source language. The future Spark/Wonder runtime now asks free-form analysis in French, while exact English scientific findings stay unchanged. Older English sessions need appropriate translation review. Automatic TTS is deliberately disabled until a semantic-fidelity/translation gate exists, and no ElevenLabs or Meta model call is triggered by reading either output. The PDF may also carry the source language. No field-science validation is implied.

## Windows quick test

Extract the latest repository GitHub ZIP to a new folder and open it in VS Code PowerShell:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$server = Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Server missing" }
$root = $server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_hack016c_narration.py" -v
if ($LASTEXITCODE -ne 0) { throw "Oral regression failed" }
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_hack016d_brief.py" -v
if ($LASTEXITCODE -ne 0) { throw "Dynamic PDF regression failed" }
$evidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

Open Edge at http://127.0.0.1:8765, click **Historique dynamique**, open an already completed dynamic HACK-016B session, then use the two new buttons. These actions consume **zero** Meta/ElevenLabs calls. They do not modify the original session.

## Further work before claiming hands-off autonomous narration

1. Human-evaluated source-aware French translation/normalization for English and digits, with machine checks that do not silently change scientific conclusions.
2. Automatic gate with escalation on mismatched claims; only low-risk approved narration eligible for ElevenLabs under user-configured data-sharing and cost budget.
3. Larger science dataset registry and spatial/temporal search, including real dust/air-quality data where available.
4. More editorially polished dynamic PDF design beyond the initial scientifically faithful report.

No user Windows regression or actual dynamic audio synthesis has been observed for this newly committed release.
