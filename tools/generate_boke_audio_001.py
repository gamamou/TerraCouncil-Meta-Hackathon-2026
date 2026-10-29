"""Execute the source-audited Boké dialogue in four individually claimed ElevenLabs batches.

DRY RUN is default. Requires --send and --approve-cost-and-sharing to dispatch.
No automatic retries. Every attempted batch gets a permanent claim before POST.
Original session is read-only. Do not run again if any claim exists: inspect first.
"""
import argparse,base64,hashlib,json,os,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_narration import build_dynamic_oral
from scientific_pronunciation import spoken_pronunciation
from terra_voice_segmentation_001 import segment_spoken_turns
from inspect_boke_audio_plan import assess
from render_session_audio import ENDPOINT
from terra_agent_voice_registry_001 import load_voice_map, voice_mapping_template

def run(args):
    source=Path(args.session)
    trace=json.loads(source.read_text(encoding="utf-8"))
    audit=assess(trace)
    if audit["state"]!="SEGMENT_PLAN_READY_NOT_AUTHORIZED":
        raise ValueError("Source audit blocked: "+audit["state"])
    draft=build_dynamic_oral(trace)
    parsed=[{"spoken_text":spoken_pronunciation(t["text_to_review"])["spoken_text"]} for t in draft["turns"]]
    plan=segment_spoken_turns(parsed)
    if audit["plan_sha256"]!=plan["plan_sha256"]:
        raise ValueError("Source plan mismatch")
    print("SOURCE:",audit["session_id"],"BATCHES:",plan["batch_count"],"CHARACTERS:",plan["total_characters"])
    roles=[t["speaker"] for t in draft["turns"]]
    if args.print_voice_template:
        print(json.dumps(voice_mapping_template(roles),ensure_ascii=False,indent=2))
        return
    if not args.send:
        print("DRY_RUN; 0 paid calls; no data sent. To run requires explicit cost/sharing flags.")
        return
    if not args.approve_cost_and_sharing:
        raise ValueError("Must explicitly accept that text will be sent to ElevenLabs and may incur charges")
    if plan["batch_count"]>4:
        raise ValueError("Unexpected batch count: check changed plan and cost")
    key=os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise ValueError("Missing ELEVENLABS_API_KEY")
    if not args.voices:
        raise ValueError("Missing --voices JSON mapping for each scientific role")
    role_voices=load_voice_map(args.voices,roles)
    output=Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    identity=hashlib.sha256((audit["session_id"]+plan["plan_sha256"]).encode()).hexdigest()[:12]
    sessiondir=output/("Boke-"+identity)
    sessiondir.mkdir(exist_ok=True)
    for batch in plan["batches"]:
        batch_id=batch["batch"]
        claim=sessiondir/f"batch-{batch_id:02d}.claim.json"
        audio=sessiondir/f"batch-{batch_id:02d}.mp3"
        timing=sessiondir/f"batch-{batch_id:02d}.timing.json"
        if claim.exists() or audio.exists() or timing.exists():
            raise ValueError(f"Batch {batch_id}: existing attempt or output; no retry.")
        payload_inputs=[]
        for item in batch["inputs"]:
            turn=draft["turns"][item["turn"]-1]
            voice=role_voices[turn["speaker"]]
            payload_inputs.append({"text":item["text"],"voice_id":voice})
        payload={"inputs":payload_inputs,"model_id":"eleven_v4","language_code":"fr"}
        with claim.open("x",encoding="utf-8") as f:
            json.dump({"state":"ATTEMPT_STARTED_DO_NOT_RETRY","batch":batch_id,
                       "session_id":audit["session_id"],"plan_sha256":plan["plan_sha256"]},f)
        try:
            request=urllib.request.Request(ENDPOINT,method="POST",
                data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
                headers={"xi-api-key":key,"Content-Type":"application/json"})
            with urllib.request.urlopen(request,timeout=180) as response:
                answer=json.load(response)
            audio_bytes=base64.b64decode(answer["audio_base64"],validate=True)
            segments=answer["voice_segments"]
            if len(audio_bytes)<1000 or not isinstance(segments,list) or not segments:
                raise ValueError("Incomplete provider response")
            for seg in segments:
                index=seg.get("dialogue_input_index")
                if not isinstance(index,int) or not 0<=index<len(payload_inputs):
                    raise ValueError("Invalid timing index")
            audio.write_bytes(audio_bytes)
            timing.write_text(json.dumps({
                "session_id":audit["session_id"],"batch":batch_id,
                "turns":[x["turn"] for x in batch["inputs"]],
                "scientific_validation":"STRUCTURAL_ONLY_NOT_FIELD_VALIDATED",
                "script_sha256":audit["script_sha256"],
                "source_fingerprint":audit["source_fingerprint"],
                "plan_sha256":plan["plan_sha256"],
                "audio_sha256":hashlib.sha256(audio_bytes).hexdigest(),
                "voice_segments":segments},ensure_ascii=False,indent=2),encoding="utf-8")
            claim.write_text(json.dumps({"state":"READY","batch":batch_id,
                "plan_sha256":plan["plan_sha256"]}),encoding="utf-8")
            print("CREATED",audio)
        except Exception as exc:
            claim.write_text(json.dumps({"state":"FAILED_OR_INDETERMINATE_DO_NOT_RETRY",
                "batch":batch_id,"error_type":type(exc).__name__,
                "note":"Inspect ElevenLabs usage and local output; never blindly retry."}),encoding="utf-8")
            raise
    print("DONE; 4 MP3 FILES:",sessiondir)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--session",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--send",action="store_true")
    p.add_argument("--voices",help="Private role-to-voice-ID JSON file")
    p.add_argument("--print-voice-template",action="store_true")
    p.add_argument("--approve-cost-and-sharing",action="store_true")
    a=p.parse_args()
    try:run(a)
    except Exception as e:
        print("STOP:",type(e).__name__,str(e)[:240],file=sys.stderr)
        sys.exit(2)
