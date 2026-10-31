"""Re-author oral conversation for an existing completed FAITH session.
No new scientific research. Optional ElevenLabs v4 with fresh files.
Do not overwrite prior oral or audio outputs.
"""
import argparse,json,os
from pathlib import Path
from datetime import datetime
from tools.terra_audio_002_live import adapt,parse_dialogue
from tools.terra_audio_002_resume import resume

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--session",required=True)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--audio",action="store_true")
    a=p.parse_args()
    root=Path(a.session)
    trace=root/"trace_working.json"
    if not trace.exists():trace=root/"artifacts"/"01_trace.json"
    if not trace.exists():raise SystemExit("No completed scientific trace for this session")
    if not a.execute:
        print(json.dumps({"mode":"PREVIEW_NO_API_CALLS","trace":str(trace),"new_science_calls":0,
            "meta_oral_calls":1,"elevenlabs":a.audio},ensure_ascii=False));return
    meta=os.environ.get("MODEL_API_KEY")
    if not meta:raise SystemExit("MODEL_API_KEY not configured")
    voices={"spark":os.environ.get("ELEVENLABS_SPARK_VOICE_ID"),
            "wonder":os.environ.get("ELEVENLABS_WONDER_VOICE_ID")}
    eleven=os.environ.get("ELEVENLABS_API_KEY")
    if a.audio and (not eleven or not all(voices.values())):raise SystemExit("ElevenLabs configuration missing")
    target=root/("oral_revised_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    target.mkdir()
    raw=adapt(json.loads(trace.read_text(encoding="utf-8-sig")),meta)
    (target/"internal_oral_script.json").write_text(json.dumps({"raw_meta_output":raw},ensure_ascii=False,indent=2),encoding="utf8")
    turns=parse_dialogue(raw)
    print(json.dumps({"status":"ORAL_REVISED","turns":len(turns),"folder":str(target)},ensure_ascii=False))
    if a.audio:
        output=root/("audio_revised_"+target.name.removeprefix("oral_revised_"))
        result=resume(target,output,eleven,voices,"eleven_v4",True)
        print(json.dumps({"status":result["status"],"folder":str(output),
            "error_message":result.get("error_message")},ensure_ascii=False))
        if result["status"]!="AUDIO_GENERATED_UNREVIEWED":raise SystemExit(2)
if __name__=="__main__":main()
