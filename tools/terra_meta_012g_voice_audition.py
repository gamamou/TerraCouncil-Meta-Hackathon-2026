"""TERRA-META-012G: explicitly authorized two-voice test (not scientific debate).
Call once per voice; atomic claim BEFORE API call to prevent inadvertent paid retries.
API key only from local environment. No secrets or real scientific transcripts in request.
"""
import argparse,json,os,urllib.request,urllib.error,datetime
from pathlib import Path
VOICES={
 "president":("5l4ttmr4SKNgi0HnOelT","Bonjour. Je suis le président scientifique de TerraCouncil. Notre mission est d'examiner les preuves et de distinguer clairement les faits des hypothèses."),
 "mining":("cEjGxRhK5rId1bacJPJr","Merci, Monsieur le Président. Pour le secteur minier, nous devons examiner la qualité des données, les limites de nos observations et les investigations nécessaires sur le terrain.")
}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output-dir",required=True);a=ap.parse_args()
 key=os.environ.get("ELEVENLABS_API_KEY","").strip()
 if not key:raise SystemExit("ELEVENLABS_API_KEY absent in this PowerShell session")
 base=Path(a.output_dir);base.mkdir(parents=True,exist_ok=True)
 print("Voice audition. Two separate short demo scripts, not 19-turn narration.")
 for role,(vid,txt) in VOICES.items():
  out=base/(role+"-012G-demo.mp3");claim=base/(role+"-012G-attempt.json")
  if claim.exists() or out.exists():
   print("SKIP_EXISTING_ATTEMPT",role)
   continue
  attempt={"role":role,"voice_id":vid,"status":"REQUEST_STARTED_NO_AUTORETRY","created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"demo_only":True}
  with claim.open("x",encoding="utf8") as f:json.dump(attempt,f,ensure_ascii=False,indent=2)
  url="https://api.elevenlabs.io/v1/text-to-speech/"+vid
  payload={"text":txt,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.55,"similarity_boost":0.75}}
  req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"},method="POST")
  try:
   with urllib.request.urlopen(req,timeout=60) as response:
    audio=response.read()
   if not audio.startswith(b"ID3") and not (len(audio)>3 and audio[:2]==b"\xff\xfb"):
    raise ValueError("Unexpected audio response; inspect without retry")
   with out.open("xb") as f:f.write(audio)
   attempt["status"]="AUDIO_SAVED";attempt["bytes"]=len(audio)
   claim.write_text(json.dumps(attempt,ensure_ascii=False,indent=2),encoding="utf8")
   print("AUDIO_READY",role,str(out),len(audio),"bytes")
  except Exception as exc:
   attempt["status"]="OUTCOME_UNCERTAIN_DO_NOT_RETRY"
   claim.write_text(json.dumps(attempt,ensure_ascii=False,indent=2),encoding="utf8")
   print("REQUEST_FAILED_NO_RETRY",role,type(exc).__name__,str(exc)[:180])
   break
if __name__=="__main__":main()
