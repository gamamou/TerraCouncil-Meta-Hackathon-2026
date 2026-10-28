# HACK-006 — Sequential Meta debate

`src/continue_debate.py` continues a locally saved, structurally verified Spark pilot in two **separate** controlled steps. Each step uses Meta Model API directly, without Muse Code.

1. `--stage critique` reviews Spark with `muse-wonder-1.0`. Independent checks follow the model output.
2. `--stage revision` revises Spark with `muse-spark-1.3`. It requires a verified Wonder trace.

Both stages default to **dry run**, zero calls. Real execution requires `--send-to-meta --i-reviewed-sharing` plus a locally held `MODEL_API_KEY`. Each real step performs at most one potentially billed call. Use unique output filenames; never blindly repeat a failed call.

The original Spark trace and preliminary Boké evidence must stay in local private Documents. Fingerprints and the checked publication are validated before use. All scientific assertions remain preliminary; structural gates are not field validation.

Example dry run from the latest extracted repo:

```powershell
$runner = Get-ChildItem . -Recurse -File -Filter continue_debate.py | Select-Object -First 1
if (-not $runner) { throw "Update GitHub ZIP" }
$dir = Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs"
$ev = Join-Path $dir "boke_screened_evidence.json"
$spark = Get-ChildItem $dir -File -Filter "HACK005-Spark-live-*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $spark) { throw "Spark trace missing" }
$out = Join-Path $dir ("HACK006-Wonder-dry-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".json")
python -X utf8 $runner.FullName --stage critique --evidence $ev --spark-trace $spark.FullName --out $out
```

Expected: `STATUS: READY_NO_MODEL_CALL`, `CALLS_ATTEMPTED: 0`. After reviewing data sharing/billing and entering the Meta key, a separate real run with a **new** output name may use `--send-to-meta --i-reviewed-sharing`. Only if the critique passes may the revision stage be attempted, again as a separate opt-in call.

**Status:** implementation committed, runtime tests and first Wonder call not yet performed.
