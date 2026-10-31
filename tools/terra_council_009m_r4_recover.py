"""009M-R4: local, zero-API recovery package for the final Muse call."""
import json,argparse,hashlib
from pathlib import Path
def main():
 p=argparse.ArgumentParser()
 for n in ("agenda","journal","raw","output"):p.add_argument("--"+n,required=True)
 a=p.parse_args()
 agenda=json.loads(Path(a.agenda).read_text(encoding="utf-8-sig"))
 journal=json.loads(Path(a.journal).read_text(encoding="utf-8-sig"))
 raw_bytes=Path(a.raw).read_bytes()
 raw=json.loads(raw_bytes.decode("utf-8-sig"))
 steps=agenda.get("steps",[])
 turns=journal.get("turns",[])
 if agenda.get("schema")!="TERRA_COUNCIL_009K_AGENDA_V1" or len(steps)!=19:
  raise ValueError("Agenda mismatch")
 if journal.get("schema")!="TERRA_COUNCIL_009M_R3_V1" or journal.get("status")!="STOP_REVIEW_REQUIRED_NO_RETRY" or journal.get("step")!=18 or len(turns)!=17:
  raise ValueError("Expected R3 stopped at turn 18 with 17 saved turns")
 if (raw.get("role"),raw.get("phase"))!=("mining","response_to_prior"):
  raise ValueError("Raw speaker mismatch")
 if raw.get("evidence_ids")!=[] or not raw.get("text") or len(raw["text"].split())>120:
  raise ValueError("Raw turn outside methodological review")
 if steps[18].get("role")!="scientific_chair" or steps[18].get("phase")!="decision_brief":
  raise ValueError("Last turn must be chair")
 recovered={"role":"mining","phase":"response_to_prior",
   "topic":steps[17].get("topic"),"text":raw["text"],"evidence_ids":[],
   "review_status":"HUMAN_REVIEW_REQUIRED_METHODOLOGICAL"}
 result={"schema":"TERRA_COUNCIL_009M_R4_PREVIEW_V1",
  "status":"HUMAN_REVIEW_REQUIRED","turns":turns+[recovered],
  "next_step":19,"raw18_sha256":hashlib.sha256(raw_bytes).hexdigest(),
  "decision_authorized":False,"audio_authorized":False,"meta_calls":0}
 with Path(a.output).open("x",encoding="utf-8") as f:
  json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":result["status"],"preserved_turns":18,"next_step":19,"meta_calls":0}))
if __name__=="__main__":main()
