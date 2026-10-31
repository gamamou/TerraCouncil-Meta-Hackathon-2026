"""009N — offline audit of completed 009M dialogue. No LLM or audio calls."""
import argparse,collections,hashlib,json,re
from pathlib import Path
def audit(debate,agenda):
 turns=debate.get("turns",[])
 steps=agenda.get("steps",[])
 if len(turns)!=19 or len(steps)!=19:raise ValueError("Expected 19 turns")
 issues=[];flags=[];stats=[]
 evidence=set(agenda.get("evidence_ids",[]))
 if debate.get("status")!="SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED":
  issues.append("UNEXPECTED_FINAL_STATUS")
 if debate.get("decision_authorized") is not False or debate.get("audio_authorized") is not False:
  issues.append("AUTHORIZATION_GATE_INVALID")
 for i,(t,s) in enumerate(zip(turns,steps),1):
  if (t.get("role"),t.get("phase"))!=(s.get("role"),s.get("phase")):
   issues.append(f"TURN_{i}_ROLE_PHASE")
  words=len(t.get("text","").split())
  if words==0 or words>s["max_words"]:issues.append(f"TURN_{i}_WORD_LIMIT")
  ids=t.get("evidence_ids",[])
  if not isinstance(ids,list) or not set(ids).issubset(evidence):
   issues.append(f"TURN_{i}_UNKNOWN_REFERENCE")
  if not ids and t.get("role")!="scientific_chair":
   flags.append(f"TURN_{i}_METHODOLOGY_WITHOUT_DATA_REFERENCE_REVIEW")
  if i in (16,18):
   flags.append(f"TURN_{i}_RECOVERED_RESPONSE_REVIEW")
  stats.append({"turn":i,"role":t.get("role"),"phase":t.get("phase"),
    "words":words,"source_refs":len(ids) if isinstance(ids,list) else 0,
    "recovery_status":t.get("review_status")})
 conclusion=turns[-1].get("text","")
 for token,desc in (("priorit","PRIORITIES"),("incert","UNCERTAINTIES"),
                     ("condition","CONDITIONS"),("arbitrag","TRADEOFFS")):
  if token not in conclusion.casefold():flags.append("CHAIR_FINAL_"+desc+"_REVIEW")
 return {"schema":"TERRA_COUNCIL_009N_AUDIT_V1",
  "status":"BLOCKED_FOR_REVIEW" if issues else "HUMAN_SCIENTIFIC_REVIEW_REQUIRED",
  "turns":19,"roles":dict(collections.Counter(t.get("role") for t in turns)),
  "total_words":sum(x["words"] for x in stats),
  "issues":issues,"review_flags":flags,"turn_details":stats,
  "scientific_approval":False,"audio_authorized":False,
  "decision_authorized":False,"api_calls":0}
def main():
 p=argparse.ArgumentParser()
 for k in ("debate","agenda","output"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 source=Path(a.debate).read_bytes()
 debate=json.loads(source.decode("utf-8-sig"))
 agenda=json.loads(Path(a.agenda).read_text(encoding="utf-8-sig"))
 result=audit(debate,agenda)
 result["source_sha256"]=hashlib.sha256(source).hexdigest()
 with Path(a.output).open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":result["status"],"turns":result["turns"],
  "issues":result["issues"],"review_flags":result["review_flags"],
  "output":a.output,"api_calls":0},ensure_ascii=False))
if __name__=="__main__":main()
