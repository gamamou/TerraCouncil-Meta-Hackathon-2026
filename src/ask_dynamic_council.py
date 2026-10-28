import argparse
import json
import os
from pathlib import Path
from dynamic_council import plan_question
from dynamic_debate import run_dynamic

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--question",required=True)
    p.add_argument("--evidence",required=True)
    p.add_argument("--geography",default="Boké, Guinea")
    p.add_argument("--sector")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--approve-cost-and-sharing",action="store_true")
    a=p.parse_args()
    records=json.loads(Path(a.evidence).read_text(encoding="utf-8"))
    plan=plan_question(a.question,records,a.geography,a.sector)
    if not a.execute:
        print(json.dumps({"mode":"PREVIEW_NO_MODEL_CALLS","plan":plan},
              indent=2,ensure_ascii=False))
        return
    if not a.approve_cost_and_sharing:
        raise ValueError("Paid Meta execution requires explicit approval")
    if not plan["status"].startswith("READY_"):
        print(json.dumps({"status":plan["status"],"calls_attempted":0}))
        return
    result=run_dynamic(plan,os.environ.get("MODEL_API_KEY",""))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
