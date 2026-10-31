"""009M-R2: prepare a human-review recovery of stored ESG response, no API calls."""
import argparse,json,hashlib
from pathlib import Path
def main():
 p=argparse.ArgumentParser()
 for k in ("agenda","journal","raw","output"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 agenda=json.loads(Path(a.agenda).read_text(encoding="utf-8-sig"))
 journal=json.loads(Path(a.journal).read_text(encoding="utf-8-sig"))
 raw_bytes=Path(a.raw).read_bytes();raw=json.loads(raw_bytes.decode("utf-8-sig"))
 turns=journal.get("turns",[])
 if agenda.get("schema")!="TERRA_COUNCIL_009K_AGENDA_V1" or len(agenda.get("steps",[]))!=19:raise ValueError("Bad agenda")
 if journal.get("schema")!="TERRA_COUNCIL_009M_R1_V1" or journal.get("status")!="STOP_REVIEW_REQUIRED_NO_RETRY":raise ValueError("Bad stopped journal")
 if journal.get("step")!=16 or len(turns)!=15:raise ValueError("Expected fifteen saved turns and stopped step 16")
 step=agenda["steps"][15]
 if step["role"]!="esg" or step["phase"]!="response_to_prior":raise ValueError("Unexpected turn")
 if raw.get("role")!="esg" or raw.get("phase")!="response_to_prior":raise ValueError("Raw response mismatch")
 if not raw.get("text") or len(raw["text"].split())>step["max_words"]:raise ValueError("Length gate")
 if raw.get("evidence_ids")!=[]:raise ValueError("Expected uncited methodological response")
 proposal={"schema":"TERRA_COUNCIL_009M_R2_RECOVERY_REVIEW_V1",
  "status":"HUMAN_REVIEW_REQUIRED","next_step_after_approval":17,
  "saved_turns":15,"recovered_turn":{"role":"esg","phase":"response_to_prior",
     "topic":step.get("topic"),"text":raw["text"],"evidence_ids":[],
     "evidence_status":"METHODOLOGICAL_PROPOSAL_NO_NEW_EMPIRICAL_FACT"},
  "raw_sha256":hashlib.sha256(raw_bytes).hexdigest(),
  "editorial_flags":["Restrict access to personal raw data","Avoid absolute admissibility claims"],
  "approval":False,"decision_authorized":False,"audio_authorized":False,
  "meta_calls":0}
 with Path(a.output).open("x",encoding="utf-8") as f:json.dump(proposal,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":proposal["status"],"saved_turns":15,"recoverable_turn":16,"next_step_after_approval":17,"meta_calls":0},ensure_ascii=False))
if __name__=="__main__":main()
