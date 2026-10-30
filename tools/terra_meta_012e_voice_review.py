"""TERRA-META-012E — prepare immutable, review-gated 19-turn voice manuscript.
Offline. No ElevenLabs calls, no auto-approval, originals unchanged.
"""
import argparse,json,hashlib
from pathlib import Path
def digest(text):return hashlib.sha256(text.encode("utf-8")).hexdigest()
ROLES=("president","mining","environment","agriculture","communities","esg")
def prepare(source):
 if source.get("schema")!="TERRA_META_011A_COUNCIL_CONSOLIDATION_V1":raise ValueError("Expected 011A consolidation")
 rows=source.get("turns")
 if not isinstance(rows,list) or len(rows)!=19 or [t.get("turn") for t in rows]!=list(range(1,20)):raise ValueError("Expected 19 ordered turns")
 result=[]
 for t in rows:
  text=t.get("spoken_text");role=t.get("role")
  if not isinstance(text,str) or not text.strip() or role not in ROLES or t.get("oral_sha256")!=digest(text):
   raise ValueError(f"Turn integrity mismatch: {t.get('turn')}")
  blocked=bool(t.get("alert_count")) or bool(t.get("alerts"))
  result.append({"turn":t["turn"],"role":role,"original_text":text,"original_sha256":digest(text),
   "candidate_text":text if not blocked else None,
   "status":"REVIEW_REQUIRED_ALERTS" if blocked else "REVIEW_REQUIRED_GENERAL",
   "unresolved_alerts":t.get("alerts",[]),"editorial_approved":False,
   "scientific_approved":False,"tts_authorized":False,"voice_id":None})
 return {"schema":"TERRA_META_012E_VOICE_REVIEW_V1","status":"HUMAN_REVIEW_REQUIRED",
  "source_schema":source["schema"],"turn_count":19,
  "flagged_turns":[r["turn"] for r in result if r["unresolved_alerts"]],
  "tts_authorized":False,"elevenlabs_calls":0,"audio_generated":False,"turns":result}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);ap.add_argument("--output",required=True)
 args=ap.parse_args();out=Path(args.output)
 if out.exists():raise SystemExit("Output exists; refuse overwrite")
 result=prepare(json.loads(Path(args.input).read_text(encoding="utf-8-sig")))
 with out.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":result["status"],"turns":19,"flagged_turns":result["flagged_turns"],
 "elevenlabs_calls":0,"tts_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
