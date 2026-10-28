# HACK-010 — Executive PDF + Natural French Audio

Created during the Meta Hackathon. This is an incremental implementation in the same TerraCouncil local server, **without Muse Code**.

## Executive brief — what changed

- Replaces the former 4-page technical log with an editorial French committee document: executive synthesis, preliminary orientation, evidence, prioritized investigations, challenges raised by Wonder, deferred decisions, science caveats.
- A technical annex retains the original Meta statements and FSDC evidence IDs for audit; **the source JSON remains unmodified**.
- A new file `src/elegant_decision_pdf.py` is used by the local `/api/pdf` endpoint.
- An `-Executive-Brief-v2.pdf` filename avoids accidentally serving a previously cached technical PDF.
- The report is editorial decision support, **not a field validation, formal committee decision, or regulatory authorization**.
- Depends on `reportlab`. No Meta or ElevenLabs call for PDF.

## Natural French oral track

- `src/natural_french_dialogue.py` builds a short 4-turn editorial reconstruction based on the **same independently verified HACK-008 session**.
- The script uses spoken French phrases rather than raw model JSON, hashes, percentages, URL strings, IDs, English technical terms or code-like characters.
- It will **reject** reuse for a session lacking the documented WorldPop and WorldCover source contexts and relevant themes.
- The label is `EDITORIAL_RECONSTRUCTION_NOT_VERBATIM`. **Human review required** before any voiced delivery.
- The interface now offers **Télécharger le scénario oral français**, at zero external cost.
- `src/render_session_audio.py` can optionally produce expressive ElevenLabs v4 multi-speaker French audio from the reviewed script, using the documented `/v1/text-to-dialogue/with-timestamps` endpoint and 2 voice IDs; at most one audio request, no retries, requires `--send-to-elevenlabs --i-reviewed-script --i-approve-cost-and-sharing`, local `ELEVENLABS_API_KEY` plus voice IDs.
- Requires total speech text no more than 2,000 characters in one request, per current ElevenLabs documentation. Audio narration is never a verbatim Meta transcript.
- Generation writes a session-named MP3 and matching `.timing.json` containing speaker segments and audio SHA-256.
- The new session audio player requires the MP3 and JSON to match the **currently opened session**, then highlights the active speaker during playback. Older, pre-hackathon ElevenLabs files remain separate archives.

## Test the upgraded PDF and oral preview **without new API calls**

1. Stop the existing localhost server using Ctrl+C in VS Code PowerShell.
2. Download/extract the latest ZIP from the public TerraCouncil GitHub repo and open the new folder in VS Code.
3. Install `reportlab` if not already installed.
4. Start the updated server on the same localhost port:

```powershell
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
python -m pip install reportlab
if ($LASTEXITCODE -ne 0) { throw "ReportLab installation failed" }
$server = Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Latest server not found" }
$root = $server.Directory.Parent.FullName
if (-not (Test-Path (Join-Path $root "src\elegant_decision_pdf.py"))) { throw "HACK-010 files missing" }
$evidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

Then open http://127.0.0.1:8765 in Edge, use **Retrouver mes sessions** and reopen the existing completed HACK-008 session. Click **Télécharger la note décisionnelle PDF** and **Télécharger le scénario oral français**. No new Meta API calls or ElevenLabs TTS calls. Verify scientific integrity and French readability.

## Optional future TTS for the currently saved session

Do not perform this step until the French preview has been read and approved. The normal default command makes only review files, without a network call.

```powershell
$runner = Get-ChildItem . -Recurse -File -Filter render_session_audio.py | Select-Object -First 1
$base = Join-Path $HOME "Documents\TerraCouncil-Hack008-Sessions"
$last = Get-ChildItem $base -Filter "HACK008-*.json" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$inputEvidence = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
$audioDir = Join-Path $HOME "Documents\TerraCouncil-Natural-Audio"
python -X utf8 $runner.FullName --session $last.FullName --evidence $inputEvidence --out-dir $audioDir
```

After carefully reviewing the resulting TXT and the source trace, and only if the user explicitly authorizes **new potentially billed** ElevenLabs generation, they may use their secure `ELEVENLABS_API_KEY` and existing `TERRA_VOICE_SPARK` and `TERRA_VOICE_WONDER` IDs and run with `--send-to-elevenlabs --i-reviewed-script --i-approve-cost-and-sharing`. Do not blindly rerun a failed generation: the request may have been charged. The script stores reviewed content as a deterministic storyboard; if the user wants text edits before generation, make those changes in the source/storyboard and repeat preview and review first. Editing the preview TXT alone does not change the transmitted script.

The output MP3 and `.timing.json` can be loaded into the same session in the Edge Chamber. The source trace has exact model responses; the audio is explicitly labeled editorial, not original quotations.

## Quality assurance

Run Python tests in the latest extracted folder:

```powershell
$root = $server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_*.py" -v
```

Relevant tests: `test_hack010.py`, `test_render_session_audio.py`. They use synthetic fixtures and mocked audio, with no external API calls.

**Current status:** GitHub source committed, Windows execution and PDF visual review pending. Real ElevenLabs v4 generation for HACK-008 has not been executed.
