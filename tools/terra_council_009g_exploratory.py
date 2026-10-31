"""009G: exploratory Boké council, using the real 009F manifest.

Preview makes no API calls. Execution requires --execute and --authorize-meta,
writes an exclusive attempt journal, never retries, and never authorizes a
mining/ESG decision or downstream audio.
"""
import argparse, json, os
from pathlib import Path
from terra_council_009_route import propose_route
from terra_council_009d_muse import request_muse, check_response

SCHEMA="TERRA_COUNCIL_009G_EXPLORATORY_V1"
ADMITTED="ADMISSIBLE_FOR_EXPLORATORY_DEBATE"

def make_plan(manifest):
    if manifest.get("schema")!="TERRA_COUNCIL_009F_EVIDENCE_V1":
        raise ValueError("009F manifest required")
    if manifest.get("scientific_status")!="EXPLORATORY_DISCUSSION_ONLY":
        raise ValueError("Manifest must be exploratory")
    if manifest.get("decision_authorized") is not False or manifest.get("human_review_required") is not True:
        raise ValueError("Unsafe or unreviewed evidence")
    claims=manifest.get("claims",[])
    if not claims or any(c.get("admissibility")!=ADMITTED or
          c.get("decision_admissibility")!="NOT_ADMISSIBLE_FOR_DECISION" or
          c.get("original_validation_status")!="SCREENED_NOT_FIELD_VALIDATED"
          for c in claims):
        raise ValueError("Missing or elevated exploratory evidence")
    ids=[c["evidence_id"] for c in claims]
    if len(ids)!=len(set(ids)):raise ValueError("Duplicate evidence IDs")
    question=manifest.get("question")
    if not question:raise ValueError("Missing original question")
    route=propose_route(question)
    roles=route["agents_selected"]
    if not roles:raise ValueError("No eligible domain experts")
    steps=[{"role":"scientific_chair","phase":"opening"}]
    steps.extend({"role":r,"phase":"position"} for r in roles)
    steps.append({"role":"scientific_chair","phase":"cross_examination"})
    steps.extend({"role":r,"phase":"rebuttal_and_revision"} for r in roles)
    steps.append({"role":"scientific_chair","phase":"deliberation"})
    # 009D request_muse accepts the structure below; never relabel as VERIFIED.
    evidence=[{"evidence_id":c["evidence_id"],"source_version":c["source_version"],
       "claim":c["finding"],"source":c["source"],"method":c["method"],
       "admissibility":c["admissibility"],"original_validation_status":c["original_validation_status"],
       "limitations":c["limitations"]} for c in claims]
    return {"schema":SCHEMA,"question":question,"active_experts":roles,
      "steps":steps,"evidence":evidence,"context_only":manifest.get("context_only",[]),
      "status":"EXPLORATORY_PREVIEW","decision_authorized":False,
      "human_review_required":True,"audio_authorized":False,
      "limitations":manifest.get("limitations",[]),"meta_calls":0}

def execute(plan,path,key,model):
    path=Path(path)
    if path.exists():raise FileExistsError("Prior attempt exists. Never overwrite or retry.")
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8") as stream:
        json.dump({"schema":SCHEMA,"status":"ATTEMPT_STARTED","turns":[]},stream)
    turns=[]
    allowed={e["evidence_id"] for e in plan["evidence"]}
    for number,step in enumerate(plan["steps"],1):
        # Include guardrails in each role's evidence context. The response
        # is not scientifically validated simply because citations exist.
        role_plan=dict(plan)
        role_plan["question"] += (
          "\nMANDAT: débat exploratoire sur les investigations prioritaires seulement. "
          "NE PAS conclure à une exposition effective, causalité minière, conformité ESG "
          "ou autorisation d'exploitation. WorldCover 2021 n'est pas une tendance 2026. "
          "Présenter explicitement les incertitudes et limites.")
        try:
            candidate=request_muse(step,role_plan,turns,key,model)
            turn=check_response(candidate,step,allowed)
            turns.append(turn)
        except Exception as error:
            path.write_text(json.dumps({"schema":SCHEMA,
                 "status":"STOP_REVIEW_NO_RETRY","steps_completed":len(turns),
                 "error_type":type(error).__name__,"http_status":getattr(error,"code",None),
                 "turns":turns,"decision_authorized":False,
                 "audio_authorized":False},ensure_ascii=False,indent=2),encoding="utf-8")
            raise RuntimeError("Muse stopped. Inspect run and billing before retry.") from None
        path.write_text(json.dumps({"schema":SCHEMA,"status":"IN_PROGRESS",
             "steps_completed":number,"turns":turns,"decision_authorized":False,
             "human_review_required":True,"audio_authorized":False},ensure_ascii=False,indent=2),encoding="utf-8")
        print("Muse",number,"/",len(plan["steps"]),step["role"],step["phase"],flush=True)
    record=json.loads(path.read_text(encoding="utf-8"))
    record["status"]="SCIENTIFIC_REVIEW_REQUIRED"
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--authorize-meta",action="store_true")
    p.add_argument("--model",default="muse-wonder-1.0")
    a=p.parse_args()
    plan=make_plan(json.loads(Path(a.manifest).read_text(encoding="utf-8-sig")))
    print(json.dumps({"status":plan["status"],"question":plan["question"],
      "experts":plan["active_experts"],"steps":len(plan["steps"]),
      "planned_meta_calls":len(plan["steps"]),"actual_meta_calls":0,
      "decision_authorized":False},ensure_ascii=False,indent=2),flush=True)
    if not a.execute:return
    if not a.authorize_meta:raise SystemExit("--authorize-meta required")
    key=os.environ.get("META_API_KEY") or os.environ.get("META_AI_API_KEY")
    if not key:raise SystemExit("META_API_KEY missing")
    execute(plan,a.output,key,a.model)
if __name__=="__main__":main()
