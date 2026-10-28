# TerraCouncil — Development history and reproducible contribution ledger

> Audit page for the **Meta Global AI Developer Hackathon 2026 jury**.
> This is a curated index of real commit evidence, not a rewritten Git history.
> The hackathon period recorded in the original repository README is **27 October–4 November 2026**.
> Existing assets before that period are acknowledged as pre-existing, irrespective of when imported into the competition repository.

## A. Pre-existing SustainAfrica FAITH/FSDC scientific foundation (not hackathon creation)
- FAITH Mining CPDM historical cadastre / snapshot `20260716_232803_UTC`; reference 22,430 cadastral rows; 1,012 rows with historical observed-footprint flag (FSMI view: 1,010 distinct shape UIDs). **Flags are not proof of a legal permit/site match**.
  Canonical source: https://github.com/SustainAfrica/faith-mining-data-core/issues/439
- MAUS v2: PANGAEA reference, source `global_mining_polygons_v2.gpkg`, documented Guinea subset 128 features. Local loader created **0 permit-footprint links**, so do not represent the national flags as 1,012 verified Maus intersects. Canonical method:
  https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/operations/local-maus-reference-load.md
- Cheng functional classes: MIN-085 ontology / MIN-087 model-feature reference; **no confirmed executed Guinea classification rasters**, and dataset commercial rights not admitted. Canonical:
  https://github.com/SustainAfrica/faith-mining-data-core/blob/main/docs/mining/min085/functional-land-use-source-ontology-v0.1.md
- Historic TerraCouncil scientific screening results WorldCover 2021, WorldPop 2026 and CHIRPS source reference, plus prototype multilingual audio and Meta feasibility work. Reuse is disclosed; dates of computations are not reset to hackathon date.

## B. Contributions committed during hackathon
| Phase / contribution | Auditable evidence | Status meaning |
| --- | --- | --- |
| HACK-001–HACK-003 | README, `src/registry.py`, `src/verification.py` | Agent registry and structural evidence gating |
| HACK-004–HACK-015 | `docs/HACK-004-REAL-BOKE-DATA.md` through HACK-015, associated code | Live council and user-facing interface evolved incrementally; consult dated source traces for which live stages were actually run |
| HACK-016 | `src/dynamic_council.py`, later HACK-016 submilestones in ROADMAP | Dynamic question and evidence selection; scientific trust remains bounded by source QA |
| FSDC-RECOVERY-001 | `src/fsdc_local_recovery.py`, historical scans | Read-only local discovery; early filenames-only strategy suffered false positives e.g. ROADMAP.md; it is retained as history, not erased |
| TERRA-DATA-GATEWAY-001 | `config/terra_data_gateway_001.json`, `src/terra_data_gateway.py` | Initial API request adapters for NASA POWER, OpenAQ station discovery and STAC collection discovery; **source committed, no live service/QA evidence yet** |
| TERRA-DATA-001 | `src/faith_asset_recovery_001.py`, `tests/test_faith_asset_recovery_001.py` | Precision read-only recovery, ZIP member discovery, duplicate SHA grouping, published tests; **local Windows verification and data re-admission pending** |

## C. New public data acquisitions are hackathon contribution
Separate three dates and their evidence:
1. **Dataset observation/reference date** — what the measurement represents.
2. **Actual API retrieval date** — captured UTC by adapter, only after a real request.
3. **Git commit / Council integration date** — when code, schema or admissible result was recorded.

A cited original FAITH result remains pre-existing even if recovered during the hackathon; newly written recovery, validation and integration code are hackathon contributions. No acquired data may be relabelled as a successful API call without preserved response SHA, URL, retrieval time and reproducible processing.

## D. Continuity and quality
- Preserve HACK and scientific milestone names; use TERRA-DATA-001 through -005 as a **coherent workstream**, not rebranding of HACK-016 or FAITH work.
- New features do not replace verified older modules; expand source coverage before extra visualization.
- No scientifically validated measurement without AOI geometry, CRS, units, temporal comparability, license, checksum and transparent failure/abstention.
- Never commit model/API keys or restricted licensed data. Private Google Drive is staging; public GitHub contains schemas, small synthetic tests and provenance pointers only.
- **Tests committed** does not mean **tests executed**. Add dated invocation output to a later acceptance record.
- No paid Meta/ElevenLabs calls in recovery or API-metadata code without explicit consent.

## E. Evaluation proof still required
- Local Windows tests for the new targeted scanner + gateway.
- Actual FAITH dataset path recovery and hashes, with source content and geometry QA.
- A successful API acquisition from at least one new public provider with raw response + SHA (private) and sanitized status record (public).
- First enriched, genuinely source-driven Spark/Wonder debate compared to baseline, with explicit human review.
