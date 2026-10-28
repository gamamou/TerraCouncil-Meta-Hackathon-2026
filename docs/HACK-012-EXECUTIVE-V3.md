# HACK-012 — Executive PDF V3: visible-design and cache correction

**Issue verified**: The PDF sent on October 28 remained the previous five-page committee note with dense technical annex and near-identical design. HACK-011 changed the audio review process, not the visual PDF layout. The previous endpoint also saved a PDF under a persistent V2 path and reused it if it already existed; the browser downloaded all versions as `TerraCouncil-Decision-Brief.pdf`.

## Implemented

- New `src/executive_brief_v3.py`: visually distinct PDF with full navy cover, clear decision message, prominent summary, five-priority investigation matrix, policy limits and source/review appendix. Editorial conclusions are qualified; no false endorsement.
- Source evidence values and remarks come from the same independently verified HACK-008 records; the original session JSON remains unchanged.
- Local server now generates `HACK008-<ID>-Executive-Brief-V3.pdf`, not the V2 cached file, and responds with downloadable `TerraCouncil-Executive-Brief-V3.pdf` and HTTP header `X-Terra-Pdf-Version`.
- Button says **Télécharger le rapport exécutif V3 (PDF)**.
- `tests/test_executive_brief_v3.py` provides PDF generation smoke checks with synthetic data.
- No Meta or ElevenLabs calls needed.

## Use in Windows VS Code

1. Stop the old server using **Ctrl+C**.
2. Download latest ZIP of `gamamou/TerraCouncil-Meta-Hackathon-2026`, extract, open newest folder.
3. Start the latest server from that folder and use the existing FSDC evidence:

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter "local_council_server.py" | Select-Object -First 1
if (-not $server) { throw "Server missing" }
$root=$server.Directory.Parent.FullName
if (-not (Test-Path (Join-Path $root "src\executive_brief_v3.py"))) { throw "HACK-012 not extracted" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

4. In Edge open `http://127.0.0.1:8765`, choose a saved finished HACK-008 session, click **Télécharger le rapport exécutif V3 (PDF)**.
5. Confirm PDF page one is a **full navy-blue cover** with title **INTELLIGENCE DÉCISIONNELLE**. If it isn't, you are still using the previous server or opened an older download.

## Optional smoke test

```powershell
$testdir=Join-Path $root "tests"
python -X utf8 -m unittest discover -s $testdir -p "test_executive_brief_v3.py" -v
```

No new scientific conclusions or model responses were generated. The project continues to mark the Boké data **SCREENED_NOT_FIELD_VALIDATED** and requires human review.
