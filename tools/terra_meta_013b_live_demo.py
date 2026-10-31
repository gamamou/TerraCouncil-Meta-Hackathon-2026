"""013B CLI: preview first, explicit opt-in for real Muse calls."""
import argparse,json,os
from pathlib import Path
from verification import gate_evidence
from terra_meta_013b_muse_runtime import run

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--question",required=True)
 p.add_argument("--evidence",required=True)
 p.add_argument("--geography",default="Boké, Guinea")
 p.add_argument("--sector",default="mining")
 p.add_argument("--execute",action="store_true")
 p.add_argument("--output")
 a=p.parse_args()
 records=json.loads(Path(a.evidence).read_text(encoding="utf-8-sig"))
 if not isinstance(records,list):raise SystemExit("Evidence must be a JSON list")
 gate=gate_evidence(records,a.sector,a.geography)
 ready=gate["evidence"]
 if not a.execute:
  print(json.dumps({"status":gate["status"],"accepted_ids":[r["evidence_id"] for r in ready],
   "rejected_count":len(gate["rejected"]),"source_sha256":gate["evidence_sha256"],
   "meta_calls":0,"next":"--execute --output <new file> (billable Meta calls)"},ensure_ascii=False,indent=2))
  return
 if not a.output:raise SystemExit("--output required for live calls")
 if not ready:raise SystemExit("No admissible or screened evidence, no calls")
 key=os.environ.get("MODEL_API_KEY")
 if not key:raise SystemExit("MODEL_API_KEY absent in this terminal")
 path=Path(a.output)
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("x",encoding="utf-8") as f:json.dump({"status":"REQUEST_STARTED_NO_AUTOMATIC_RETRY"},f)
 try:
  result=run(a.question,ready,key,max_steps=6)
 except Exception as exc:
  result={"status":"STOP_OUTCOME_UNCERTAIN_DO_NOT_RETRY","error_type":type(exc).__name__}
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
