"""009O-B: Muse oral adaptation, one source turn per guarded execution."""
import argparse,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from meta_scientific_dialogue_004 import meta_call
RULES="""Tu es directeur oral scientifique. Reformule uniquement le texte source
dans un francais oral naturel, sans fait nouveau, sans nouvelle position,
sans inventer de desaccord. Conserve incertitudes et reserves.
Retourne JSON: {"role":"...","phase":"...","spoken_text":"..."}.
Le role et la phase doivent rester identiques. Pas de references FSDC prononcees."""
def main():
 p=argparse.ArgumentParser()
 for k in ("packets","output"):p.add_argument("--"+k,required=True)
 p.add_argument("--turn",required=True,type=int)
 p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 source=json.loads(Path(a.packets).read_text(encoding="utf-8-sig"))
 if source.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or source.get("audio_authorized") is not False:raise ValueError("Invalid packets")
 if len(source.get("turns",[]))!=19 or not 1<=a.turn<=19:raise ValueError("Invalid turn")
 item=source["turns"][a.turn-1]
 if item.get("turn")!=a.turn:raise ValueError("Turn order mismatch")
 print(json.dumps({"status":"PREVIEW","turn":a.turn,"meta_calls":0,"elevenlabs_calls":0}))
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit authorization needed")
 if not (os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta key missing")
 out=Path(a.output)
 if out.exists():raise SystemExit("Output exists; do not retry")
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT","turn":a.turn},f)
 try:
  response=meta_call("muse-wonder-1.0",RULES,{"role":item["speaker"],
   "phase":item["phase"],"source_text":item["scientific_source_text"]})
  raw=out.with_name(out.stem+"-raw.json")
  with raw.open("x",encoding="utf-8") as f:json.dump(response,f,ensure_ascii=False,indent=2)
  if response.get("role")!=item["speaker"] or response.get("phase")!=item["phase"] or not response.get("spoken_text"):
   raise ValueError("Invalid oral turn")
 except Exception as e:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","error":str(e)[:300],"turn":a.turn}),encoding="utf-8")
  raise SystemExit("Stopped; inspect raw and journal")
 out.write_text(json.dumps({"status":"SCIENTIFIC_REVIEW_REQUIRED","turn":a.turn,
  "spoken_text":response["spoken_text"],"source_text":item["scientific_source_text"],
  "source_evidence_ids":item.get("source_evidence_ids",[]),
  "audio_authorized":False},ensure_ascii=False,indent=2),encoding="utf-8")
 print("ORAL CANDIDATE SAVED; HUMAN REVIEW REQUIRED")
if __name__=="__main__":main()
