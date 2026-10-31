"""TERRA-META-012I: 19-turn deterministic voice routing and readiness report.
Offline, no paid calls, does not approve edits or science. Never overwrite files.
"""
import argparse,hashlib,json
from pathlib import Path
ROLES=("president","mining","environment","agriculture","communities","esg")
def make(council, voices):
 if council.get("schema")!="TERRA_META_011A_COUNCIL_CONSOLIDATION_V1":raise ValueError("Invalid council schema")
 if voices.get("schema")!="TERRA_META_012H_CONFIRMED_ROLE_VOICES" or voices.get("status")!="USER_CONFIRMED_MAPPING":raise ValueError("Confirmed role registry required")
 mapping=voices["roles"]
 if set(mapping)!=set(ROLES) or len(set(x["voice_id"] for x in mapping.values()))!=6:raise ValueError("Exactly six distinct role voices required")
 rows=council.get("turns",[])
 if len(rows)!=19 or [x.get("turn") for x in rows]!=list(range(1,20)):raise ValueError("Expected ordered 19 turns")
 out=[]
 for t in rows:
  role=t["role"];raw=t["spoken_text"]
  digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
  if role not in mapping or digest!=t["oral_sha256"]:raise ValueError("Scientific source integrity mismatch")
  out.append({"turn":t["turn"],"role":role,"speaker":mapping[role]["name"],"voice_id":mapping[role]["voice_id"],
   "text_sha256":digest,"review_gate":"FLAGGED_EDIT_AND_HUMAN_REVIEW" if t["alert_count"] else "HUMAN_EDITORIAL_REVIEW",
   "audio_status":"NOT_GENERATED","source_text_included":False})
 return {"schema":"TERRA_META_012I_VOICE_ROUTING_V1","status":"REVIEW_REQUIRED_NO_AUDIO",
 "scientific_approval":False,"tts_authorized":False,"provider_calls":0,"turn_count":len(out),
 "flagged_turns":[x["turn"] for x in out if x["review_gate"].startswith("FLAGGED")],"turns":out}
def main():
 p=argparse.ArgumentParser();p.add_argument("--council",required=True);p.add_argument("--voices",required=True);p.add_argument("--output",required=True)
 a=p.parse_args();target=Path(a.output)
 if target.exists():raise SystemExit("Output exists. No overwrite.")
 obj=make(json.loads(Path(a.council).read_text(encoding="utf-8-sig")),json.loads(Path(a.voices).read_text(encoding="utf-8-sig")))
 target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("x",encoding="utf8") as f:json.dump(obj,f,ensure_ascii=False,indent=2)
 print("ROUTING_READY",len(obj["turns"]),"turns; flagged",obj["flagged_turns"])
 for row in obj["turns"]:print(f"T{row['turn']:02d}: {row['speaker']} | {row['review_gate']}")
 print("AUDIO_GENERATED 0; ELEVENLABS_CALLS 0; HUMAN_REVIEW_REQUIRED")
if __name__=="__main__":main()
