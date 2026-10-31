"""010A: offline Muse multi-model scientific orchestration plan.

Does not call Meta. Model identifiers are configurable, not an API capability claim.
"""
import argparse,hashlib,json
from pathlib import Path

ROUTING={
 "scientific_chair":"wonder",
 "mining":"spark","environment":"spark","esg":"spark",
 "communities":"spark","agriculture":"spark"
}
def plan(manifest,agenda,wonder="muse-wonder-1.0",spark="muse-spark-1.3"):
 if manifest.get("schema")!="TERRA_COUNCIL_009F_EVIDENCE_V1":
  raise ValueError("009F evidence manifest required")
 if manifest.get("decision_authorized") is not False:
  raise ValueError("Evidence must remain exploratory")
 if agenda.get("schema")!="TERRA_COUNCIL_009K_AGENDA_V1":
  raise ValueError("009K agenda required")
 steps=agenda.get("steps",[])
 if len(steps)!=19:raise ValueError("19-turn agenda required")
 claims=manifest.get("claims",[])
 ids={c.get("evidence_id") for c in claims if c.get("admissibility")=="ADMISSIBLE_FOR_EXPLORATORY_DEBATE"
  and c.get("original_validation_status")=="SCREENED_NOT_FIELD_VALIDATED"}
 if not ids or ids!=set(agenda.get("evidence_ids",[])):
  raise ValueError("Scientific evidence IDs mismatch")
 if manifest.get("question")!=agenda.get("question"):
  raise ValueError("Scientific question mismatch")
 if not wonder.strip() or not spark.strip():raise ValueError("Nonempty model IDs required")
 phases=[]
 for i,s in enumerate(steps,1):
  role=s.get("role")
  if role not in ROUTING:raise ValueError("Unregistered role")
  lane=ROUTING[role]
  phases.append({"turn":i,"role":role,"phase":s.get("phase"),"model":wonder if lane=="wonder" else spark,
   "max_words":s.get("max_words"),"scientific_gate":"SCREENED_NOT_FIELD_VALIDATED"})
 return {"schema":"TERRA_COUNCIL_010A_MULTI_MODEL_PLAN_V1",
  "status":"OFFLINE_PREVIEW_ONLY","question":agenda["question"],
  "models":{"wonder":wonder,"spark":spark},
  "workflow":[
   {"stage":"evidence_gate","model":None,"purpose":"Verify FSDC scientific provenance"},
   {"stage":"council","model":"per_turn_routing","purpose":"19 role-grounded scientific turns"},
   {"stage":"critical_review","model":wonder,"purpose":"Review evidence entailment and uncertainties"},
   {"stage":"oral_director","model":wonder,"purpose":"Whole-council natural spoken dialogue"},
   {"stage":"semantic_integrity","model":wonder,"purpose":"Flag unsupported additions/omissions"},
   {"stage":"human_approval","model":None,"purpose":"Approve science and editorial before any audio"}],
  "routing":phases,"evidence_ids":sorted(ids),
  "existing_009m_preserved":True,"future_generation_enabled":False,
  "semantic_approval":False,"decision_authorized":False,"audio_authorized":False,
  "api_calls":0,"elevenlabs_calls":0,
  "note":"Model names must be verified against account access before live calls. Reasoning effort and tool calling not yet integrated."}
def main():
 p=argparse.ArgumentParser()
 for name in ("manifest","agenda","output"):p.add_argument("--"+name,required=True)
 p.add_argument("--wonder",default="muse-wonder-1.0")
 p.add_argument("--spark",default="muse-spark-1.3")
 a=p.parse_args()
 mraw=Path(a.manifest).read_bytes();araw=Path(a.agenda).read_bytes()
 result=plan(json.loads(mraw.decode("utf-8-sig")),json.loads(araw.decode("utf-8-sig")),a.wonder,a.spark)
 result["manifest_sha256"]=hashlib.sha256(mraw).hexdigest()
 result["agenda_sha256"]=hashlib.sha256(araw).hexdigest()
 with Path(a.output).open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":result["status"],"stages":len(result["workflow"]),
  "turns":len(result["routing"]),"models":result["models"],
  "api_calls":0,"elevenlabs_calls":0},ensure_ascii=False))
if __name__=="__main__":main()
