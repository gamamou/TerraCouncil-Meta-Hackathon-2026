# HACK-004 — First genuine Boké screened-data bridge

Created during hackathon on October 27, 2026. **No Muse Code.**

## Grounded source inputs (pre-existing, not hackathon-created scientific work)

The input records `010HI_evidence.json` and `010HJ_spatial_qa.json` originate from SustainAfrica/TerraCouncil's earlier multidomain geospatial experiment and must be kept out of the public GitHub repository unless publication rights and privacy are reviewed.

The adapter `src/import_boke_010hi.py` is new hackathon integration code. It reads those locally supplied JSON records, cross-checks their known schemas, AOI (EPSG:4326 bounding box -14.5, 10.5, -14.0, 11.0), WorldPop/WorldCover/CHIRPS source hashes and scientific status, then exports two source-derived finding records:

- WorldPop 2026 raster-cell sum within the rectangular AOI; **not** a census, mining exposure estimate, or count of affected people.
- ESA WorldCover 2021 area-weighted shares for selected land-cover classes; **not** a biodiversity survey, land-cover change trend, or evidence of mining causality.

The adapter requires `READY_FOR_EXPLORATORY_COUNCIL` in the QA record, no QA errors, and preserves `SCREENED_NOT_FIELD_VALIDATED` for every exported record. It does not produce mining footprint or damage claims.

## Run locally from extracted latest GitHub repo

Find `src/import_boke_010hi.py` under your GitHub extraction and supply the existing `010HI_evidence.json` and `010HJ_spatial_qa.json` files outside the repository. Example:

```powershell
$builder = Get-ChildItem . -Recurse -File -Filter import_boke_010hi.py | Select-Object -First 1
$root = $builder.Directory.Parent.FullName
$inputs = "$HOME\Documents\TerraCouncil-Scientific-Inputs"
$evidence = Join-Path $inputs "boke_screened_evidence.json"
python -X utf8 "$($builder.FullName)" --hi (Join-Path $inputs "010HI_evidence.json") --qa (Join-Path $inputs "010HJ_spatial_qa.json") --out "$evidence"
if ($LASTEXITCODE -ne 0) { throw "FSDC screened data import failed" }
$verified = Join-Path $root "src\verified_council.py"
python -X utf8 "$verified" --sector mining --question "Quelles investigations scientifiques prioriser a Boke ?" --evidence "$evidence" --out (Join-Path $inputs "boke_exploratory_plan.json")
```

**Do not add --execute initially.** The plan may show `EVIDENCE_READY_EXPLORATORY` and >0 *planned* calls but **no calls will have been made**. Review privacy, licensing, permitted model transmission and claims before running `--execute`; it can be billed and sends finding text to Meta.

## Hard limit: model outputs are not yet scientifically verified

HACK-003 ensures strict known evidence IDs and verbatim source findings, but it does **not** independently verify the scientific truth of the original source, causal interpretations in free-form hypotheses, quantified computations, source permissions or model behavior. The developer may not treat a structural PASS as scientific sign-off.

## QA

`tests/test_import_boke_010hi.py` checks no status upgrades, AOI integrity, hash agreement, census qualifiers, unsupported claims. Synthetic **test fixtures** are not the real scientific inputs.

Next: real live Meta pilot, input permission review, model-format response tuning, machine-verifiable trace storage and human sign-off.
