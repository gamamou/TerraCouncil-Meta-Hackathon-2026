"""009O-C: checkpointed Muse oral council (review candidates, never audio)."""
import argparse,hashlib,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from meta_scientific_dialogue_004 import meta_call
from terra_council_009o_b2_oral import DIRECTOR,review
def save(path,obj):
 temp=path.with_name(path.name+".tmp")
 temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
 temp.replace(path)
def load_source(path):
 raw=path.read_bytes();obj=json.loads(raw.decode("utf-8-sig"))
 if obj.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or obj.get("audio_authorized") is not False:raise ValueError("Invalid source")
 turns=obj.get("turns",[])
 if len(turns)!=19 or any(t.get("turn")!=i or not t.get("scientific_source_text") for i,t in enumerate(turns,1)):raise ValueError("Invalid turns")
 return turns,hashlib.sha256(raw).hexdigest()
def check_candidate(item,response):
 if not isinstance(response,dict) or (response.get("role"),response.get("phase"))!=(item["speaker"],item["phase"]):
  raise ValueError("Role/phase mismatch")
 if not isinstance(response.get("spoken_text"),str) or not response["spoken_text"].strip():raise ValueError("Empty speech")
 return {"turn":item["turn"],"speaker":item["speaker"],"phase":item["phase"],
  "source_text":item["scientific_source_text"],"spoken_text":response["spoken_text"],
  "source_evidence_ids":item.get("source_evidence_ids",[]),
  "review_flags":review(response,item),
  "semantic_review":"PENDING_HUMAN_REVIEW"}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--packets",required=True);p.add_argument("--output",required=True)
 p.add_argument("--preview",action="store_true");p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 p.add_argument("--max-turns",type=int,default=3)
 a=p.parse_args()
 if a.preview==a.execute:raise SystemExit("Select exactly one of --preview or --execute")
 if not 1<=a.max_turns<=19:raise SystemExit("max-turns must be 1..19")
 src=Path(a.packets);out=Path(a.output)
 turns,sha=load_source(src)
 if out.exists():
  state=json.loads(out.read_text(encoding="utf-8-sig"))
  if state.get("source_sha256")!=sha or state.get("schema")!="TERRA_COUNCIL_009O_C_V1":raise SystemExit("Journal source mismatch")
  if state.get("status") not in ("READY","PARTIAL_REVIEW_REQUIRED"):raise SystemExit("Stopped or completed journal; no automatic retry")
 else:
  state={"schema":"TERRA_COUNCIL_009O_C_V1","source_sha256":sha,"status":"READY",
   "turns":[],"audio_authorized":False,"elevenlabs_calls":0}
 i=len(state["turns"])
 if i>19 or [x.get("turn") for x in state["turns"]]!=list(range(1,i+1)):raise SystemExit("Journal corrupt")
 print(json.dumps({"status":state["status"],"completed":i,"remaining":19-i,
  "planned_meta_calls":min(a.max_turns,19-i) if a.execute else 0,"elevenlabs_calls":0}),flush=True)
 if a.preview or i==19:return
 if not a.authorize_meta or not (os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta authorization/key required")
 if not out.exists():
  out.parent.mkdir(parents=True,exist_ok=True)
  with out.open("x",encoding="utf-8") as f:json.dump(state,f)
 for idx in range(i,min(19,i+a.max_turns)):
  item=turns[idx];state.update({"status":"CALL_IN_FLIGHT","current_turn":idx+1})
  save(out,state)
  try:
   response=meta_call("muse-wonder-1.0",DIRECTOR,{"role":item["speaker"],
    "phase":item["phase"],"scientific_source_text":item["scientific_source_text"],
    "preceding_oral_context":[{"speaker":x["speaker"],"spoken_text":x["spoken_text"]} for x in state["turns"][-2:]]})
   raw=out.with_name(out.stem+f"-raw-{idx+1:02d}.json")
   with raw.open("x",encoding="utf-8") as f:json.dump(response,f,ensure_ascii=False,indent=2)
   entry=check_candidate(item,response)
  except Exception as e:
   state.update({"status":"STOP_NO_RETRY","error":str(e)[:300]});save(out,state)
   raise SystemExit("Stopped: inspect journal/raw before resuming")
  state["turns"].append(entry)
  state.update({"status":"PARTIAL_REVIEW_REQUIRED","current_turn":None})
  save(out,state)
  print(f"ORAL {idx+1}/19 accepted for human review",flush=True)
 if len(state["turns"])==19:
  state["status"]="COMPLETE_HUMAN_REVIEW_REQUIRED";save(out,state)
 print(json.dumps({"status":state["status"],"completed":len(state["turns"]),"audio_authorized":False}))
if __name__=="__main__":main()
