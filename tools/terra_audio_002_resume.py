"""Resume ElevenLabs from preserved Meta oral script; never calls Meta.
New output directory mandatory. No automatic retries. Offline preview by default.
"""
import argparse,hashlib,json,os
from pathlib import Path
from urllib import request,error
from tools.terra_audio_002_live import parse_dialogue,chunks,POLICY

URL="https://api.elevenlabs.io/v1/text-to-dialogue"

def prepare(source, voices, model, language="fr"):
    source=Path(source)
    doc=json.loads((source/"internal_oral_script.json").read_text(encoding="utf-8-sig"))
    turns=parse_dialogue(doc["raw_meta_output"])
    grouped=chunks(turns)
    return turns,[{"inputs":[{"text":t["text"],"voice_id":voices[t["speaker"]]} for t in g],
        "model_id":model,"language_code":language} for g in grouped]

def convert(payload,key,transport=None):
    body=json.dumps(payload,ensure_ascii=False).encode("utf-8")
    req=request.Request(URL,data=body,method="POST",headers={
        "xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"})
    transport=transport or request.urlopen
    try:
        with transport(req,timeout=120) as response:
            audio=response.read()
            if not audio:raise RuntimeError("Empty ElevenLabs audio")
            return audio
    except error.HTTPError as e:
        body=e.read(8192).decode("utf-8","replace")
        try: body=json.dumps(json.loads(body),ensure_ascii=False)
        except ValueError: pass
        raise RuntimeError(f"ElevenLabs HTTP {e.code}: {body[:1300]}") from None
    except error.URLError as e:raise RuntimeError("ElevenLabs network error") from None

def resume(source,output,key,voices,model="eleven_v4",execute=False,tts=convert,language="fr"):
    turns,payloads=prepare(source,voices,model,language)
    info={"status":"PREVIEW_NO_API_CALLS","source":str(source),"model":model,"language":language,
        "turn_count":len(turns),"chunks":len(payloads),"characters":sum(len(x["text"]) for x in turns),
        "audio_policy":POLICY,"audio_segments":[]}
    if not execute:return info
    root=Path(output)
    if root.exists():raise FileExistsError("New output directory required; do not overwrite")
    root.mkdir(parents=True)
    manifest=root/"audio_manifest.json"
    def save():manifest.write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    info["status"]="GENERATING_NO_AUTORETRY";save()
    for idx,payload in enumerate(payloads,1):
        info["pending"]="ELEVENLABS_CHUNK_"+str(idx);save()
        try:
            audio=tts(payload,key)
            if len(audio)<100:raise RuntimeError("Audio response too small")
            name="council_audio_%02d.mp3"%idx
            (root/name).write_bytes(audio)
            info["audio_segments"].append({"file":name,"sha256":hashlib.sha256(audio).hexdigest(),
                 "bytes":len(audio)})
            save()
        except Exception as e:
            info["status"]="INTERRUPTED_DO_NOT_AUTORETRY"
            info["error_message"]=str(e)[:1450]
            save()
            return info
    info.pop("pending",None);info["status"]="AUDIO_GENERATED_UNREVIEWED";save()
    return info

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,help="Existing failed AUDIO-002 directory containing internal_oral_script.json")
    p.add_argument("--output-dir",required=True)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--model",choices=["eleven_v4","eleven_v3"],default="eleven_v4")
    a=p.parse_args()
    voices={"spark":os.environ.get("ELEVENLABS_SPARK_VOICE_ID"),
        "wonder":os.environ.get("ELEVENLABS_WONDER_VOICE_ID")}
    if not all(voices.values()):raise SystemExit("Missing voice IDs")
    key=os.environ.get("ELEVENLABS_API_KEY")
    if a.execute and not key:raise SystemExit("Missing ELEVENLABS_API_KEY")
    result=resume(a.source,a.output_dir,key,voices,a.model,a.execute)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result["status"]=="INTERRUPTED_DO_NOT_AUTORETRY":raise SystemExit(2)
if __name__=="__main__":main()
