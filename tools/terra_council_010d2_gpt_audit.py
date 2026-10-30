"""010D2 — audit GPT against the *same* FSDC claims used for Muse.

One explicit optional Meta Spark API call. Does not modify prior outputs.
Do not claim independence: Spark also audited Muse; a human must review both.
"""
import argparse,hashlib,json
from pathlib import Path
from terra_council_010d_pipeline import (source_info,validate_claims,verify_audit,
    AUDIT,call)

SCHEMA="TERRA_COUNCIL_010D2_GPT_AUDIT_V1"
def load(path):
 return json.loads(Path(path).read_text(encoding="utf-8-sig"))
def assemble(packets,extraction,gpt):
 source,sha=source_info(packets)
 if extraction.get("status")!="CLAIMS_HUMAN_REVIEW_REQUIRED" or extraction.get("source_sha256")!=sha:
  raise ValueError("Claim manifest invalid or stale")
 claims=validate_claims(extraction,source)
 if gpt.get("schema")!="TERRA_COUNCIL_010D_GPT_REFERENCE_V1" or gpt.get("role")!="esg":
  raise ValueError("Invalid GPT reference")
 if gpt.get("scientific_source_text")!=source:
  raise ValueError("GPT reference is not EXACTLY the same scientific source")
 spoken=gpt.get("spoken_text")
 if not isinstance(spoken,str) or not spoken.strip():raise ValueError("Empty GPT text")
 return {"source":source,"claims":claims,"spoken_text":spoken},sha
def main():
 p=argparse.ArgumentParser()
 for name in ("packets","claims","gpt","output"):p.add_argument("--"+name,required=True)
 p.add_argument("--model",default="muse-spark-1.3")
 p.add_argument("--effort",default="high",choices=("minimal","low","medium","high","xhigh","max"))
 p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 data,sha=assemble(load(a.packets),load(a.claims),load(a.gpt))
 output=Path(a.output)
 print(json.dumps({"status":"010D2_PREVIEW","target":"GPT-6 ESG reference",
  "source_sha256":sha,"claims":len(data["claims"]),"model":a.model,
  "potential_meta_calls":1,"actual_meta_calls":0,"audio_authorized":False}))
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit --authorize-meta required")
 if output.exists():raise SystemExit("Output already exists; no overwrite or automatic retry")
 output.parent.mkdir(parents=True,exist_ok=True)
 with output.open("x",encoding="utf-8") as f:
  json.dump({"schema":SCHEMA,"status":"CALL_IN_FLIGHT","source_sha256":sha},f)
 try:
  result,usage=call(a.model,a.effort,AUDIT,data,output)
  verify_audit(result,data["claims"])
 except Exception as exc:
  output.write_text(json.dumps({"schema":SCHEMA,"status":"STOP_NO_RETRY",
   "error_type":type(exc).__name__,"error":str(exc)[:400]}),encoding="utf-8")
  raise SystemExit("Stopped. Review raw response and journal; do not retry automatically")
 report={**result,"schema":SCHEMA,"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED",
  "subject":"GPT-6 ESG oral reference","source_sha256":sha,
  "model":a.model,"effort":a.effort,"usage":usage,
  "scientific_approval":False,"audio_authorized":False,"decision_authorized":False}
 output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"status":report["status"],"subject":report["subject"],
  "claims_checked":len(report["assessments"]),"audio_authorized":False}))
if __name__=="__main__":main()
