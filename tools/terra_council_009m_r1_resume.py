"""009M-R1: safe continuation of an interrupted 009M dialogue.

Creates NEW journal; preserves original failed journal. Never retries automatically.
Each raw response is persisted before validation, so rejected answers can be reviewed.
"""
import argparse,json,os,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from terra_council_009m_runner import validate,check,RULES
from meta_scientific_dialogue_004 import meta_call

def preflight(agenda,old,manifest,source):
    steps=validate(agenda)
    if old.get("schema")!="TERRA_COUNCIL_009M_V1" or old.get("status")!="STOP_DO_NOT_RETRY":
        raise ValueError("Stopped 009M journal required")
    turns=old.get("turns",[])
    if not turns or old.get("step")!=len(turns)+1:
        raise ValueError("Journal step is inconsistent")
    if manifest.get("schema")!="TERRA_COUNCIL_009F_EVIDENCE_V1" or manifest.get("decision_authorized") is not False:
        raise ValueError("009F exploratory manifest required")
    if source.get("schema")!="TERRA_COUNCIL_009I_V1" or source.get("status")!="SCIENTIFIC_REVIEW_REQUIRED":
        raise ValueError("Reviewed 009I source required")
    claims=manifest.get("claims",[])
    ids={c.get("evidence_id") for c in claims if c.get("admissibility")=="ADMISSIBLE_FOR_EXPLORATORY_DEBATE" and c.get("original_validation_status")=="SCREENED_NOT_FIELD_VALIDATED"}
    if not claims or len(ids)!=len(claims) or ids!=set(agenda["evidence_ids"]):
        raise ValueError("FSDC evidence IDs/status mismatch")
    if manifest.get("question")!=agenda.get("question"):
        raise ValueError("Question mismatch")
    for n,(turn,step) in enumerate(zip(turns,steps),1):
        try:check(turn,step,ids)
        except ValueError as exc:raise ValueError(f"Saved turn {n}: {exc}") from exc
    return steps,ids,turns

def main():
    p=argparse.ArgumentParser()
    for name in ("agenda","journal","manifest","source","output"):p.add_argument("--"+name,required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--authorize-meta",action="store_true")
    a=p.parse_args()
    read=lambda path:json.loads(Path(path).read_text(encoding="utf-8-sig"))
    agenda,journal,manifest,source=map(read,(a.agenda,a.journal,a.manifest,a.source))
    steps,ids,turns=preflight(agenda,journal,manifest,source)
    next_step=len(turns)+1
    print(json.dumps({"status":"SAFE_RESUME_PREVIEW","completed":len(turns),
      "next_step":next_step,"remaining":len(steps)-len(turns),
      "calls_now":0,"prior_failed_call_may_have_been_billed":True},ensure_ascii=False),flush=True)
    if not a.execute:return
    if not a.authorize_meta:raise SystemExit("Explicit --authorize-meta required")
    if not (os.environ.get("META_API_KEY") or os.environ.get("META_AI_API_KEY")):
        raise SystemExit("Meta key missing")
    out=Path(a.output)
    if out.exists():raise SystemExit("Output already exists - no retry or overwrite")
    out.parent.mkdir(parents=True,exist_ok=True)
    initial_sha=hashlib.sha256(Path(a.journal).read_bytes()).hexdigest()
    turns=list(turns)
    with out.open("x",encoding="utf-8") as f:
        json.dump({"status":"RESUME_INITIALIZED","previous_journal_sha256":initial_sha,
                   "turns":turns},f)
    evidence=[{"evidence_id":c["evidence_id"],"finding":c["finding"],
               "method":c.get("method"),"limitations":c.get("limitations"),
               "admissibility":c["admissibility"]} for c in manifest["claims"]]
    for n in range(next_step,len(steps)+1):
        step=steps[n-1]
        state={"schema":"TERRA_COUNCIL_009M_R1_V1","status":"CALL_IN_FLIGHT",
               "step":n,"turns":turns,"previous_journal_sha256":initial_sha,
               "decision_authorized":False,"audio_authorized":False,
               "scientific_review_required":True}
        out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        data={"question":agenda["question"],"agents":agenda["active_experts"],
              "evidence":evidence,"step":step,"prior":turns,
              "source_009I_relevant":[{"role":t["role"],"phase":t["phase"],
                "text":t["text"][:600]} for t in source["turns"]
                if t["role"]==step["role"]][-2:]}
        try:
            raw=meta_call(a.model,RULES,data)
            # Separate immutable raw artifact BEFORE validation.
            raw_path=out.with_name(out.stem+f"-raw-turn-{n:02d}.json")
            with raw_path.open("x",encoding="utf-8") as f:
                json.dump(raw,f,ensure_ascii=False,indent=2)
            state["raw_response_path"]=str(raw_path)
            out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
            accepted=check(raw,step,ids)
        except Exception as exc:
            state["status"]="STOP_REVIEW_REQUIRED_NO_RETRY"
            state["error_type"]=type(exc).__name__
            state["error_message"]=str(exc)[:500]
            out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
            raise SystemExit("Stopped. Inspect journal and raw response before any additional request.")
        turns.append(accepted)
        state.update({"status":"IN_PROGRESS","turns":turns})
        out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"TURN {n}/{len(steps)} {step['role']} {step['phase']}",flush=True)
    state["status"]="SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED"
    out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    print("19 turns complete; human review still required.")
if __name__=="__main__":main()
