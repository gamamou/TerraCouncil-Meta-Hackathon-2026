"""010D6B: non-destructive scientific alert triage for a flagged oral turn.

Candidate classifications are editorial hypotheses, NOT adjudications.
Leaves raw Spark audit intact; flagged speech remains out of model context.
"""
import argparse,json,hashlib
from pathlib import Path
from terra_council_010d_pipeline import read
from terra_council_010d6_runner import output,digest

def classify(msg):
 s=msg.lower()
 if "question" in s or "interrogative" in s:
  return "RESEARCH_QUESTION_CANDIDATE"
 if "methodolog" in s or "cartographie de classes" in s:
  return "METHODOLOGICAL_EXPLANATION_CANDIDATE"
 if "ne prouve" in s or "pas prouve" in s:
  return "NEGATIVE_EVIDENCE_LIMIT_CANDIDATE"
 return "UNCLASSIFIED_REQUIRES_HUMAN_ASSESSMENT"

def triage(root,turn):
 oral=read(output(root,turn,"oral"));audit=read(output(root,turn,"audit"))
 if oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED":
  raise ValueError("Human review pending records required")
 if oral.get("source_sha256")!=audit.get("source_sha256") or audit.get("oral_sha256")!=digest(oral.get("spoken_text","")):
  raise ValueError("Source or speech hash mismatch")
 alerts=audit.get("unsupported_additions",[])
 if not isinstance(alerts,list):raise ValueError("Invalid audit additions")
 return {"schema":"TERRA_COUNCIL_010D6B_ALERT_TRIAGE_V1",
  "status":"HUMAN_CLASSIFICATION_REQUIRED","turn":turn,
  "source_sha256":oral["source_sha256"],"oral_sha256":audit["oral_sha256"],
  "audit_preserved":True,"alerts":[{"text":msg,"candidate_type":classify(msg),
    "review_status":"NOT_ADJUDICATED"} for msg in alerts],
  "unresolved_critical_omissions":audit.get("critical_omissions",[]),
  "unresolved_numerical_mutations":audit.get("numerical_mutations",[]),
  "approved_for_conversational_reuse":False,
  "scientific_approval":False,"audio_authorized":False,"decision_authorized":False}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--workdir",required=True)
 p.add_argument("--turn",type=int,default=6)
 p.add_argument("--output",required=True)
 a=p.parse_args()
 result=triage(a.workdir,a.turn)
 with Path(a.output).open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":result["status"],"alerts":len(result["alerts"]),
  "classifications":[x["candidate_type"] for x in result["alerts"]],
  "approved_for_conversational_reuse":False,"audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
