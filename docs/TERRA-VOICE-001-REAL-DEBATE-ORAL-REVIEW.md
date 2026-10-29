# TERRA-VOICE-001 — Natural French oral review for actual HACK-016 session

Target real successful dynamic debate: `HACK016-20261029T001224-8479e1c5` (confirmed via user Edge screenshots, status `COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED`, 6 calls/steps). Scientific status remains *structural and citation verification only*; no Boké field validation and no source-specific mine dust PM measurement.

## What was built

- `src/terra_voice_editorial_001.py`: builds a bounded review worksheet from the original HACK-016 source-verified `dynamic_narration.build_dynamic_oral`. Creates six (or three-to-six generally) source-bound items that keep speaker, source model, original entire oral text, original evidence IDs, proposed **unchanged, complete extracted clauses only** where possible, and review flags for omitted arguments or difficult numerals and technical tokens. It never invents numbers, rewrites the scientific record or claims semantic equivalence.
- `src/local_council_server.py`: authenticated local read-only endpoint `/api/dynamic-oral-worksheet?id=<verified session>`. Restricts session IDs and file size; verifies source trace integrity through existing oral builder.
- `ui/hack008.html`: optional **Version orale courte** button in the current, simplified product UI. User sees a reviewable text area, caution flags and expandable source-original text for each intervention. The text stays local, never saved as an approved script and never sent to Meta/ElevenLabs by this new feature.
- `tests/test_terra_voice_001_editorial_worksheet.py`: tests verified source association, no mid-clause truncation, no silent TTS authorization, and UI endpoint matching; published, pending Windows execution.

## Remaining blocking issue

The existing provider adapter `dynamic_voice_plan.prepare_voice` permits **exact source-extractive** scripts only, using `dynamic_oral_audit.verify_oral`, `scientific_pronunciation.spoken_storyboard`, and a strict 2000-character single-call limit. An edited/abridged scientific script is NOT automatically eligible for ElevenLabs; human semantic review and a new explicit approval gate must be implemented and tested before authorized TTS. This milestone is an honest *intermediate editorial preparation* and not a completed audible debate. Do not bypass the source fidelity gate.

The user's local server also reported `clé vocale absente`. A future new PowerShell process will need `ELEVENLABS_API_KEY`, `TERRA_VOICE_SPARK`, and `TERRA_VOICE_WONDER` configured privately. Never put keys into project files or GitHub.

## Windows consolidated check after downloading latest GitHub

```powershell
$module=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $module) { throw "Module absent du ZIP actuel" }
$root=$module.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$root\tests" -p test_terra_voice_001_editorial_worksheet.py -v
```

Restart existing server with the previously verified private `--hi/--qa` paths; in Edge open the saved successful dynamic session, then click **Version orale courte**, and compare the proposed short phrases with the original before considering audio approval. Avoid a new billed Meta debate. Do not reproduce the source-full session or API credentials in GitHub.

**Next implementation priority:** approved, source-linked, human-reviewed six-turn script gate with an audited voice payload, while maintaining the existing one-attempt no-blind-retry and paid-consent protections.
