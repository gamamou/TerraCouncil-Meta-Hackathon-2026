"""AUDIO-002: per-session Meta oral adaptation -> ElevenLabs dialogue audio.
Explicit --execute only. No pre-recorded files, no exposed transcript UI.
No scientific validation claim: post-hackathon review documented internally.
"""
import argparse, json, os, hashlib
from pathlib import Path
from urllib import request, error
from council import meta_call, SPARK

URL="https://api.elevenlabs.io/v1/text-to-dialogue"
POLICY="HACKATHON_AUDIO_ADAPTATION_ACCEPTED_POST_HACKATHON_VALIDATION_REQUIRED"

def parse_dialogue(raw):
    if not isinstance(raw,str):raise ValueError("Meta must return text")
    text=raw.strip()
    if text.startswith("```"):
        lines=text.splitlines()
        text="\n".join(lines[1:-1]).strip()
    try: obj=json.loads(text)
    except json.JSONDecodeError:
        at=text.find("{")
        if at<0:raise ValueError("No dialogue JSON")
        obj,_=json.JSONDecoder().raw_decode(text[at:])
    turns=obj.get("dialogue") if isinstance(obj,dict) else None
    if not isinstance(turns,list) or not 2<=len(turns)<=24:raise ValueError("Expected 2..24 dialogue turns")
    aliases={
        "spark":"spark","muse spark":"spark","muse-spark-1.3":"spark",
        "scientific lead":"spark","spark — scientific lead":"spark",
        "wonder":"wonder","muse wonder":"wonder","muse-wonder-1.0":"wonder",
        "scientific critic":"wonder","wonder — scientific critic":"wonder",
        "expert":"wonder","scientific expert":"wonder",
        "modérateur":"spark","moderateur":"spark","moderator":"spark",
        "narrator":"spark","narrateur":"spark"
    }
    for t in turns:
        if not isinstance(t,dict):raise ValueError("Invalid dialogue turn")
        original=t.get("speaker")
        speaker=aliases.get(str(original).strip().lower())
        # The hackathon uses two available voices. Unknown model-authored expert
        # labels are voiced by Wonder, without changing the original spoken text.
        # Preserve original role internally for scientific provenance.
        if not speaker:
            if not isinstance(original,str) or not original.strip():
                raise ValueError("Missing speaker label")
            speaker="wonder"
        if speaker!=str(original).strip().lower():
            t["original_speaker"]=original
        t["speaker"]=speaker
        if not isinstance(t.get("text"),str) or not 1<=len(t["text"])<=1900:raise ValueError("Invalid turn text")
    if len({t["speaker"] for t in turns}) < 2:
        raise ValueError("DEBATE_SINGLE_VOICE: Meta generated only one distinct voice; no ElevenLabs call made")
    return turns

def chunks(turns, max_chars=1900):
    result=[];current=[];count=0
    for t in turns:
        size=len(t["text"])
        if size>max_chars:raise ValueError("Single turn exceeds dialogue chunk")
        if current and count+size>max_chars:
            result.append(current);current=[];count=0
        current.append(t);count+=size
    if current:result.append(current)
    return result

def eleven_convert(inputs,key,model="eleven_v3"):
    body=json.dumps({"inputs":inputs,"model_id":model},ensure_ascii=False).encode("utf8")
    req=request.Request(URL,data=body,method="POST",headers={
        "xi-api-key":key,"Content-Type":"application/json","Accept":"audio/mpeg"})
    try:
        with request.urlopen(req,timeout=120) as response:return response.read()
    except error.HTTPError as exc:raise RuntimeError("ElevenLabs HTTP "+str(exc.code)) from None
    except error.URLError:raise RuntimeError("ElevenLabs connection error") from None

