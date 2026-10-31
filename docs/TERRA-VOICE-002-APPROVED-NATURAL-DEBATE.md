# TERRA-VOICE-002 — Approved Natural Debate: security and fidelity gate

**Status:** core approval module + offline unit tests committed on a feature branch. **Not deployed or audio-enabled.**

**Target:** existing six-turn Boké session `HACK016-20261029T001224-8479e1c5`. Do not rerun Meta calls. Never commit the private session transcript, data payloads, audio, provider keys, or user approval artifacts.

## What the module does

1. `prepare_review(trace)` reconstructs the same verified TERRA-VOICE-001 worksheet and derives immutable source markers, evidence IDs, stage order and original-text hashes.
2. An identified human editor compares **each** proposed spoken intervention with the entire underlying scientific text; personally confirms semantics and pronunciation. Editing may reorder words or shorten arguments, but this is **not** a scientific validation.
3. `approve(trace, submitted, reviewer)` fails closed unless each of the six turns is individually checked, the source identity remains intact, language/character constraints pass, and the aggregate text is within the current 2000-character TTS budget. It produces a SHA-256-bound approval record.
4. `voice_payload(trace, approval, spark_voice, wonder_voice)` re-verifies source markers and approval checksum, and returns a voice-preparation plan with the existing six-turn order and distinct voices. **No provider calls or financial consent are made by these functions.**

## Integration gate still required (TERRA-VOICE-002B)

The application must implement a *server-side*, authenticated review persistence workflow and a one-attempt TTS dispatch pathway. The dispatch must freshly validate the recorded approval against the exact source session, require separate explicit sharing and possible billing consents, check the configured ElevenLabs key and distinct voice IDs, enforce existing one-attempt/no-blind-retry behavior, and save the output privately. Never accept a client-supplied `may_be_sent` flag or allow the review approval to count as consent. The old exact-extraction adapter must not be silently bypassed. Do not attach this module to the existing paid endpoint until these constraints are implemented and tested. Display status as **awaiting authorized TTS**, not “audio produced”.

Source integrity is structural and provenance-limited: **NOT_FIELD_VALIDATED**.

## Offline tests (Windows PowerShell, in cloned repo)

```powershell
$test = Get-ChildItem . -Recurse -File -Filter test_terra_voice_002_approval.py | Select-Object -First 1
if (-not $test) { throw "TERRA-VOICE-002 tests not found" }
$root = $test.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p test_terra_voice_002_approval.py -v
```

No paid service is needed for these tests. Do not place `ELEVENLABS_API_KEY` in repository files.
