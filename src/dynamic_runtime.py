"""HACK-016B — append-safe dynamic run with durable per-call checkpoints.

Each potentially billed call is recorded before dispatch, and its response
is independently checked before advancing. Never retry uncertain requests.
"""
import json
from pathlib import Path
from council import SPARK,WONDER,meta_call
from verification import verify_submission,evidence_hash

SCHEMA=("You are a FAITH analytical role, NOT a stakeholder. "
 "Answer this exact question using ONLY supplied evidence. "
 "Return STRICT JSON with exactly observations, hypotheses, investigations, abstentions. "
 "observations entries must have evidence_id and EXACT unchanged finding; "
 "all other fields must be nonempty string arrays. "
 "Write hypotheses, investigations and abstentions in natural French suitable for later oral narration. "
 "Keep the observation finding EXACTLY as provided even when it is English. "
 "Identify missing evidence; no invented impacts, approvals or numerical measurements.")

def execute_dynamic(plan,run_id,directory,key,caller=meta_call):
    if not plan["status"].startswith("READY_") or not plan["evidence"]:
        raise ValueError("No suitable FSDC evidence")
    if evidence_hash(plan["evidence"])!=plan["evidence_sha256"]:
        raise ValueError("Changed evidence fingerprint")
    if not key:
        raise ValueError("MODEL_API_KEY not configured")
    root=Path(directory)
    root.mkdir(parents=True,exist_ok=True)
    target=root/(run_id+".json")
    if target.exists():
        raise ValueError("A run with this ID already exists; never retry")
    data={
      "run_id":run_id,"schema_version":"HACK016B.1",
      "question":plan["question"],"sector":plan["sector"],
      "geography":plan["geography"],"topics":plan["topics"],
      "proposers":plan["proposers"],"missing_topics":plan["missing_topics"],
      "source_ids":[x["evidence_id"] for x in plan["evidence"]],
      "evidence_sha256":plan["evidence_sha256"],
      "evidence_snapshot":plan["evidence"],"planned_calls":len(plan["proposers"])+2,
      "calls_attempted":0,"status":"STARTED",
      "human_review_required":True,"steps":[]}
    def save():
        tmp=root/(run_id+".tmp")
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+chr(10),encoding="utf-8")
        tmp.replace(target)
    save()
    common={"question":plan["question"],"sector":plan["sector"],
            "geography":plan["geography"],"topics":plan["topics"],
            "missing_topics":plan["missing_topics"],
            "evidence_sha256":plan["evidence_sha256"],"evidence":plan["evidence"]}
    def call(role,model,payload):
        item={"role":role,"model":model,"status":"REQUEST_STARTED_DO_NOT_RETRY"}
        data["steps"].append(item)
        data["calls_attempted"]+=1
        data["status"]="RUNNING_"+role.upper()
        save()  # before any external request
        try:
            raw=caller(model,SCHEMA+"\nAnalytical role: "+role,payload,key)
            item["raw_model_text"]=raw
            report=verify_submission(raw,plan["evidence"],plan["evidence_sha256"])
            item["verification_status"]=report["status"]
            item["verification_issues"]=report["issues"]
            item["checked_publication"]=report.get("publication")
            item["status"]="ACCEPTED_STRUCTURAL_ONLY" if report["verified"] else "BLOCKED_BY_VERIFIER"
            save()
            if not report["verified"]:
                raise ValueError("Independent citation verification failed")
            return report["publication"]
        except Exception as error:
            item["status"]="STOPPED_NO_AUTOMATIC_RETRY"
            item["error_type"]=type(error).__name__
            save()
            raise
    try:
        views=[]
        for role in plan["proposers"]:
            pub=call(role,SPARK,common)
            views.append({"role":role,"checked_publication":pub})
        critique=call("scientific_critic",WONDER,
                      dict(common,verified_positions=views))
        final=call("final_synthesis",SPARK,
                   dict(common,verified_positions=views,verified_critique=critique))
        data["decision_support"]=final
        data["status"]="COMPLETED_STRUCTURALLY_CHECKED_HUMAN_REVIEW_REQUIRED"
    except Exception:
        data["status"]="STOPPED_DO_NOT_RETRY_BLINDLY"
    save()
    return data
