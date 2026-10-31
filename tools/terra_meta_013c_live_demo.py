"""013C live demo: screened Boké evidence, opt-in Meta calls, per-call audit.
Never retry an uncertain call or overwrite an existing run.
"""
import argparse,datetime,hashlib,json,os
from pathlib import Path
from verification import gate_evidence
from council import meta_call
from terra_meta_013c_adaptive_council import run

def canon(obj):
 return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--evidence",required=True)
 p.add_argument("--question",required=True)
 p.add_argument("--sector",default="mining")
 p.add_argument("--geography",default="Boké, Guinea")
 p.add_argument("--execute",action="store_true")
 p.add_argument("--output")
 args=p.parse_args()
 records=json.loads(Path(args.evidence).read_text(encoding="utf-8-sig"))
 if not isinstance(records,list):raise SystemExit("Evidence must be a JSON list")
 gate=gate_evidence(records,args.sector,args.geography)
 details={"question":args.question,"evidence_ids":[r["evidence_id"] for r in gate["evidence"]],
   "evidence_sha256":gate["evidence_sha256"],"gate_status":gate["status"],
   "rejected_count":len(gate["rejected"])}
 if not args.execute:
  print(json.dumps({"status":"PREVIEW_NO_META_CALLS",**details,
      "maximum_model_calls":10,"note":"Up to 8 Spark + 2 Wonder; neither number is mandatory"},
      ensure_ascii=False,indent=2))
  return
 if not gate["evidence"]:raise SystemExit("No screened evidence; no model calls")
 if not args.output:raise SystemExit("--output required for --execute")
 key=os.environ.get("MODEL_API_KEY")
 if not key:raise SystemExit("MODEL_API_KEY is missing in this terminal")
 target=Path(args.output)
 target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("x",encoding="utf-8") as f:
  json.dump({"status":"IN_PROGRESS_DO_NOT_REPEAT","details":details,"calls":[]},f,ensure_ascii=False,indent=2)
 ledger={"status":"IN_PROGRESS_DO_NOT_REPEAT","details":details,"calls":[]}
 def save():
  target.write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding="utf-8")
 def audited_caller(model,instructions,payload,secret):
  num=len(ledger["calls"])+1
  item={"sequence":num,"model":model,"payload_sha256":hashlib.sha256(canon(payload).encode()).hexdigest(),
    "started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status":"STARTED_OUTCOME_UNKNOWN_DO_NOT_RETRY"}
  ledger["calls"].append(item);save()
  result=meta_call(model,instructions,payload,secret)
  item["response_sha256"]=hashlib.sha256(result.encode()).hexdigest()
  item["status"]="RESPONSE_RECEIVED"
  save()
  return result
 try:
  answer=run(args.question,gate["evidence"],key,caller=audited_caller,max_steps=8,max_consults=2)
  ledger["status"]="FINISHED_"+answer["status"]
  ledger["result"]=answer
 except Exception as exc:
  ledger["status"]="STOPPED_DO_NOT_AUTORETRY"
  ledger["error_type"]=type(exc).__name__
  ledger["note"]="Review audit before deciding whether another new run is appropriate"
 save()
 print(json.dumps({"status":ledger["status"],"model_calls":len(ledger["calls"]),
   "models":[c["model"] for c in ledger["calls"]],
   "consultations":len(ledger.get("result",{}).get("consultations",[])),
   "decision":ledger.get("result",{}).get("decision"),"output":str(target)},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
