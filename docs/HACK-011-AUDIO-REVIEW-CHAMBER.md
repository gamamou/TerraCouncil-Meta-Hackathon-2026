# HACK-011 — Review Gate & Interactive Audio Chamber

## Why this milestone

The current HACK-008 Boké debate completed four **real** Meta model calls and was archived with its scientific evidence. The executive PDF and initial natural French audio storyboard were developed in HACK-010. HACK-011 ensures the TTS workflow cannot accidentally transmit an unreviewed fixed template or a technical model JSON.

**No Muse Code. No additional Meta calls.**

## New implementation

- `src/approve_oral_script.py` verifies the human-edited narration against the same complete HACK-008 session and screened FSDC evidence fingerprint. It allows only `turns[].text_to_review` to change; speaker, model, stage, evidence references and session identity must remain unchanged.
- A required `--i-reviewed-meaning` flag records explicit human editorial review, but is **not** scientific validation or a waiver of rights/terms checks.
- The TTS runner `src/render_session_audio.py` now requires **`--approved-manifest`** and independently re-verifies that manifest's digest and source binding. No TTS call will be made from an unapproved `oral-draft.json`.
- Edge offers **Projet oral modifiable (JSON)** alongside the friendly French TXT preview.
- Before playback, the browser verifies the selected MP3's SHA256 against the matching local timing manifest, rejects a different session, and highlights the active speaker while playing audio.
- 4 original interventions, a separate editable oral manuscript and the downloaded PDF remain **three distinct artifacts**. The spoken script is labeled `EDITORIAL_RECONSTRUCTION_NOT_VERBATIM`.

## Windows — update the app without new Meta calls

1. Stop the current Python server using Ctrl+C.
2. Download/extract the latest GitHub ZIP and reopen that directory in VS Code.
3. Start `local_council_server.py` with the same FSDC evidence path and port 8765 (same command as HACK-010); Meta API key is not required for replay and exports.
4. Open `http://127.0.0.1:8765`, choose **Retrouver mes sessions** then **Ouvrir cette session** (HACK008-20261028T010424-45b2d6b6).
5. Download **Projet oral modifiable (JSON)** as well as the human-readable French text.
6. Open the downloaded JSON in VS Code. Review and, if appropriate, edit only each `text_to_review`; do not modify scientific references, attribution, model names, IDs, metadata or the original HACK-008 trace.

## Approve the edited narrative, offline

From the updated repository's VS Code PowerShell:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$approver = Get-ChildItem . -Recurse -File -Filter approve_oral_script.py | Select-Object -First 1
if (-not $approver) { throw "HACK-011 absent: extract latest GitHub ZIP" }
$folder = Join-Path $HOME "Documents\TerraCouncil-Hack008-Sessions"
$session = Join-Path $folder "HACK008-20261028T010424-45b2d6b6.json"
$evidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
$draft = Join-Path $HOME "Downloads\TerraCouncil-HACK008-20261028T010424-45b2d6b6-oral-draft.json"
$approved = Join-Path $HOME "Documents\TerraCouncil-Hack008-Sessions\HACK011-approved-oral.json"
if (-not (Test-Path $session) -or -not (Test-Path $draft) -or -not (Test-Path $evidence)) { throw "Required source/draft file missing. Verify download file name." }
python -X utf8 $approver.FullName --session $session --evidence $evidence --draft $draft --out $approved --i-reviewed-meaning
if ($LASTEXITCODE -ne 0) { throw "Editorial approval failed; no audio requested" }
```

Expected: `EDITORIAL_REVIEW_APPROVED_NOT_SCIENTIFICALLY_VALIDATED`. The program validates technical format, exact source IDs and fingerprints; the user must validate **semantic fidelity**.

## Optional separately authorized ElevenLabs generation (potential billing)

Use only after approval. The TTS request sends the **reviewed** text to ElevenLabs. A paid call might complete even when its response is lost, so **never auto-retry**.

```powershell
$runner = Get-ChildItem . -Recurse -File -Filter render_session_audio.py | Select-Object -First 1
$out = Join-Path $HOME "Documents\TerraCouncil-Natural-Audio"
$env:TERRA_VOICE_SPARK = "onwK4e9ZLuTAKqWW03F9"
$env:TERRA_VOICE_WONDER = "EXAVITQu4vr4xnSDxMaL"
# First load ELEVENLABS_API_KEY securely into the same PowerShell process.
python -X utf8 $runner.FullName --session $session --evidence $evidence --out-dir $out --approved-manifest $approved --send-to-elevenlabs --i-reviewed-script --i-approve-cost-and-sharing
if ($LASTEXITCODE -ne 0) { throw "TTS failed; inspect history before retry" }
```

This step makes at most one potentially charged request and creates a new MP3 plus `.timing.json`. The player then verifies MP3 SHA-256 and session match before synchronized replay.

**Important:** this audio is a *short editorial discussion* of the scientific debate, not a literal reading or transcript of the original four machine responses. Nothing here claims that the narrator represents real people or public-sector stakeholders.

## Current status

HACK-011 source and tests committed to GitHub; not yet run end to end on the participant's Windows environment. Existing scientifically screened Boké inputs still are **NOT_FIELD_VALIDATED**. Human scientific review before any decision is required.
