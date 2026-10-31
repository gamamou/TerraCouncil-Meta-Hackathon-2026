"""Read-only diagnostic for an existing HACK016 debate. No model or TTS calls.

Usage: python -X utf8 tools/check_boke_voice_ready.py ROOT [SESSION_ID]
ROOT: the private server output folder containing Dynamic-HACK016.
Only derived flags and hashes are printed; no scientific transcript is printed.
"""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from dynamic_narration import build_dynamic_oral
from dynamic_oral_audit import verify_oral
from scientific_pronunciation import spoken_pronunciation

DEFAULT_ID="HACK016-20261029T001224-8479e1c5"

def diagnose(out_dir,run_id=DEFAULT_ID):
    import re
    if not re.fullmatch(r"HACK016-[A-Za-z0-9_-]{10,80}",run_id):
        raise ValueError("Invalid session ID")
    source=Path(out_dir)/"Dynamic-HACK016"/(run_id+".json")
    if not source.is_file() or source.stat().st_size>3000000:
        return {"session_id":run_id,"state":"PRIVATE_SESSION_NOT_FOUND",
                "searched_directory":str(source.parent),"provider_calls":0}
    trace=json.loads(source.read_text(encoding="utf-8"))
    if trace.get("run_id")!=run_id:
        raise ValueError("Session identity mismatch")
    draft=build_dynamic_oral(trace)
    audit=verify_oral(trace,draft)
    if audit.get("status")!="EXACT_EXTRACTION_CHECK_PASSED":
        return {"session_id":run_id,"state":"SOURCE_AUDIT_BLOCKED",
                "audit_status":audit.get("status"),"provider_calls":0}
    results=[]
    for item in draft["turns"]:
        try:
            result=spoken_pronunciation(item["text_to_review"])
            results.append({"turn":item["turn"],"model":item["source_model"],
                            "status":"READY","characters":len(result["spoken_text"]),
                            "normalizations":len(result["normalizations"])})
        except ValueError as error:
            results.append({"turn":item["turn"],"model":item["source_model"],
                            "status":"NEEDS_ADAPTATION","reason":str(error)})
    n=sum(x.get("characters",0) for x in results)
    all_ready=all(x["status"]=="READY" for x in results) and n<=2000
    return {"session_id":run_id,"state":"READY_FOR_VOICE_CONSENT" if all_ready else "ORAL_ADAPTATION_NEEDED",
            "source_audit":audit["status"],"turn_count":len(results),
            "total_characters":n,"max_characters":2000,"turns":results,
            "scientific_validation":"STRUCTURAL_ONLY_NOT_FIELD_VALIDATED",
            "provider_calls":0}

if __name__=="__main__":
    if len(sys.argv) not in (2,3):
        sys.exit("Usage: python tools/check_boke_voice_ready.py OUTPUT_DIR [SESSION_ID]")
    result=diagnose(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else DEFAULT_ID)
    print(json.dumps(result,ensure_ascii=False,indent=2))
