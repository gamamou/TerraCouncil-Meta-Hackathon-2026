"""DEMO-008: inspect FAITH evidence coverage and query selected source records.
This module returns facts only. It never selects candidates or matches interventions.
"""
import argparse,json
from terra_demo_001_faith_gateway import Gateway,load

def discover(data):
 g=Gateway(data)
 return {"available":g.discover_faith_data(),
   "scientific_caveats":[
    "Permit cadastral area is not measured mine disturbance.",
    "Missing spatial matches do not imply zero environmental risk.",
    "Historical/active administrative status is not an observed footprint.",
    "RehabilitationSolution is a catalog, not a site prescription.",
    "Candidate screening score is not a probability of degradation."]}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--snapshot",required=True)
 p.add_argument("--entity",choices=["PilotCandidate","MiningPermit",
  "PermitSpatialContext","RehabilitationSolution"],default="MiningPermit")
 p.add_argument("--limit",type=int,default=10)
 args=p.parse_args()
 data=load(args.snapshot);g=Gateway(data)
 print(json.dumps({"discovery":discover(data),
   "query":{"entity":args.entity,"records":g.query_faith_data(args.entity,args.limit)}},
   ensure_ascii=False,indent=2))
if __name__=="__main__":main()
