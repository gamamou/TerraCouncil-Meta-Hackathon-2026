"""Offline source-bound preflight for multi-segment Boké narration.

Does not invoke the existing single-call synthesis endpoint. No paid actions.
Retains exact-source audit and permits only the overall single-call budget
exception after verifying the actual segmented plan.
"""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_narration import build_dynamic_oral
from dynamic_oral_audit import verify_oral
from scientific_pronunciation import spoken_pronunciation
from terra_voice_segmentation_001 import segment_spoken_turns

def assess(trace):
    draft=build_dynamic_oral(trace)
    audited=verify_oral(trace,draft)
    ordinary_errors=[]
    for item in audited["checks"]:
        if item.get("issue")=="SINGLE_CALL_CHARACTER_LIMIT":
            continue
        if item.get("classification")!="EXTRACTIVE_PASS":
            ordinary_errors.append({"turn":item.get("turn"),"issues":item.get("issues")})
    if ordinary_errors:
        return {"state":"REVIEW_REQUIRED","issues":ordinary_errors,"provider_calls":0}
    turns=[{"spoken_text":spoken_pronunciation(t["text_to_review"])["spoken_text"]}
           for t in draft["turns"]]
    plan=segment_spoken_turns(turns)
    return {"state":"SEGMENT_PLAN_READY_NOT_AUTHORIZED",
            "session_id":draft["session_id"],"source_fingerprint":draft["evidence_sha256"],
            "script_sha256":audited["script_sha256"],"plan_sha256":plan["plan_sha256"],
            "turn_count":len(turns),"characters":plan["total_characters"],
            "batch_count":plan["batch_count"],
            "batches":[{"batch":b["batch"],"turns":[i["turn"] for i in b["inputs"]],
                        "characters":sum(len(i["text"]) for i in b["inputs"])}
                       for b in plan["batches"]],
            "tts_authorized":False,"provider_calls":0,
            "note":"Offline plan only. No paid multi-call dispatcher is enabled."}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: inspect_boke_audio_plan.py SESSION_JSON")
    trace=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(assess(trace),ensure_ascii=False,indent=2))
