"""010C: checkpointed Wonder/Spark FSDC council, 19 turns.

Preview offline; execute only after explicit Meta authorization. A failed or
uncertain call stops permanently pending manual review; no automatic retry.
"""
import argparse,hashlib,json,os,sys,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from terra_council_010a_plan import plan
from terra_council_010b_reasoning import evidence_for
from meta_scientific_dialogue_004 import meta_call

SYSTEM="""Tu joues uniquement le role scientifique demande dans une simulation
multi-agents TerraCouncil. Les expertises sont des roles pilotes par programme;
ne pretend jamais etre un expert humain independant.
Utilise exclusivement les preuves FSDC admissibles et les interventions precedentes.
Ne cree pas d'impact, d'exposition miniere, de causalite, de conformite ou
d'autorisation. Distingue decisions d'investigation et developpement minier.
Une recommandation methodologique peut avoir evidence_ids=[].
Les chiffres ne sont pas des observations terrain. Reponds aux idees deja
exprimees sans inventer d'accord ou d'opposition.
Reponds en JSON strict:
{"role":"ROLE","phase":"PHASE","text":"INTERVENTION","evidence_ids":["ID"]}.
Respecte le maximum de mots; dialogue court, naturel et scientifique."""
def save(path,data):
 temp=path.with_name(path.name+".tmp")
 temp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 temp.replace(path)
def checked(answer,step,allowed):
 if not isinstance(answer,dict) or (answer.get("role"),answer.get("phase"))!=(step["role"],step["phase"]):
  raise ValueError("Wrong role or phase")
 speech=answer.get("text");refs=answer.get("evidence_ids")
 if not isinstance(speech,str) or not speech.strip() or len(speech.split())>step["max_words"]:
  raise ValueError("Missing or oversized turn")
 if not isinstance(refs,list) or any(not isinstance(x,str) or x not in allowed for x in refs):
  raise ValueError("Invalid evidence reference")
 return {"turn":step["turn"],"model":step["model"],"role":step["role"],
  "phase":step["phase"],"text":speech,"evidence_ids":refs,
  "review_status":"SCIENTIFIC_HUMAN_REVIEW_REQUIRED"}
def main():
 p=argparse.ArgumentParser()
 for arg in ("manifest","agenda","output"):p.add_argument("--"+arg,required=True)
 p.add_argument("--wonder",default="muse-wonder-1.0")
 p.add_argument("--spark",default="muse-spark-1.3")
 p.add_argument("--preview",action="store_true");p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 p.add_argument("--max-turns",type=int,default=2)
 a=p.parse_args()
 if a.preview==a.execute:raise SystemExit("Choose --preview or --execute")
 if not 1<=a.max_turns<=19:raise SystemExit("max-turns must be between 1 and 19")
 mr=Path(a.manifest).read_bytes();ar=Path(a.agenda).read_bytes()
 manifest=json.loads(mr.decode("utf-8-sig"));agenda=json.loads(ar.decode("utf-8-sig"))
 specification=plan(manifest,agenda,a.wonder,a.spark)
 sources=evidence_for(manifest);steps=specification["routing"]
 digest={"manifest":hashlib.sha256(mr).hexdigest(),"agenda":hashlib.sha256(ar).hexdigest()}
 out=Path(a.output)
 if out.exists():
  state=json.loads(out.read_text(encoding="utf-8-sig"))
  if state.get("schema")!="TERRA_COUNCIL_010C_V1" or state.get("source_sha256")!=digest:
   raise SystemExit("Existing journal does not match source")
  if state.get("status") not in ("READY","PARTIAL_REVIEW_REQUIRED"):
   raise SystemExit("Journal blocked or complete; do not retry")
 else:
  state={"schema":"TERRA_COUNCIL_010C_V1","status":"READY",
   "source_sha256":digest,"models":specification["models"],
   "turns":[],"audio_authorized":False,"decision_authorized":False,
   "scientific_review_required":True}
 if state["models"]!=specification["models"]:raise SystemExit("Model assignment changed")
 count=len(state["turns"])
 if count>19 or [t.get("turn") for t in state["turns"]]!=list(range(1,count+1)):
  raise SystemExit("Invalid journal sequence")
 for t in state["turns"]:
  route=steps[t["turn"]-1]
  if (t.get("role"),t.get("phase"),t.get("model"))!=(route["role"],route["phase"],route["model"]):
   raise SystemExit("Journal route mismatch")
 print(json.dumps({"status":state["status"],"completed":count,"remaining":19-count,
   "next_model":steps[count]["model"] if count<19 else None,
   "planned_calls":min(a.max_turns,19-count) if a.execute else 0,
   "completed_calls_this_run":0,"elevenlabs_calls":0}),flush=True)
 if a.preview or count==19:return
 if not a.authorize_meta:raise SystemExit("Explicit Meta authorization required")
 if not (os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta key missing")
 if not out.exists():
  out.parent.mkdir(parents=True,exist_ok=True)
  with out.open("x",encoding="utf-8") as f:json.dump(state,f)
 for index in range(count,min(19,count+a.max_turns)):
  step=steps[index];state.update(status="CALL_IN_FLIGHT",current_turn=index+1)
  save(out,state)
  try:
   answer=meta_call(step["model"],SYSTEM,{"question":manifest["question"],
    "turn_spec":step,"evidence":sources,"prior_turns":state["turns"]})
   rawpath=out.with_name(out.stem+f"-raw-{index+1:02d}.json")
   with rawpath.open("x",encoding="utf-8") as f:json.dump(answer,f,ensure_ascii=False,indent=2)
   checked_turn=checked(answer,step,set(specification["evidence_ids"]))
  except Exception as e:
   state.update(status="STOP_NO_RETRY",error_type=type(e).__name__,error_message=str(e)[:350])
   save(out,state)
   raise SystemExit("Stopped; inspect journal and raw response before any retry")
  state["turns"].append(checked_turn)
  state.update(status="PARTIAL_REVIEW_REQUIRED",current_turn=None)
  save(out,state)
  print(f"TURN {index+1}/19: {step['role']} / {step['model']}",flush=True)
 if len(state["turns"])==19:
  state["status"]="COMPLETE_SCIENTIFIC_REVIEW_REQUIRED";save(out,state)
 print(json.dumps({"status":state["status"],"completed":len(state["turns"]),
   "audio_authorized":False,"decision_authorized":False}),flush=True)
if __name__=="__main__":main()
