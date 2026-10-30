"""DEMO-005: bounded three-call Muse scientific deliberation.
One Spark analysis, one Wonder critique, one Spark revision. No JSON tool-call
dependency. Input is a locally reviewed FAITH snapshot. No invented joins.
"""
import argparse,datetime,hashlib,json,os,re
from pathlib import Path
from council import meta_call,SPARK,WONDER
from terra_demo_001_faith_gateway import load
from terra_demo_003_preflight import preflight

POLICY="""You are part of TerraCouncil, a decision-support scientific council.
Use only supplied FAITH source facts. Do not fabricate site diagnostics, distances,
geography or confirmed mining footprints. Priority screening is NOT proof of a
restoration need. Thirty candidate sites share a score of 100; do not claim
unwarranted precision or uniqueness of five chosen sites. Distinguish candidate
investigation priorities from confirmed restoration targets. The intervention
catalog is unassigned to sites: any solution is conditional, subject to field
diagnosis and human approval. Cite exact shape_uid and solution_id for proposed
choices. State material uncertainties. Answer in French, substantive and clear."""
SPARK_FIRST=POLICY+"""
Act as Muse Spark. Independently reason from the supplied candidate records and
catalog. Propose five named-by-UID candidates for investigation and tentative
rehabilitation consideration, explain why selection among ties is provisional.
For each provide potential catalog options only if clearly conditional.
Do not present a pre-approved rehabilitation plan. Use exact IDs."""
WONDER_CRITIC=POLICY+"""
Act as Muse Wonder, an independent scientific critic. Analyze Spark's actual
proposed five selections and intervention rationales. Challenge score ties,
lack of verified site-specific diagnosis, lack of observed footprint, absence of
spatial evidence, and unjustified interventions. Identify which claims are
supported and which require field tests. Respond in French."""
SPARK_REVISE=POLICY+"""
Act as Muse Spark. Revise your preliminary response in light of Wonder's
specific critique. Provide five provisional candidate IDs and clearly separate
FAITH observations, model judgments, conditional intervention possibilities
and field investigations. Explicitly say which Wonder criticisms you accepted
or could not resolve. Never claim five uniquely optimal rehabilitation sites.
If evidence cannot discriminate five, state that clearly without inventing it."""

def brief(data):
 candidates=data["PilotCandidate"]
 permit_by_uid={p["shape_uid"]:p for p in data["MiningPermit"]}
 return {"source_snapshot":"20260716_232803_UTC",
  "scope":"exploratory_faith_screening_not_field_validated",
  "candidates":[{"shape_uid":c["shape_uid"],"score_0_100":c.get("score_0_100"),
    "selection_reason":c.get("selection_reason"),
    "pilot_category":c.get("pilot_category"),
    "national_rank":permit_by_uid[c["shape_uid"]].get("national_rank"),
    "has_observed_footprint":permit_by_uid[c["shape_uid"]].get("has_observed_footprint"),
    "confidence_level":permit_by_uid[c["shape_uid"]].get("confidence_level")}
   for c in candidates],
  "solutions":[{"solution_id":s["solution_id"],"solution_name":s.get("solution_name"),
   "degradation_types":s.get("degradation_types"),
   "required_field_validation":s.get("required_field_validation")}
   for s in data["RehabilitationSolution"]],
  "source_limits":{"site_spatial_records":len(data.get("PermitSpatialContext",[])),
  "observed_site_diagnostics":len(data.get("SiteRehabilitationRecommendation",[])),
  "model_selection_is_not_approved":True}}

def run(data,question,api_key,output,caller=meta_call):
 quality=preflight(data)
 if quality["status"]!="READY_FOR_EXPLORATORY_MUSE_DEMO":
  raise ValueError("FAITH scientific preflight blocked run")
 source=brief(data)
 source_hash=hashlib.sha256(json.dumps(source,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
 record={"status":"STARTED_DO_NOT_AUTORETRY","question":question,
  "source_sha256":source_hash,"source_counts":{"candidates":len(source["candidates"]),
  "catalog":len(source["solutions"])},"calls":[]}
 def save():
  output.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
 save()
 sequence=[
  ("SPARK_INITIAL",SPARK,SPARK_FIRST,lambda:{"question":question,"faith":source}),
  ("WONDER_CRITIQUE",WONDER,WONDER_CRITIC,lambda:{"question":question,"faith":source,
   "spark_initial":record["calls"][0]["response"]}),
  ("SPARK_REVISED",SPARK,SPARK_REVISE,lambda:{"question":question,"faith":source,
   "spark_initial":record["calls"][0]["response"],
   "wonder_critique":record["calls"][1]["response"]})]
 valid_uids={c["shape_uid"] for c in source["candidates"]}
 valid_solutions={s["solution_id"] for s in source["solutions"]}
 for label,model,instruction,payload in sequence:
  record["next_call"]=label
  save()
  try:
   response=caller(model,instruction,payload(),api_key)
   if not isinstance(response,str) or not response.strip():
    raise ValueError("Empty Meta answer")
   cited_uids=set(re.findall(r"GUIDSHAPE:[A-Za-z0-9-]+",response))
   cited_sol=set(re.findall(r"SOL-CAT-\\d{5}",response))
   record["calls"].append({"stage":label,"model":model,"response":response,
      "cited_site_ids":sorted(cited_uids),"invalid_site_ids":sorted(cited_uids-valid_uids),
      "cited_solution_ids":sorted(cited_sol),"invalid_solution_ids":sorted(cited_sol-valid_solutions)})
   record.pop("next_call",None)
   save()
  except Exception as exc:
   record["status"]="INTERRUPTED_DO_NOT_AUTORETRY"
   record["error_type"]=type(exc).__name__
   record["error_message"]=str(exc)[:400]
   save()
   return record
 record["status"]="GENERATED_NEEDS_SCIENTIFIC_REVIEW"
 record["warnings"]=["Citations checked for ID membership only, not factual truth.",
  "Free-text scientific assertions require independent validation.",
  "No automatic site-treatment approval."]
 save()
 return record

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--snapshot",required=True)
 p.add_argument("--question",required=True)
 p.add_argument("--output",required=True)
 p.add_argument("--execute",action="store_true")
 a=p.parse_args()
 data=load(a.snapshot)
 if not a.execute:
  print(json.dumps({"status":"PREVIEW_NO_CALLS","preflight":preflight(data)["status"],
   "planned_calls":["SPARK_INITIAL","WONDER_CRITIQUE","SPARK_REVISED"]},ensure_ascii=False))
  return
 key=os.getenv("MODEL_API_KEY")
 if not key:raise SystemExit("MODEL_API_KEY missing")
 path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():raise SystemExit("Output exists; refusing to overwrite or retry")
 path.write_text(json.dumps({"status":"RESERVED_DO_NOT_AUTORETRY"}),encoding="utf-8")
 outcome=run(data,a.question,key,path)
 print(json.dumps({"status":outcome["status"],"completed_calls":len(outcome["calls"]),
                   "output":str(path)},ensure_ascii=False))
 if outcome["status"]!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":raise SystemExit(2)
if __name__=="__main__":main()
