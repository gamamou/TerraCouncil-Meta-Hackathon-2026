"""TERRA-META-011B: deterministic FSDC-gated council planner (offline prototype).
No autonomous scientific conclusions, network, model calls or audio.
Policy and keyword selection are explicit heuristics, not ML inference.
"""
import argparse,hashlib,json,re
from pathlib import Path

ROLES={
 "mining": ("mine","minier","minière","bauxite","gisement","exploitation","minerai","géologie"),
 "environment": ("environnement","climat","eau","hydro","biodivers","forêt","pollution","inondation"),
 "agriculture": ("agriculture","agricole","sol","culture","irrigation","récolte"),
 "communities": ("communauté","population","social","village","habitant","déplacement"),
 "esg": ("esg","gouvernance","conformité","traçabilité","audit","décision","risque"),
}
ORDER=("mining","environment","agriculture","communities","esg")
def sha(b):return hashlib.sha256(b).hexdigest()
def policy(question, evidence, max_turns, max_calls):
 if not isinstance(question,str) or not question.strip():raise ValueError("A nonempty scientific question is required")
 if len(question)>5000:raise ValueError("Question too long")
 if not isinstance(evidence,dict) or evidence.get("schema")!="TERRA_META_011B_EVIDENCE_V1":raise ValueError("Explicit FSDC evidence manifest required")
 sources=evidence.get("sources")
 if not isinstance(sources,list):raise ValueError("Manifest requires sources list")
 if not isinstance(max_turns,int) or isinstance(max_turns,bool) or not 3<=max_turns<=24:raise ValueError("max_turns must be 3..24")
 if not isinstance(max_calls,int) or isinstance(max_calls,bool) or not 0<=max_calls<=72:raise ValueError("max_calls must be 0..72")
 verified=[]
 for s in sources:
  if not isinstance(s,dict) or not all(isinstance(s.get(k),str) and s[k].strip() for k in ("id","provider","version","license","provenance","coverage","limitations")):
   raise ValueError("Every evidence source needs ID, provider, version, license, provenance, coverage, limitations")
  if s.get("validation") not in ("SCREENED_NOT_FIELD_VALIDATED","FIELD_VALIDATED","NOT_VALIDATED"):
   raise ValueError("Unknown validation level")
  verified.append(s)
 if len({x["id"] for x in verified})!=len(verified):raise ValueError("Duplicate evidence IDs")
 q=question.casefold()
 selected=[name for name,keys in ROLES.items() if any(key in q for key in keys)]
 if not selected:selected=["environment","esg"]
 selected=[x for x in ORDER if x in selected]
 # Always add ESG as oversight, not as a data scientist or automatic verifier.
 if "esg" not in selected:selected.append("esg")
 # Chair opens and closes; one primary contribution per expert, with capped optional reflection.
 n=min(max_turns,max(3,len(selected)+2))
 roles=["president"]+selected[:max(1,n-2)]
 while len(roles)<n-1:roles.append(selected[(len(roles)-1)%len(selected)])
 roles.append("president")
 admissible=bool(verified) and all(x["validation"] in ("SCREENED_NOT_FIELD_VALIDATED","FIELD_VALIDATED") for x in verified)
 missing=len(verified)==0 or not admissible
 # Planning only, never authorize execution from plan or imply field validation.
 steps=[]
 for i,role in enumerate(roles,1):
  step={"turn":i,"role":role,
        "goal":("Define scope, evidence gaps and a focused question" if i==1 else
                "Conditional synthesis of uncertainty and further evidence" if i==len(roles) else
                "Contribute only evidence-grounded domain reasoning"),
        "execution_status":"PLANNED_NO_MODEL_CALL",
        "human_review_required":True}
  steps.append(step)
 return {"schema":"TERRA_META_011B_PLAN_V1","status":"PLAN_REQUIRES_HUMAN_REVIEW",
  "question":question,"question_sha256":sha(question.encode("utf-8")),
  "selection_method":"DETERMINISTIC_KEYWORD_HEURISTIC_NOT_MODEL",
  "selected_experts":selected,"turn_count":len(steps),
  "evidence_status":"SCREENING_READY_NOT_FIELD_VALIDATED" if admissible else "INSUFFICIENT_EVIDENCE",
  "source_count":len(verified),"evidence_ids":[s["id"] for s in verified],
  "evidence_manifest_sha256":sha(json.dumps(evidence,ensure_ascii=False,sort_keys=True).encode("utf-8")),
  "max_meta_calls":max_calls,"calls_per_turn_ceiling":3,
  "model_calls_authorized":False,"actual_meta_calls":0,
  "scientific_approval":False,"decision_authorized":False,"audio_authorized":False,
  "may_form_empirical_conclusions":False,
  "steps":steps}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--question",required=True);p.add_argument("--evidence",required=True)
 p.add_argument("--output",required=True);p.add_argument("--max-turns",type=int,default=8)
 p.add_argument("--max-calls",type=int,default=12)
 a=p.parse_args();out=Path(a.output)
 if out.exists():raise SystemExit("Output exists; no overwrite")
 evidence=json.loads(Path(a.evidence).read_text(encoding="utf-8-sig"))
 result=policy(a.question,evidence,a.max_turns,a.max_calls)
 with out.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":result["status"],"selected_experts":result["selected_experts"],
 "turn_count":result["turn_count"],"evidence_status":result["evidence_status"],
 "potential_meta_calls_ceiling":result["max_meta_calls"],"actual_meta_calls":0,"audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
