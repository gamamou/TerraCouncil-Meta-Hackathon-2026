"""TERRA-COUNCIL-009F: HACK016 scientific evidence admissibility, offline.

Screened findings may support a question about investigations, never a
site-specific approval, regulatory compliance or established mine impact.
No evidence status is promoted to VERIFIED.
"""
import argparse, hashlib, json
from pathlib import Path

EXPLORATORY = "ADMISSIBLE_FOR_EXPLORATORY_DEBATE"
CONTEXT = "CONTEXT_ONLY"
BLOCKED = "NOT_ADMISSIBLE_FOR_DECISION"

def adapt_session(session, raw_sha256):
    if not isinstance(session, dict) or not session.get("run_id"):
        raise ValueError("HACK016 session required")
    if session.get("human_review_required") is not True:
        raise ValueError("Expected explicit human review flag")
    snapshot=session.get("evidence_snapshot")
    if not isinstance(snapshot,list) or not snapshot:
        raise ValueError("Missing evidence snapshot")
    findings=[]
    ids=set()
    for item in snapshot:
        if not isinstance(item,dict):
            raise ValueError("Malformed evidence")
        required=("evidence_id","dataset","source","observed_at",
                  "method","validation_status","provenance","finding","usage")
        if any(not item.get(k) for k in required):
            raise ValueError("Missing mandatory scientific metadata")
        eid=item["evidence_id"]
        if eid in ids:raise ValueError("Duplicate evidence ID")
        ids.add(eid)
        if item["validation_status"]!="SCREENED_NOT_FIELD_VALIDATED" or item["usage"]!="exploratory_only":
            raise ValueError("Unknown evidence status; manual review")
        findings.append({
            "evidence_id":eid,"dataset":item["dataset"],"source":item["source"],
            "source_version":str(item["dataset"]),"observed_at":item["observed_at"],
            "method":item["method"],"finding":item["finding"],
            "provenance":item["provenance"],"original_validation_status":item["validation_status"],
            "admissibility":EXPLORATORY,"decision_admissibility":BLOCKED,
            "limitations":"Screening only; not field-validated or mine-specific causation"
        })
    context=[]
    for row in session.get("regional_context",[]):
        if not isinstance(row,dict) or not row.get("evidence_id"):
            raise ValueError("Invalid regional context")
        context.append({"evidence_id":row["evidence_id"],"admissibility":CONTEXT,
                        "original_validation_status":row.get("validation_status"),
                        "coverage_relation":row.get("coverage_relation"),
                        "claim":row.get("claim"),"source":row.get("source_url") or row.get("source_path")})
    return {"schema":"TERRA_COUNCIL_009F_EVIDENCE_V1",
        "run_id":session["run_id"],"question":session.get("question"),
        "session_source_sha256":raw_sha256,"reported_evidence_sha256":session.get("evidence_sha256"),
        "scientific_status":"EXPLORATORY_DISCUSSION_ONLY",
        "human_review_required":True,"decision_authorized":False,
        "claims":findings,"context_only":context,
        "limitations":["No site-specific exposure established","No mine-caused impact established",
                       "No regulatory or ESG compliance determination",
                       "Historical 2021 land cover is not a 2026 trend"],
        "meta_calls":0,"elevenlabs_calls":0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--session",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    raw=Path(a.session).read_bytes()
    result=adapt_session(json.loads(raw.decode("utf-8-sig")),hashlib.sha256(raw).hexdigest())
    dest=Path(a.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":result["scientific_status"],
       "exploratory_findings":len(result["claims"]),
       "context_only":len(result["context_only"]),
       "decision_authorized":False,"output":str(dest)},ensure_ascii=False))
if __name__=="__main__":main()
