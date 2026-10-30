"""TerraCouncil 012K: explicit user-requested draft listening of 19 source-faithful spoken turns.
NOT scientific approval, NOT final publication. Local API key. One-attempt ledger per turn.
"""
import argparse,json,os,hashlib,urllib.request,urllib.error,datetime
from pathlib import Path
def sha(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("--council",required=True);p.add_argument("--voices",required=True);p.add_argument("--app",required=True);p.add_argument("--output-dir",required=True);a=p.parse_args()
 key=os.getenv("ELEVENLABS_API_KEY","").strip()
 if not key:raise SystemExit("Clé ElevenLabs absente dans ce terminal PowerShell.")
 council=json.loads(Path(a.council).read_text(encoding="utf-8-sig"))
 voices=json.loads(Path(a.voices).read_text(encoding="utf-8-sig"))
 if council.get("schema")!="TERRA_META_011A_COUNCIL_CONSOLIDATION_V1" or len(council.get("turns",[]))!=19:raise SystemExit("Manifeste 011A invalide.")
 if voices.get("schema")!="TERRA_META_012H_CONFIRMED_ROLE_VOICES" or voices.get("status")!="USER_CONFIRMED_MAPPING":raise SystemExit("Registre des voix confirmé requis.")
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 web=Path(a.app)/"data"/"audio";web.mkdir(parents=True,exist_ok=True)
 available=[]
 for t in council["turns"]:
  n=t["turn"];role=t["role"];spoken=t["spoken_text"];voice=voices["roles"][role]["voice_id"]
  if sha(spoken)!=t["oral_sha256"]:raise SystemExit(f"T{n:02d} intégrité du texte incorrecte.")
  name=f"t{n:02d}-draft.mp3";audio=out/name;claim=out/f"t{n:02d}-attempt.json";dest=web/name
  if audio.is_file() and audio.stat().st_size>1024:
   if not dest.exists():dest.write_bytes(audio.read_bytes())
   available.append({"turn":n,"file":"audio/"+name,"voice_id":voice,"draft":True,"flagged":bool(t.get("alert_count"))})
   print("EXISTING",name);continue
  if claim.exists():
   print("SKIP_UNCERTAIN_ALREADY_ATTEMPTED",n);continue
  # exclusive journal created before spending money
  record={"turn":n,"voice_id":voice,"source_sha256":t["oral_sha256"],"status":"REQUEST_STARTED_DO_NOT_REPEAT","at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
  with claim.open("x",encoding="utf-8") as f:json.dump(record,f,ensure_ascii=False,indent=2)
  request=urllib.request.Request("https://api.elevenlabs.io/v1/text-to-speech/"+voice,
   data=json.dumps({"text":spoken,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.8}}).encode("utf8"),
   headers={"xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"},method="POST")
  try:
   with urllib.request.urlopen(request,timeout=120) as response:
    data=response.read()
   if len(data)<1024 or not (data.startswith(b"ID3") or data[:1]==b"\xff"):
    raise ValueError("Réponse audio invalide")
   with audio.open("xb") as f:f.write(data)
   dest.write_bytes(data)
   record.update({"status":"AUDIO_SAVED","audio_sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)})
   claim.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf8")
   available.append({"turn":n,"file":"audio/"+name,"voice_id":voice,"draft":True,"flagged":bool(t.get("alert_count"))})
   print("AUDIO_READY",f"T{n:02d}",len(data))
  except Exception as e:
   record["status"]="OUTCOME_UNCERTAIN_DO_NOT_RETRY"
   claim.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf8")
   print("STOP_API_ERROR",f"T{n:02d}",str(e)[:250])
   break
 manifest=Path(a.app)/"data"/"audio-draft.json"
 if manifest.exists():manifest.replace(manifest.with_suffix(".json.backup"))
 manifest.write_text(json.dumps({"status":"DRAFT_NOT_SCIENTIFICALLY_APPROVED","items":available,"nineteen_final_approved":False},ensure_ascii=False,indent=2),encoding="utf8")
 print("AUDIO_DRAFT_AVAILABLE",len(available),"/19","MANIFEST",manifest)
if __name__=="__main__":main()
