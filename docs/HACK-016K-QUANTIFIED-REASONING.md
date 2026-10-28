# HACK-016K — Quantified Scientific Reasoning & Decision Brief V3

The first real HACK-016 Boké session (HACK016-20261028T064321-062f7f3a) was used as the scientific reference. Its stored FSDC ESA WorldCover 2021 source provides five cover-share percentages. The new code extracts those percentages directly from source findings, not from model speculation or hardcoded Boké scores.

## Implemented

- src/dynamic_quantification.py: from a structurally verified session, extracts source-literal percentage labels and values, with source IDs, observation year, validation status, provenance hash, and explicit limitations. Percentages are not interpreted as trends or causal impacts.
- GET /api/dynamic-quantification?id=...: returns those metrics for a saved completed HACK-016 council, no Meta or ElevenLabs calls.
- Edge button **Indicateurs FSDC**: displays the actual source-derived values and coverage limitations.
- src/dynamic_brief.py: a new quantified evidence table before the proposed-investigation matrix and scientific debate. Separate **Dynamic-Brief-V3.pdf** file is produced without overwriting V1 or V2.
- tests/test_hack016k_quantified.py: simulated dynamic council with the five original percentage values (50.613, 2.262, 0.846, 0.528, 0.493), rejection of changed evidence, optional ReportLab PDF regression.

## What is and isn't quantified
The five ESA WorldCover percentage shares correspond to the screened, area-weighted **2021 rectangular area of interest**, not the entire Boké administrative area. They do not prove change in 2026, dust exposure, causal mining impact, agricultural profitability, or the condition of specific local communities. No additional quantitative metrics are invented. A future cross-sector FSDC connector must ingest actual additional sources and validate spatial and temporal representativeness.

## Windows no-cost validation
Extract latest GitHub ZIP into a new folder and open it in VS Code PowerShell.

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Server not found" }
$root=$server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p "test_hack016k_quantified.py" -v
if ($LASTEXITCODE -ne 0) { throw "HACK-016K regression failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

In Edge use **Historique dynamique** and open completed session HACK016-20261028T064321-062f7f3a. Click **Indicateurs FSDC**, then **Télécharger le brief dynamique**. The V3 report uses that saved session; no new scientific debate or billed API requests are needed.

## Status
Source files and mock tests committed; no user Windows execution or V3 PDF end-to-end inspection confirmed yet. Before claiming full decision quantification, real cross-sector FSDC numeric evidence, AOI coverage verification, source dates and independent scientific review are necessary.
