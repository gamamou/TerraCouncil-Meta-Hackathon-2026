# HACK-016J — Scientific Debate Quality and Dynamic Decision Intelligence

First real HACK-016 session used: HACK016-20261028T064321-062f7f3a.
The uploaded four-page report showed four Spark perspectives, one Wonder critique, and a final Spark synthesis. Its only cited FSDC observation was ESA WorldCover 2021. The arguments appropriately abstained from inferring 2026 land change, mining causality or population exposure, but they lacked an actionable comparative investigations matrix.

## Implemented
- src/dynamic_decision_matrix.py: construct a matrix of exact original proposed investigations, grouped by agent and tied to actual evidence IDs, with source validation status and agent abstentions. Costs, feasibility, comparative ranking and expected impacts are NOT_ASSESSED / NOT_AVAILABLE without data.
- src/dynamic_runtime.py: stronger role instructions for future sessions: proposer tests must be question-specific, Wonder must compare viewpoints and unresolved disagreements, and final Spark synthesis must prioritize prerequisite investigations rather than invent financial scores.
- GET /api/dynamic-decision-matrix?id=...: local token-protected access to the matrix from a completed session.
- Edge: a new **Matrice décisionnelle** button inside the dynamic narration/brief section shows documented investigations and Wonder concerns. No Meta calls needed for an existing session.
- src/dynamic_brief.py: new matrix section in decision brief, before full scientific debate transcript. Previous V1 is not overwritten. /api/dynamic-brief now generates the V2 file.
- tests/test_hack016j_matrix.py: simulated debate with distinct questions; all options reference existing FSDC source IDs; tampered data fails closed; PDF V2 is generated without silent overwrite.

## Scientific boundaries
The matrix is NOT a financing plan or an approved project investment decision. It lists proposals from models and emphasizes their missing empirical support. A source-verified reference is not a validated scientific conclusion. WorldCover 2021 on the analyzed rectangular AOI does not establish 2026 land-cover change or causal mining damage. Economics and finance hypotheses are flagged as unverified until actual financial/fiscal evidence is ingested.

## Windows zero-cost test
Stop the old server and open the newest extracted GitHub ZIP in VS Code PowerShell.

```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Latest TerraCouncil server absent" }
$root=$server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p test_hack016j_matrix.py -v
if ($LASTEXITCODE -ne 0) { throw "HACK-016J QA failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```

In Edge use Historique dynamique to reopen HACK016-20261028T064321-062f7f3a, click Matrice décisionnelle and Télécharger le brief dynamique. This generates the V2 PDF from the **existing saved real session** at zero new Meta or ElevenLabs calls. Existing V1 remains untouched. New debate prompts apply only to future sessions that are initiated with separate user approval.

This release is committed; end-to-end user-side QA is pending.
