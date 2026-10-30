"""TERRA-META-012F: propose six distinct available ElevenLabs voices.
No API call, no token, no scientific approval; never overwrite an existing registry.
"""
import argparse,json
from pathlib import Path
VOICES={
 "president":{"voice_id":"5l4ttmr4SKNgi0HnOelT","name":"Paul K — Deep French Narrator"},
 "mining":{"voice_id":"cEjGxRhK5rId1bacJPJr","name":"Bakumba — Clear, Deep"},
 "environment":{"voice_id":"ojsdYNTmnPdf7yAl8rI5","name":"Loïc — French calm"},
 "agriculture":{"voice_id":"4SFJvuIUvxaPLgk8FoK3","name":"Alimata — Professional"},
 "communities":{"voice_id":"TrvjhxOWz4IB9qYry8Lb","name":"Joel Labo — Friendly"},
 "esg":{"voice_id":"MmLmgmAm7pKFUJBu1Lov","name":"Mélodie"}
}
def main():
 p=argparse.ArgumentParser();p.add_argument("--output",required=True);a=p.parse_args()
 dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():raise SystemExit("Existing registry not overwritten")
 if len({v["voice_id"] for v in VOICES.values()})!=6:raise ValueError("Duplicate voice ID")
 obj={"schema":"TERRA_META_012F_VOICE_PROPOSAL","status":"PROPOSED_REQUIRES_USER_LISTENING_APPROVAL",
 "source":"ElevenLabs voices listing supplied by user 2026-10-30",
 "historical_selection_verified":False,"tts_authorized":False,"roles":VOICES}
 with dest.open("x",encoding="utf-8") as f:json.dump(obj,f,ensure_ascii=False,indent=2)
 print("VOICE_PROPOSAL_READY",dest)
 for role,entry in VOICES.items():print(role, "=>",entry["name"],entry["voice_id"])
 print("NO_AUDIO_GENERATED; NO_API_CALLS; HUMAN_APPROVAL_REQUIRED")
if __name__=="__main__":main()
