"""TERRA-META-DEMO-007: quantify source coverage; never infer missing site evidence."""
import argparse,json
from pathlib import Path
from terra_demo_001_faith_gateway import load

FIELDS=["cadastral_area_km2","substance","region","prefecture",
 "administrative_status","has_observed_footprint","confidence_level"]
def coverage(data):
 candidates=data.get("PilotCandidate",[])
 permits={}
 for p in data.get("MiningPermit",[]):
  uid=p.get("shape_uid")
  if uid:permits.setdefault(uid,[]).append(p)
 linked=[permits[c.get("shape_uid")][0] for c in candidates
         if len(permits.get(c.get("shape_uid"),[]))==1]
 return {"candidate_count":len(candidates),"unique_permit_joins":len(linked),
  "fields":{f:{"present":sum(p.get(f) is not None for p in linked),
                "missing":sum(p.get(f) is None for p in linked)}
            for f in FIELDS},
  "matched_footprint_relation_count":sum(
    r.get("shape_uid") in {c.get("shape_uid") for c in candidates}
    for r in data.get("PermitFootprintRelation",[])),
  "matched_spatial_context_count":sum(
    r.get("shape_uid") in {c.get("shape_uid") for c in candidates}
    for r in data.get("PermitSpatialContext",[])),
  "scientific_limits":["cadastral area is not observed degradation area",
    "a blank spatial join is not evidence of zero environmental risk",
    "no model-based rehabilitation prescription is verified by this audit"]}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--snapshot",required=True)
 args=p.parse_args()
 print(json.dumps(coverage(load(args.snapshot)),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