def adapt(trace,key,caller=meta_call):
    stages={x.get("stage"):x.get("response") for x in trace["steps"]}
    if trace.get("status")!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":raise ValueError("Incomplete council trace")
    if not stages.get("SPARK_REVISION") or not stages.get("WONDER_CRITIQUE"):
        raise ValueError("Missing council interventions")
    instruction=("Convert the following council into a natural French two-voice oral conversation. "+
        "Return ONLY JSON {\\\"dialogue\\\":[{\\\"speaker\\\":\\\"spark\\\",\\\"text\\\":\\\"...\\\"},...]} . "+
        "Use simple spoken language, no technical identifiers or jargon where unnecessary. "+
        "Preserve material uncertainty and disagreement and do not invent science or claim approval. "+
        "Make the user's CURRENT question and geography the primary topic of every exchange. "+
        "Some FAITH results may concern unrelated sectors: when discussing climate, water, "+
        "agriculture or biodiversity, do NOT retell mining permit inventories, rankings, "+
        "solution IDs, or site selection unless the current question explicitly asks for them "+
        "and they are geographically relevant. If only mining data were consulted, say briefly "+
        "that local evidence for the requested domains is unavailable and explain the conditional "+
        "multisector recommendation; never imply those mining data prove local conditions. "+
        "Keep the main counterarguments and actionable staged recommendations for the asked domain. "+
        "Every dialogue MUST include at least one spark intervention and one wonder intervention. "+
        "Write distinct turns with both labels, alternating where natural; do not narrate all objections as one speaker. "+
        "Use 6 to 12 short alternating turns, maximum 1800 characters per grouped audio chunk; "+
        "keep total dialogue ideally under 3500 characters. No heading or markdown.")
    return caller(SPARK,instruction,{"question":trace.get("question"),
        "wonder_critique":stages["WONDER_CRITIQUE"],"spark_revision":stages["SPARK_REVISION"]},key)

def run(session,output,meta_key,eleven_key,voices,meta=meta_call,tts=eleven_convert):
    folder=Path(output)
    if folder.exists():raise FileExistsError("Output already exists")
    trace=json.loads((Path(session)/"01_trace.json").read_text(encoding="utf-8-sig"))
    folder.mkdir(parents=True)
    state={"status":"STARTED_DO_NOT_AUTORETRY","audio_policy":POLICY,
           "source_session":Path(session).name,"audio_segments":[]}
    def save():(folder/"audio_manifest.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf8")
    save()
    try:
        state["pending"]="META_ORAL_ADAPTATION";save()
        raw=adapt(trace,meta_key,meta)
        (folder/"internal_oral_script.json").write_text(json.dumps({"raw_meta_output":raw},ensure_ascii=False,indent=2),encoding="utf8")
        turns=parse_dialogue(raw)
        state["dialogue_sha256"]=hashlib.sha256(json.dumps(turns,ensure_ascii=False).encode()).hexdigest()
        state["turn_count"]=len(turns)
        for i,group in enumerate(chunks(turns),1):
            inputs=[{"text":t["text"],"voice_id":voices[t["speaker"]]} for t in group]
            state["pending"]="ELEVENLABS_CHUNK_"+str(i);save()
            audio=tts(inputs,eleven_key)
            if not isinstance(audio,bytes) or len(audio)<100:raise ValueError("Empty audio response")
            name="council_audio_%02d.mp3"%i
            (folder/name).write_bytes(audio)
            state["audio_segments"].append({"file":name,"bytes":len(audio),"sha256":hashlib.sha256(audio).hexdigest()})
            save()
        state.pop("pending",None);state["status"]="AUDIO_GENERATED_UNREVIEWED";save()
    except Exception as exc:
        state["status"]="INTERRUPTED_DO_NOT_AUTORETRY"
        state["error_type"]=type(exc).__name__;state["error_message"]=str(exc)[:180];save()
    return state

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--session",required=True);p.add_argument("--output-dir",required=True)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--spark-voice",default=os.environ.get("ELEVENLABS_SPARK_VOICE_ID"))
    p.add_argument("--wonder-voice",default=os.environ.get("ELEVENLABS_WONDER_VOICE_ID"))
    a=p.parse_args()
    if not a.execute:
        print(json.dumps({"status":"PREVIEW_NO_API_CALLS","session":a.session,
            "endpoint":URL,"requires":["MODEL_API_KEY","ELEVENLABS_API_KEY",
            "ELEVENLABS_SPARK_VOICE_ID","ELEVENLABS_WONDER_VOICE_ID"]},ensure_ascii=False,indent=2))
        return
    keys=[os.environ.get("MODEL_API_KEY"),os.environ.get("ELEVENLABS_API_KEY"),a.spark_voice,a.wonder_voice]
    if not all(keys):raise SystemExit("Missing Meta/ElevenLabs credentials or voice ids")
    state=run(a.session,a.output_dir,keys[0],keys[1],{"spark":keys[2],"wonder":keys[3]})
    print(json.dumps({"status":state["status"],"segments":state["audio_segments"],
      "output":a.output_dir},ensure_ascii=False))
    if state["status"]!="AUDIO_GENERATED_UNREVIEWED":raise SystemExit(2)
if __name__=="__main__":main()
