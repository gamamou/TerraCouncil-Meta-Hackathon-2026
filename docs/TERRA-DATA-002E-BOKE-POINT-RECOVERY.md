# TERRA-DATA-002E — First actual Boké-labeled contextual record

Date of recovery into hackathon: 2026-10-28. Original producer: FAITH/FSMI pre-existing source `public/data/fsmi/guinea_34_nasa_power_2001_2025_v01.json`, generated 2026-10-20. No new external API data was requested.

## Recovered point

- Reference point labeled `Boke` in the existing 34-prefecture NASA POWER / MERRA-2 record, lon **-14.413188**, lat **11.068551**; not an administrative polygon average.
- 2025 modeled rainfall **1944.2 mm**, 2001–2020 baseline **1918.0 mm**, anomaly **+26.2 mm / +1.4%**.
- 2025 modeled air temperature **27.66 °C**, baseline **27.25 °C**, anomaly **+0.41 °C**.
- The original modeled point source response SHA256: `ac0be2a6eb4f7c8b395489201127470170a0a10cd1fe868dc29600d5a8198518`.
- Original internal recorded status: `COMPUTED_SCREENING_UNREVIEWED`.
- Historic response source URL, version and date recorded in `data/boke_nasa_power_context_candidate_002e.json`.

## Crucial mismatch

Previous TerraCouncil pilot AOI `[-14.5,10.5,-14.0,11.0]` EPSG:4326 **does not contain** the source reference point at latitude 11.068551. The saved point is labeled Boké prefecture by the producer but should not be asserted as an observation inside that exploratory rectangle or at a mine site. This is a real scientific/data-geography distinction that the original simple catalog matching did not capture.

## Added software

- `src/faith_boke_context_guard_002e.py`: validates preserved source point, rectangle, historic status, source response fingerprint; explicitly returns **zero** council observations and blocks scientific promotion pending location and licensing review.
- `tests/test_faith_boke_context_guard_002e.py`: tests original numerical values, outside-AOI classification, rejection of geographic mutation and evidence-status promotion.

Both are hackathon engineering additions; source computations precede the hackathon. Tests are committed but not yet run on participant Windows. No model calls, no API calls, no Base44 mutations and no reruns of source calculations.

### Windows verification (latest GitHub ZIP)
```powershell
$script = Get-ChildItem "$HOME\Downloads" -Recurse -File -Filter "faith_boke_context_guard_002e.py" | Select-Object -Last 1
if (-not $script) { throw "Actualiser le depot TerraCouncil depuis GitHub" }
$packageDir = $script.Directory.Parent.FullName
python -X utf8 -m unittest discover -s "$packageDir\tests" -p "test_faith_boke_context_guard_002e.py" -v
python -X utf8 $script.FullName
```

Next: select a canonical question geography (pilot rectangle vs named prefecture), acquire permitted static/source view with approved geographic semantics, and then admit a properly scoped *exploratory* evidence finding to the existing `HACK-016` verifier. No promotion merely because a source uses the name Boké.
