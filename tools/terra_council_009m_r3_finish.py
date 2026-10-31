"""009M-R3: finish turns 17–19 after explicit review of recovered turn 16.

Never edits 009M/009M-R1 originals. New journal; raw before validation.
"""
import argparse,hashlib,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from terra_council_009m_runner import validate,check,RULES
from terra_council_009m_r1_resume import preflight
from meta_scientific_dialogue_004 import meta_call

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def assemble(agenda,original,restart,recovery,manifest,source):
    steps,ids,prior=preflight(agenda,original,manifest,source)
    if len(prior)!=7 or original.get("step")!=8:
        raise ValueError("Original must preserve seven turns")
    if restart.get("schema")!="TERRA_COUNCIL_009M_R1_V1":
        raise ValueError("R1 journal required")
    if restart.get("status")!="STOP_REVIEW_REQUIRED_NO_RETRY" or restart.get("step")!=16:
        raise ValueError("R1 must be stopped at 16")
    saved=restart.get("turns",[])
    if len(saved)!=15 or saved[:7]!=prior:
        raise ValueError("R1 must preserve first fifteen turns")
    for turn,step in zip(saved,steps):
        check(turn,step,ids)
    if recovery.get("schema")!="TERRA_COUNCIL_009M_R2_RECOVERY_REVIEW_V1":
        raise ValueError("R2 recovery required")
    if recovery.get("status")!="HUMAN_REVIEW_REQUIRED" or recovery.get("approval") is not False:
        raise ValueError("Unexpected recovery approval status")
    turn16=recovery["recovered_turn"]
    if turn16.get("evidence_status")!="METHODOLOGICAL_PROPOSAL_NO_NEW_EMPIRICAL_FACT":
        raise ValueError("Recovered turn not methodological")
    if turn16.get("role")!="esg" or turn16.get("phase")!="response_to_prior":
        raise ValueError("Wrong recovered turn")
    if turn16.get("evidence_ids")!=[] or not turn16.get("text","").strip():
        raise ValueError("Recovery evidence mismatch")
    if len(turn16["text"].split())>steps[15]["max_words"]:
        raise ValueError("Recovered response too long")
    return steps,ids,saved+[{"role":turn16["role"],"phase":turn16["phase"],
      "topic":turn16.get("topic"),"text":turn16["text"],"evidence_ids":[],
      "review_status":"REVIEWED_METHODOLOGICAL_NO_DATA_CLAIM"}]

def main():
    p=argparse.ArgumentParser()
    for k in ("agenda","original","restart","recovery","manifest","source","output"):
        p.add_argument("--"+k,required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--authorize-meta",action="store_true")
    p.add_argument("--approve-methodological-turn-16",action="store_true")
    a=p.parse_args()
    agenda,original,restart,recovery,manifest,source=map(load,
      (a.agenda,a.original,a.restart,a.recovery,a.manifest,a.source))
    steps,ids,turns=assemble(agenda,original,restart,recovery,manifest,source)
    print(json.dumps({"status":"R3_PREVIEW","saved_turns":15,
       "recovered_turn":16,"next_turn":17,"remaining_meta_calls":3,
       "calls_now":0,"human_approval_needed":True},ensure_ascii=False),flush=True)
    if not a.execute:return
    if not a.approve_methodological_turn_16:
        raise SystemExit("Explicit --approve-methodological-turn-16 required")
    if not a.authorize_meta:raise SystemExit("--authorize-meta required")
    if not (os.environ.get("META_API_KEY") or os.environ.get("META_AI_API_KEY")):
        raise SystemExit("Meta key missing")
    out=Path(a.output)
    if out.exists():raise SystemExit("R3 output already exists. Never retry blindly.")
    out.parent.mkdir(parents=True,exist_ok=True)
    prev_sha=hashlib.sha256(Path(a.restart).read_bytes()).hexdigest()
    with out.open("x",encoding="utf-8") as f:
        json.dump({"status":"INITIALIZED","turns":turns},f)
    evidence=[{"evidence_id":c["evidence_id"],"finding":c["finding"],
      "limitations":c.get("limitations"),"method":c.get("method")}
      for c in manifest["claims"]]
    for n in range(17,20):
        step=steps[n-1]
        state={"schema":"TERRA_COUNCIL_009M_R3_V1","status":"CALL_IN_FLIGHT",
          "step":n,"turns":turns,"previous_journal_sha256":prev_sha,
          "decision_authorized":False,"audio_authorized":False,
          "scientific_review_required":True}
        out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        data={"question":agenda["question"],"agents":agenda["active_experts"],
          "evidence":evidence,"step":step,"prior":turns,
          "source_009I_relevant":[{"role":t["role"],"phase":t["phase"],
            "text":t["text"][:600]} for t in source["turns"]
            if t["role"]==step["role"]][-2:]}
        try:
            answer=meta_call(a.model,RULES,data)
            raw_path=out.with_name(out.stem+f"-raw-turn-{n:02d}.json")
            with raw_path.open("x",encoding="utf-8") as f:
                json.dump(answer,f,ensure_ascii=False,indent=2)
            state["raw_response_path"]=str(raw_path)
            out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
            accepted=check(answer,step,ids)
        except Exception as exc:
            state.update({"status":"STOP_REVIEW_REQUIRED_NO_RETRY",
              "error_type":type(exc).__name__,"error_message":str(exc)[:400]})
            out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
            raise SystemExit("Stopped. Inspect journal/raw before any additional request.")
        turns.append(accepted)
        state.update({"status":"IN_PROGRESS","turns":turns})
        out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"TURN {n}/19 {step['role']} {step['phase']}",flush=True)
    state["status"]="SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED"
    out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    print("19 turns completed; full scientific review still required.")
if __name__=="__main__":main()
