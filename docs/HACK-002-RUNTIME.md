# HACK-002 — Meta Model API orchestration (first implementation)

**No Muse Code.** Direct HTTPS calls to `https://api.meta.ai/v1/chat/completions` using standard-library Python. Models: `muse-spark-1.3` for perspective/revision and `muse-wonder-1.0` for independent critique. Model availability and permissions must be confirmed in your Meta account. API calls may incur charges.

## Implemented

- HACK-001 agent registry-based selection, capped at four proposer perspectives per question.
- Evidence gate checks mandatory provenance, sector, `ADMISSIBLE` status, unique evidence IDs and nonempty finding.
- Spark proposer positions → Wonder scientific critique → Spark revised synthesis.
- Default `--execute` **off**; absent evidence never triggers an API request.
- Runtime output marked `GENERATED_UNVERIFIED`, because prompt instructions alone cannot guarantee true provenance or correct citations.
- Seven isolated tests using synthetic fixtures and an injected fake API caller; these tests do not incur costs or establish scientific correctness.

## Quick start (Windows PowerShell)

Clone or download this repository. From the root of the repository:

```powershell
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 src/council.py --sector mining --question "What investigations should be prioritized in Boke?" --out council_plan.json
```

The second command produces `ABSTAIN_NO_ADMISSIBLE_EVIDENCE` by design (0 model calls). **Do not use artificial test fixtures as if they were verified Boké measurements.**

When authorized `ADMISSIBLE` FSDC records are available at a local path (without uploading private source data publicly), review them and run:

```powershell
$secret = Read-Host "Meta MODEL_API_KEY" -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try { $env:MODEL_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
python -X utf8 src/council.py --sector mining --question "What investigations should be prioritized in Boke?" --evidence "C:\PRIVATE\boke_evidence.json" --out "C:\PRIVATE\boke_council.json" --execute
```

`--execute` can make multiple **paid** model calls; never retry an incomplete run blindly. Keep raw evidence, traces, outputs and credentials outside the public repo. If you need to test connectivity first, run one small API request separately.

## Limitations and next tasks

HACK-002 is a first prototype. No FSDC data connector, live model response, UI, citation-verification engine, model-side tools or deployed service has been exercised here. Critic and synthesis texts are **not** mechanically provenance checked. HACK-003 will add claim extraction and evidence ID validation, plus stricter field-validation rules and auditable JSON traces. An abstention is an acceptable and scientifically necessary outcome.
