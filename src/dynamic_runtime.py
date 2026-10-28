"""HACK-016B — append-safe dynamic run with durable per-call checkpoints.

Each potentially billed call is recorded before dispatch, and its response
is independently checked before advancing. Never retry uncertain requests.
"""
import json
from pathlib import Path
from council import SPARK,WONDER,meta_call
from verification import verify_submission,evidence_hash

SCHEMA = """You are a FAITH scientific analytical perspective, not a human stakeholder.
Return ONLY one valid JSON object. No markdown, code fences, explanations or extra fields.
Its four REQUIRED keys and their shapes are:
{
 "observations": [{"evidence_id":"COPY_ID","finding":"COPY_EXACT_FINDING"}],
 "hypotheses": ["une hypothèse incertaine en français"],
 "investigations": ["une investigation proposée en français"],
 "abstentions": ["une conclusion impossible avec ces preuves, en français"]
}
For observations COPY the exact finding string AND evidence_id from the evidence list
supplied in this request, character-for-character. Include at least one matching
observation. Do not paraphrase observations, not even to translate them.
You may summarize uncertainties and proposals in French, but these are NOT verified facts.
Never invent data or attribute causal mining impact or population exposure to
WorldCover or WorldPop. Do not claim field validation or official approval.
The input may contain missing_topics: these topics have NO supporting measurements.
Every investigation must respond to THIS question; critique the earlier agents
when those verified publications are in your input. Preserve disagreement.
Keep the result concise to minimize truncation. If a requested claim is unsupported,
put it in abstentions, not observations.
"""

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
      "plan_sha256":plan.get("plan_sha256"),
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
