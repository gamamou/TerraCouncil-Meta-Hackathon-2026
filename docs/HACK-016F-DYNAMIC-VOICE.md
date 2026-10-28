# HACK-016F — Dynamic voice playback for new scientific councils

The current HACK-016F code provides variable-length ElevenLabs speech for a **completed HACK-016B dynamic debate**, without replaying the four fixed Boké speeches. The existing HACK-015 demo remains unchanged.

## Features implemented

- src/dynamic_voice_plan.py: source-specific voice plan for 3–6 verified Spark/Wonder interventions, preserving question, evidence hash, exact investigation and abstention, stage identity and editorial status. Rejects unexpected language, number rendering, speech symbols and length overflow.
- src/dynamic_voice_workflow.py: paid synthesis behind a **separate explicit consent** and server-only ElevenLabs API key. Writes an exclusive attempt journal **before** the external request. Never repeats an uncertain call. Saves MP3 and timing JSON plus SHA256.
- Local server routes: /api/dynamic-voice-status, /api/dynamic-voice-start, /api/dynamic-voice-audio, /api/dynamic-voice-timing.
- Edge dynamic session: a separate voice box with status, explicit data-sharing/cost opt-in, one-shot generation and authenticated playback. The display highlights the active speaking role from the timestamp manifest.
- tests/test_hack016f_voice.py: mock-only synthesis, source integrity, voice status and no-retry behaviors. Tests must be run on Windows before a paid request.

## Limitations

- A successful exact extraction from screened sources is *not* verified scientific accuracy, and the synthesized speech is a non-verbatim editorial reconstruction.
- The voice plan uses the already configured Spark and Wonder voice IDs; all Spark specialist roles currently share the Spark voice. Voice-per-agent personalization remains future work.
- The builder does not translate old English speeches or safely normalize digits. Such scripts are blocked for review, not silently transformed into French.
- No paid ElevenLabs call has been performed by the development process. Browser rendering and billing behavior still require validation on the user's local installation.
- At most one paid request per session; a timeout may already have been billed, so no automatic retry.
- The HACK-016B session must have completed and passed exact FSDC citation gates. No mining impact, exposure, field validation or regulatory permission is asserted.

## Windows validation without any billable API request

Download/extract the latest repository ZIP and open it in VS Code:

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "New server not found" }
$root=$server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p test_hack016f_voice.py -v
if ($LASTEXITCODE -ne 0) { throw "HACK-016F mock tests failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

In Edge, use **Historique dynamique**, open an already completed HACK-016B session, then **Voir le scénario oral dynamique** and **Contrôle automatique de fidélité**. In the new **Écoute vocale de cette délibération**, first check voice status. Do not authorize ElevenLabs if the spoken script is English, unreviewed, longer than the provider budget or contains unnormalized numerical material. If a session is eligible and the user accepts data sharing and the possible charge, the generation requires checking the box and clicking **Générer la voix une seule fois**. After checking the status becomes READY, click **Écouter le débat**. Playback verifies the MP3 SHA256 and source session before display.

To provide credentials in a local PowerShell terminal before launching the server: ELEVENLABS_API_KEY, TERRA_VOICE_SPARK and TERRA_VOICE_WONDER must be configured. Never disclose the key or save it in the public repository.

## Next milestone

Improve the semantic-language gate to verify French translation/paraphrase, allowing exception-only human review rather than repeated approvals. The current fast path is source-extractive French and is grounded in real Spark/Wonder session text. No model call or audio generation happens merely by opening a session.
