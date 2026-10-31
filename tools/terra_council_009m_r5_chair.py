"""009M-R5: last Muse call only; fresh journal, no automatic retries."""
import argparse,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from meta_scientific_dialogue_004 import meta_call
from terra_council_009m_runner import RULES,check

def main():
 p=argparse.ArgumentParser()
 for k in ("agenda","recovery","manifest","output"):p.add_argument("--"+k,required=True)
 p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 p.add_argument("--approve-recovery",action="store_true")
 a=p.parse_args()
 read=lambda x:json.loads(Path(x).read_text(encoding="utf-8-sig"))
 agenda,recovery,manifest=map(read,(a.agenda,a.recovery,a.manifest))
 turns=recovery.get("turns",[]);steps=agenda.get("steps",[])
 if (agenda.get("schema")!="TERRA_COUNCIL_009K_AGENDA_V1"
     or recovery.get("schema")!="TERRA_COUNCIL_009M_R4_PREVIEW_V1"
     or recovery.get("status")!="HUMAN_REVIEW_REQUIRED"
     or len(turns)!=18 or len(steps)!=19 or recovery.get("next_step")!=19):
  raise ValueError("Invalid R4 recovery")
 step=steps[18]
 if (step.get("role"),step.get("phase"))!=("scientific_chair","decision_brief"):
  raise ValueError("Chair step required")
 claims=manifest.get("claims",[])
 ids={c.get("evidence_id") for c in claims if c.get("admissibility")=="ADMISSIBLE_FOR_EXPLORATORY_DEBATE"}
 if (manifest.get("decision_authorized") is not False or not ids
     or len(ids)!=len(claims) or ids!=set(agenda["evidence_ids"])):
  raise ValueError("FSDC evidence mismatch")
 print("READY: 18 preserved, next 19, no Meta calls yet.",flush=True)
 if not a.execute:return
 if not (a.authorize_meta and a.approve_recovery):raise SystemExit("Explicit approval required")
 if not os.getenv("META_API_KEY") and not os.getenv("META_AI_API_KEY"):raise SystemExit("Meta key missing")
 out=Path(a.output)
 if out.exists():raise SystemExit("Output exists; do not retry")
 out.parent.mkdir(parents=True,exist_ok=True)
 state={"schema":"TERRA_COUNCIL_009M_R5_V1","status":"CALL_IN_FLIGHT",
   "step":19,"turns":turns,"scientific_review_required":True,
   "decision_authorized":False,"audio_authorized":False}
 with out.open("x",encoding="utf-8") as f:json.dump(state,f,ensure_ascii=False)
 try:
  raw=meta_call("muse-wonder-1.0",RULES,
   {"question":agenda["question"],"step":step,"prior":turns,"evidence":claims})
  rawpath=out.with_name(out.stem+"-raw-19.json")
  with rawpath.open("x",encoding="utf-8") as f:json.dump(raw,f,ensure_ascii=False,indent=2)
  state["raw_path"]=str(rawpath)
  out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
  final=check(raw,step,ids)
 except Exception as exc:
  state.update({"status":"STOP_NO_RETRY","error_type":type(exc).__name__,
                "error_message":str(exc)[:300]})
  out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
  raise SystemExit("Stopped; inspect journal, no retry")
 state["turns"].append(final)
 state["status"]="SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED"
 out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
 print("COMPLETE: 19 turns. Scientific review required.",flush=True)
if __name__=="__main__":main()
