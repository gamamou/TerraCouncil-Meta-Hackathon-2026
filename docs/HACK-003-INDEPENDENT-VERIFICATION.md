# HACK-003 — Independent Scientific Verification

Date: 2026-10-27. **Hackathon code, prototype. No Muse Code.**

## Core principle

The agent cannot mark itself verified. A standard-library verification layer runs outside the Meta models at fixed control points. Muse Wonder's critique is *not* the independent verifier.

## Pipeline

1. Decision question + selected FAITH sector
2. Evidence Gate (deterministic) — presence of metadata, exact pilot geography, sector, allowed validation status, no duplicate IDs; creates canonical source fingerprint
3. Muse Spark analytical perspectives — strict JSON with observations referring to exact source findings, labeled hypotheses, investigative proposals and abstentions
4. Mandatory independent verification after **each** position: block on unknown citation, changed or invented finding, additional unchecked fields, malformed JSON or evidence tampering
5. Muse Wonder critique only if all positions pass the gate; same checks
6. Muse Spark revised synthesis only if critique passes; same checks
7. Human scientific review before release. Structural checks are *not scientific truth verification*.

## Scientific tiers and pilot limitations

- \`ADMISSIBLE\`: input status explicitly given by upstream evidence process; validator checks metadata only, **not** authenticity or scientific correctness.
- \`SCREENED_NOT_FIELD_VALIDATED\` and \`NOT_FIELD_VALIDATED\`: admitted only for **exploratory** observations and proposals; never upgrade their status.
- Other statuses: rejected; zero model calls if no usable evidence.
- Boké pilot retains overall \`NOT_FIELD_VALIDATED\` status. An exploratory dialogue is *not* an impact finding, causal estimate, verified mine footprint, permit approval or recommendation to proceed.
- \`finding\` must be copied verbatim from a source record to become an observation. All free-form hypotheses, proposals and abstentions are explicitly unverified, **not authoritative conclusions**.
- The verifier does not currently inspect source authenticity, geographic overlap beyond exact place labels, numeric/unit accuracy, satellite resolution, field validation, causal identification, full semantics of hypotheses, or underlying FSDC computations.

## Files

- \`src/verification.py\`: deterministic evidence/response checks.
- \`src/verified_council.py\`: Meta orchestration with non-optional verifier between every stage.
- \`tests/test_verification.py\`: 13 zero-cost tests using **synthetic fixtures only**.
- Previous \`src/council.py\` remains HACK-002 prototype; **use \`verified_council.py\` for HACK-003**.

## Local tests, PowerShell (at repository root)

\`\`\`powershell
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 src/verified_council.py --sector mining --question "Quelles investigations prioriser a Boke ?" --out (Join-Path $HOME "Documents\TerraCouncil-HACK003-plan.json")
\`\`\`

These commands **do not call Meta** and the expected output status with no evidence is \`ABSTAIN_NO_USABLE_EVIDENCE\` with 0 planned calls.

## Real local evidence (not for public GitHub)

Provide a private evidence JSON array. Each record requires:
\`evidence_id\`, \`dataset\`, \`source\`, \`observed_at\`, \`geography\` (exactly \`Boké, Guinea\` for pilot), \`method\`, \`license\`, \`validation_status\`, \`provenance\`, \`finding\`, \`sectors\` (include \`mining\`).

First inspect without API:
\`\`\`powershell
python -X utf8 src/verified_council.py --sector mining --question "Quelles investigations prioriser a Boke ?" --evidence "C:\PRIVATE\boke_evidence.json"
\`\`\`

After checking scientific provenance and data-sharing permissions, add \`--execute\` and provide \`MODEL_API_KEY\` locally in your terminal to enable **real potentially billable** Meta calls. Each prospective run can perform multiple model calls, and a blocked response halts subsequent calls. **Never retry blindly after an error.** No credentials or private source records should be committed to the public repository.

## Next scientific work

1. Ingest real authorized FSDC geospatial outputs with hashes, checksums, spatial footprints and independent field-aware QA.
2. Add per-claim numeric and causal evidence type checks, signed/annotated evidence manifests and source record versioning.
3. Add human-review workflow, separate release state and full immutable trace of each model call and verification outcome.
4. Validate actual Meta API behavior; adapt model response parsing to its responses without silently weakening gates.
5. Demonstrate a Boké dialogue from authentic FSDC evidence and disclose uncertainty transparently.

**Current state: code checked into GitHub, user-side/local full suite execution pending, real API/FSDC runs not yet claimed.**
