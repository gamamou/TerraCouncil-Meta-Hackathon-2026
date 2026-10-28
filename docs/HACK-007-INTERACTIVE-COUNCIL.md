# HACK-007 — Interactive Scientific Council (offline validated replay)

Hackathon contribution created after the first real Boké Meta Spark → Muse Wonder → Spark cycle. **No Muse Code.** This UI is a new integration of pre-existing FAITH/FSDC screening and the real hackathon-era Meta model traces. It does not claim to generate new model responses.

## Implementation

- `src/build_council_ui.py`: standalone HTML generator; no external dependencies, no network, no API keys.
- `tests/test_build_council_ui.py`: synthetic zero-call tests for three-stage replay, independent re-verification, evidence integrity and basic HTML script escaping.
- Dashboard: single scientific question, three navigable stages, exact screened FSDC observations with IDs, preliminary hypotheses, proposed investigations, abstentions and provenance.
- A new-question textbox is intentionally **not a live chat**. It tells the user that a new evidence-gated model session is required. No fake responses.
- No sound synthesized; earlier ElevenLabs audio is pre-hackathon and NOT part of this new demo.

## How to build with the participant's real traces

Download/extract latest public repository. In VS Code PowerShell, from the extracted folder:

```powershell
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$builder = Get-ChildItem . -Recurse -File -Filter 'build_council_ui.py' | Select-Object -First 1
if (-not $builder) { throw 'HACK-007 absent: redownload latest GitHub ZIP' }
$inputs = Join-Path $HOME 'Documents\TerraCouncil-Scientific-Inputs'
$ev = Join-Path $inputs 'boke_screened_evidence.json'
$spark = Get-ChildItem $inputs -File -Filter 'HACK005-Spark-live-*.json' |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
$wonder = Get-ChildItem $inputs -File -Filter 'HACK006-Wonder-live-*.json' |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
$revision = Get-ChildItem $inputs -File -Filter 'HACK006-Revision-live-*.json' |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not (Test-Path $ev) -or -not $spark -or -not $wonder -or -not $revision) {
    throw 'Evidence or one of the three real Meta traces is missing'
}
$out = Join-Path $inputs ('TerraCouncil-HACK007-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.html')
python -X utf8 "$($builder.FullName)" --evidence "$ev" --spark-trace "$($spark.FullName)" --wonder-trace "$($wonder.FullName)" --revision-trace "$($revision.FullName)" --out "$out"
if ($LASTEXITCODE -ne 0) { throw 'HACK-007 HTML build failed' }
Start-Process "$out"
```

Expected: `STATUS: OFFLINE_COUNCIL_READY`, `STAGES: 3`, `EVIDENCE: 2`, `META_CALLS: 0`.

The HTML is a standalone artifact with embedded derived evidence findings and checked model texts. Do not publish it or the three trace JSONs without first reviewing data-sharing rights and content. Open locally in Edge.

## Important limitations

- The study area is a rectangle in Boké, not all of Boké administrative region.
- WorldPop 2026 raster population sum is NOT a census, mine exposure or affected people.
- ESA WorldCover 2021 classes are NOT a 2026 change, ecological survey, or proof of mining causation.
- The independent verification gate enforces exact matching to supplied findings; it cannot verify scientific truth, causal validity, agent completeness or human approval.
- Three live model messages represent one analytical perspective, one critique and one revision, **not a completed council of eight distinct live stakeholder agents**.
- No new-question backend or fresh deliberation inside the HTML; planned next.
- Human scientific review is mandatory before use as a decision recommendation.

## Quality checks

```powershell
$root = $builder.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root 'tests') -p 'test_*.py' -v
```

Tests do not call Meta. Existing HACK-001–006 tests should remain green.
