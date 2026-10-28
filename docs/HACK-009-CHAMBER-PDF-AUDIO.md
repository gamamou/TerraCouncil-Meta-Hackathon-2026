# HACK-009 — Immersive Deliberation Chamber & Scientific PDF

Created during the Meta Hackathon 2026. **No Muse Code.** This milestone adds new integration capabilities to the HACK-008 interactive localhost application. Its audio playback explicitly reuses a *pre-hackathon* ElevenLabs experiment when the user supplies archive MP3s; it does **not** claim that archival audio voices the new HACK-008 debate.

## Delivered in source

1. **PDF Decision Brief**: `src/export_decision_pdf.py` checks the complete 4-step HACK-008 trace against the exact FSDC evidence fingerprint and repeats citation/finding checks. It rejects incomplete, tampered, or unverified runs, then generates a multi-section PDF containing the original question, FSDC evidence, 2 Spark perspectives, Wonder critique, revised Spark synthesis, investigation proposals, abstentions and scientific warnings. The PDF requires the third-party `reportlab` package. **No model calls.**
2. **Local PDF button**: `GET /api/pdf?id=<session-id>` generates/downloads the PDF from a saved complete, structurally checked run, only over localhost with the session token. The server never exposes arbitrary filesystem paths.
3. **Session history**: `GET /api/sessions` and local JSON session reopening mean a previous HACK-008 run can be revisited **without repeating or paying for four Meta calls**.
4. **Visual evidence context**: source-derived ESA WorldCover 2021 land-cover percentage bars, clearly labeled preliminary, for the rectangular Boké area. No invented measures, biodiversity conclusions, mining damage or trend claims.
5. **Audio chamber (first stage)**: HTML audio player accepts *user-selected local MP3 files*. It labels prior ElevenLabs files as a separate pre-hackathon archive and does NOT claim that they correspond to the current four live model interventions. No paid ElevenLabs call or audio synthesis occurs here.

## Explicit remaining work

- New session-specific natural French oral scripts, independently reviewed for faithfulness before synthesis.
- Authorized ElevenLabs TTS for each new deliberation; new costs and sharing decision are separate from Meta calls.
- Precise speaker-to-audio segment timestamp alignment for active agent visualizations.
- Better maps, geospatial interaction and data-driven visual narratives, from scientific datasets only.
- PDF language localization and human scientific approval/signature controls.
- Scientific validation of screened data: current only structural source checks.

## Launch on Windows (latest GitHub ZIP required)

In a new VS Code PowerShell terminal, from the extracted latest repository:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
python -m pip install reportlab
$server = Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Latest HACK-009 source not found" }
$evidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
if (-not (Test-Path $evidence)) { throw "FSDC evidence missing" }
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

Stop the old HACK-008 server first with Ctrl+C (otherwise TCP port 8765 is occupied). A Meta key is **not needed** to reopen a saved session or export its PDF. Open http://127.0.0.1:8765 in Edge, choose **Retrouver mes sessions**, open your last completed session, and click **Exporter le brief PDF**. It should download a PDF without a Meta call. To explore historical ElevenLabs audio, choose its MP3s manually; its archive label must remain visible.

## Quality and provenance requirements

The report is explicitly **exploratory/not field validated**, and even a structurally verified session requires human scientific review. The XML/HTML playback does not imply verified narrative alignment. Never publish private JSON traces or unreviewed audio in the public repository. Production deployment will require separate real authentication, authorization and file-sharing policy.

## Testing

```powershell
$root = $server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_*.py" -v
```

The PDF-related tests skip the optional reportlab test if it is not installed. All tests are synthetic and do not call Meta or ElevenLabs.

**Status:** GitHub source committed; user-side Windows integration and PDF review pending.
