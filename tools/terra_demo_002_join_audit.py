"""DEMO-002: local FAITH snapshot QA. Read-only, no model, no new science.
Use on exported JSON keyed by Base44 entity names. Never silently infer joins.
"""
import argparse,json
from collections import Counter
from pathlib import Path
from terra_demo_001_faith_gateway import load
def audit(data):
 candidates=data.get("PilotCandidate",[])
 permits=data.get("MiningPermit",[])
 contexts=data.get("PermitSpatialContext",[])
 solutions=data.get("RehabilitationSolution",[])
 groups={}
 for name,rows in (("MiningPermit",permits),("PermitSpatialContext",contexts)):
  m={}
  for row in rows:
   uid=row.get("shape_uid")
   if uid:
    m.setdefault(uid,[]).append(row)
  groups[name]=m
 rows=[]
 for c in candidates:
  uid=c.get("shape_uid")
  p=groups["MiningPermit"].get(uid,[])
  s=groups["PermitSpatialContext"].get(uid,[])
  rows.append({"shape_uid":uid,"candidate_score":c.get("score_0_100"),
     "permit_match_count":len(p),"spatial_match_count":len(s),
     "permit_score":p[0].get("score_0_100") if len(p)==1 else None,
     "has_observed_footprint":p[0].get("has_observed_footprint") if len(p)==1 else None,
     "river_distance_m":s[0].get("nearest_distance_m") if len(s)==1 else None,
     "school_distance_m":s[0].get("nearest_mapped_school_distance_m") if len(s)==1 else None,
     "spatial_coverage":"AVAILABLE" if len(s)==1 and any(s[0].get(k) is not None for k in ("nearest_distance_m","nearest_mapped_school_distance_m")) else "NOT_CONFIRMED"})
 matched=sum(r["permit_match_count"]==1 for r in rows)
 ties=Counter(str(r["candidate_score"]) for r in rows)
 return {"status":"JOIN_AUDIT_ONLY_NO_SCIENTIFIC_APPROVAL","candidate_count":len(candidates),
   "permit_count_loaded":len(permits),"spatial_count_loaded":len(contexts),
   "catalog_solution_count":len(solutions),
   "candidates_with_unique_permit":matched,
   "candidates_with_unique_spatial_context":sum(r["spatial_match_count"]==1 for r in rows),
   "score_ties":{k:v for k,v in ties.items() if v>1},
   "site_join_audit":rows,
   "limits":["Exact shape_uid joins only; no guessed spatial associations.",
    "No Python selection of five sites or matching of rehabilitation measures."]}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--snapshot",required=True);p.add_argument("--output",required=True)
 a=p.parse_args()
 report=audit(load(a.snapshot))
 target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("x",encoding="utf8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps({k:v for k,v in report.items() if k!="site_join_audit"},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
