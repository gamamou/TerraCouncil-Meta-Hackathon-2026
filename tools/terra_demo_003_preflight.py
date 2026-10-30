"""DEMO-003: preflight a local FAITH export before any Muse model call."""
import argparse,json
from pathlib import Path
from terra_demo_001_faith_gateway import load
from terra_demo_002_join_audit import audit

def preflight(data):
 report=audit(data)
 if report["candidate_count"]<5:
  return {"status":"BLOCKED_TOO_FEW_CANDIDATES","audit":report}
 if report["catalog_solution_count"]==0:
  return {"status":"BLOCKED_NO_SOLUTION_CATALOG","audit":report}
 if report["candidates_with_unique_permit"]<5:
  return {"status":"BLOCKED_INSUFFICIENT_PERMIT_JOINS","audit":report}
 return {"status":"READY_FOR_EXPLORATORY_MUSE_DEMO","audit":report,
    "claim_boundaries":["Priority score is not independently validated need for rehabilitation.",
    "Observed footprint flags must remain as recorded; false is not proof of no mine.",
    "A catalog rehabilitation solution is not a prescribed intervention.",
    "No site-level spatial context is inferred from approximate regional records."]}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--snapshot",required=True)
 p=parser.parse_args()
 result=preflight(load(p.snapshot))
 a=result["audit"]
 print(json.dumps({"status":result["status"],"candidate_count":a["candidate_count"],
  "permit_joins":a["candidates_with_unique_permit"],"spatial_joins":a["candidates_with_unique_spatial_context"],
  "catalog_solutions":a["catalog_solution_count"],"score_ties":a["score_ties"]},ensure_ascii=False,indent=2))
 if result["status"]!="READY_FOR_EXPLORATORY_MUSE_DEMO":raise SystemExit(2)
if __name__=="__main__":main()
