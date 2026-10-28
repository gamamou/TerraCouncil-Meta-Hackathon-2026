# HACK-015 — One-click approved dialogue, then synchronized playback

This milestone extends the **same localhost TerraCouncil FAITH app**; no Muse Code and no new Meta calls.

## What is now in GitHub

- `src/voice_workflow.py`: single-attempt ElevenLabs workflow. It reads **exactly one** existing approved French script for the completed HACK-008 session. It writes `attempt.json` **before** any paid request. A failure is not silently retried; account billing/history must be inspected.
- `src/local_council_server.py`: token-protected localhost routes `/api/voice-status`, `/api/voice-start`, `/api/voice-audio` and `/api/voice-timing`. Only the server sees the ElevenLabs API key. The audio request runs once in a worker, not upon page opening.
- `ui/hack008.html`: **Produire l'audio une seule fois**, **Actualiser l'état de l'audio**, **Écouter dans la Chambre**. The last action checks SHA-256 of the MP3, the source session ID and timed segments before synchronized playback.
- `tests/test_voice_workflow.py`: offline checks for session isolation and prevention of blind repeats.

The MP3 is a **human-approved editorial reconstruction** of real model interventions, **not** a verbatim recording. Scientific evidence remains SCREENED_NOT_FIELD_VALIDATED.

## Windows workflow

1. Stop old server with Ctrl+C; download latest GitHub ZIP and extract into a fresh folder.
2. Open VS Code terminal in the new extracted directory.
3. Load the ElevenLabs key locally and the previously used voices. Do not paste it in ChatGPT or into Edge:

```powershell
$secret = Read-Host "Cle ElevenLabs" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try { $env:ELEVENLABS_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
$env:TERRA_VOICE_SPARK = "onwK4e9ZLuTAKqWW03F9"
$env:TERRA_VOICE_WONDER = "EXAVITQu4vr4xnSDxMaL"
```

4. Launch with previously screened evidence:

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "HACK-015 source missing" }
$root=$server.Directory.Parent.FullName
if (-not (Test-Path (Join-Path $root "src\voice_workflow.py"))) { throw "Update GitHub ZIP" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_voice_workflow.py" -v
if ($LASTEXITCODE -ne 0) { throw "Voice safety tests failed" }
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

5. In Edge open http://127.0.0.1:8765 and click **Retrouver mes sessions → Ouvrir cette session** for the original completed HACK-008 run.
6. If you have not yet approved the spoken script, use **Atelier oral** to review all four texts against the scientific original and click **Approuver et enregistrer localement**. The approval is local and free.
7. Under **Génération vocale de cette session**, check availability. Only after checking data-sharing rights and accepting a potentially billed TTS request, tick the **separate ElevenLabs consent** and choose **Produire l'audio une seule fois**.
8. Click **Actualiser l'état de l'audio** rather than pressing generate again. If the state is `READY`, click **Écouter dans la Chambre**. The active scene follows the speaker timestamps. If an error appears, **do not re-run the generation** before checking the ElevenLabs account history and output files.

## Local saved output

`Documents/TerraCouncil-Hack008-Sessions/Audio-V15/<run_id>/` includes `attempt.json`, an MP3 and a `.timing.json` when the provider returns both successfully. Never publish them or API keys to the public repository.

## Limits / pending validation

- Actual paid generation from the user's environment has not been executed or confirmed.
- ElevenLabs voice availability, paid response shape and timings must be checked with the user's account. Some API errors may be charged.
- Only 2 analytic perspectives, 1 Wonder critique and 1 Spark revision are represented in this four-turn pilot, **not all FAITH stakeholders**.
- A rejected or failed attempt is deliberately not retried automatically. Investigate first.
- The local development server is not intended for public internet deployment.
