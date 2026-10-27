# HACK-001 — FAITH Knowledge & Multi-Stakeholder Agent Registry

**Started during the official October 27–November 4, 2026 build window.**

## Product boundary

TerraCouncil AI is the cross-sector decision council of SustainAfrica's FAITH ecosystem. It must route a question to relevant analytical perspectives across mining, agriculture, environment, energy, Simandou, critical minerals and digital twins. The first end-to-end pilot is Boké mining. Cross-sector connectors are *designed*, not claimed implemented.

## What is implemented in HACK-001

- Machine-readable agent and sector registry (`config/faith_agent_registry.json`).
- Minimal local loader/validator and sector-based agent selection (`src/registry.py`).
- No cloud models, prompts, external tools, FSDC data or validated field claims are implied.
- Standard-library tests (`tests/test_registry.py`).

## What is not yet implemented

Live Meta Spark/Wonder reasoning, knowledge retrieval from actual FSDC data, temporal and geographic evidence filters, debate/orchestration, PDF generation, audio integration, real stakeholder consultation and deployment. These require later hackathon milestones and must not be presented as functional now.

## Architectural rules

1. Perspectives are *simulations of analytical interests*, never actual named stakeholder representation or endorsement.
2. All evidence-backed numeric claims require versioned FSDC evidence with identifiers, licensing, geography, observation time, computation method and validation status.
3. Unavailable or inadmissible evidence results in abstention; Boké remains NOT_FIELD_VALIDATED.
4. Scientific critique must be independently performed and preserve objections.
5. Human decision-makers own approvals and operational decisions.
6. Muse Code is optional and **not used** in this development workflow. Future model runtime will use Meta Model API directly; specific model availability and permissions must be checked then.

## Local smoke tests

```powershell
$root = Get-Location
python -X utf8 -m unittest discover -s (Join-Path $root 'tests') -p 'test_*.py' -v
python -X utf8 (Join-Path $root 'src\registry.py')
```

These tests assert registry consistency, not scientific/model performance.

## Pilot

Question: *Which investigations and safeguards should be prioritized before deciding on a proposed industrial development in Boké?*

The answer must distinguish evidence-grounded statements, hypotheses, missing data and suggested investigations. No premature conclusions about impacts, permits or financing.
