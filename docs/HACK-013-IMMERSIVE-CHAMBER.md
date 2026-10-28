# HACK-013 — First Immersive Scientific Deliberation Chamber

**Code status:** the source-level visual chamber, evidence-cue API, offline script preparation and tests have been committed. Real Edge playback of a *new* session-specific MP3 is **not yet validated**. No new Meta or ElevenLabs request was performed during this milestone.

## What changed

- Four cinematic presentation scenes linked to the four **already completed** real Meta model steps in HACK-008. Navigate by clicking scene buttons even without audio.
- Each scene is sourced from the verified scientific trace, with role, planned investigation, FSDC source IDs and abstention.
- WorldPop estimated rectangular-area raster cell sum and WorldCover 2021 cover shares appear as **preliminary source values only**, not mine-exposure or causal-impact findings.
- `src/chamber_visuals.py` builds scene metadata and refuses source-tampered or incomplete traces using the same independent verifier.
- `GET /api/chamber?id=<saved-session>` serves those cues from the local server with the existing session token; no networked AI requests.
- The existing session-matched MP3 and `.timing.json` listener follows ElevenLabs timestamps: highlights the current speaker and selects the matching visual scene. Audio is *editorial reconstruction*, not verbatim model speech.
- `src/prepare_chamber.py` prepares the validated natural-language script and scene metadata **offline** for one specified session. No automatic TTS generation.
- The existing HACK-011 approval and integrity checks remain mandatory before any paid ElevenLabs audio.

## Windows: validate visuals with the existing session — zero API calls

Stop the old VS Code server with Ctrl+C, download/extract latest GitHub ZIP, open its new folder in VS Code, and run:

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "HACK-013 server absent: refresh GitHub ZIP" }
$root=$server.Directory.Parent.FullName
if (-not (Test-Path (Join-Path $root "src\chamber_visuals.py"))) { throw "HACK-013 source missing" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

Open http://127.0.0.1:8765 in Edge. Click **Retrouver mes sessions** and open the completed HACK-008 session. In **Chambre de délibération**, click the 4 scene tabs. Expect the population and cover figures as source-grounded values, source IDs, relevant investigations and abstentions. Do not launch another model debate for this test.

## Offline preparation of a natural French dialogue

Use a second PowerShell terminal while the server runs (no need to stop it):

```powershell
$preparer=Get-ChildItem . -Recurse -File -Filter prepare_chamber.py | Select-Object -First 1
$sessions=Join-Path $HOME "Documents\TerraCouncil-Hack008-Sessions"
$session=Get-ChildItem $sessions -File -Filter "HACK008-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $session) { throw "Saved HACK-008 session not found" }
$out=Join-Path $HOME "Documents\TerraCouncil-Hack013-Chamber"
python -X utf8 "$($preparer.FullName)" --session "$($session.FullName)" --evidence "$evidence" --out "$out"
if ($LASTEXITCODE -ne 0) { throw "Offline chamber preparation failed" }
```

Expected: `STATUS: REVIEW_READY`, `META_CALLS: 0`, `TTS_CALLS: 0`, plus the exact JSON/TXT paths.

Read the new French oral text and compare the summary of each speaker with the actual scientific intervention. Do **not** submit unreviewed editorial text as though it were a literal scientific quote.

## Optional audio generation: separate authorization

Only after deliberate review and approval of the specific four-turn script:

1. Approve the editable draft with `src/approve_oral_script.py --i-reviewed-meaning` and a new output JSON.
2. Load your existing ElevenLabs key **only locally** into the same PowerShell session. Voice IDs may be `TERRA_VOICE_SPARK=onwK4e9ZLuTAKqWW03F9` and `TERRA_VOICE_WONDER=EXAVITQu4vr4xnSDxMaL`, subject to current account availability.
3. Run `src/render_session_audio.py --approved-manifest <approved-json> --send-to-elevenlabs --i-reviewed-script --i-approve-cost-and-sharing`, passing `--session`, `--evidence` and `--out-dir`. A single request can be billed even on network failure: don't blindly retry.
4. The resulting MP3 and timing JSON must be selected in the two file controls in the Edge Chamber. The browser verifies session ID, file name, and MP3 SHA256 and uses real voice-segment timestamps.

The ElevenLabs text-to-dialogue-with-timestamps endpoint is documented at https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert-with-timestamps. For reliable generation keep total source dialogue within 2,000 characters.

## Limits and provenance

No field validation. No causal mining impact assessment. No verified real stakeholder endorsement. The audiovisual scene sequence is an interpretation of screened source data and verified model steps, and the oral script is a separate reviewed editorial reconstruction. The demo cannot be published as a regulatory environmental review or definitive investment decision.
