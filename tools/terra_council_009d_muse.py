"""009D Muse execution: one role-specific call per planned turn; no TTS."""
import argparse, json, os, hashlib, urllib.request
from pathlib import Path

ENDPOINT="https://api.meta.ai/v1/chat/completions"

def validate_plan(plan):
    if plan.get("schema")!="TERRA_COUNCIL_009C_EXECUTION_PLAN_V1":
        raise ValueError("Invalid 009C plan")
    if plan.get("status")!="PREVIEW_REVIEW_REQUIRED" or not plan.get("evidence"):
        raise ValueError("Reviewable evidence plan required")
    if any(e.get("evidence_status")!="VERIFIED" for e in plan["evidence"]):
        raise ValueError("Unverified evidence")
    steps=plan.get("steps",[])
    if len(steps)<3 or steps[0]!={"role":"scientific_chair","phase":"opening"} or steps[-1]!={"role":"scientific_chair","phase":"deliberation"}:
        raise ValueError("Missing chair opening or conclusion")
    return {e["evidence_id"] for e in plan["evidence"]}

def check_response(response,step,ids):
    if not isinstance(response,dict) or response.get("role")!=step["role"] or response.get("phase")!=step["phase"]:
        raise ValueError("Role/phase mismatch")
    if not isinstance(response.get("text"),str) or not response["text"].strip():
        raise ValueError("No speech")
    refs=response.get("evidence_ids",[])
    if not isinstance(refs,list) or not set(refs).issubset(ids):
        raise ValueError("Unknown scientific evidence reference")
    if step["role"]!="scientific_chair" and not refs:
        raise ValueError("Expert must cite evidence")
    return {"role":step["role"],"phase":step["phase"],"text":response["text"],"evidence_ids":refs}

def request_muse(step,plan,prior,key,model):
    system=("Tu joues seulement le rôle assigné dans un conseil scientifique. "
            "Débat vigoureux mais jamais théâtral. Aucune invention de résultats, "
            "désaccords ou citations. Distingue faits, hypothèses et incertitudes. "
            "Réponds aux interventions précédentes. Le président introduit les "
            "experts et prononce une conclusion respectant les désaccords. "
            "Retourne exclusivement JSON: role, phase, text, evidence_ids.")
    user={"step":step,"question":plan["question"],"experts":plan["active_experts"],
          "evidence":plan["evidence"],"previous_turns":prior}
    body={"model":model,"temperature":0.2,"messages":[
      {"role":"system","content":system},
      {"role":"user","content":json.dumps(user,ensure_ascii=False)}]}
    req=urllib.request.Request(ENDPOINT,method="POST",
        data=json.dumps(body,ensure_ascii=False).encode("utf-8"),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=150) as resp:
        data=json.load(resp)
    raw=data["choices"][0]["message"]["content"]
    if isinstance(raw,list):
        raw="".join(part.get("text","") for part in raw if isinstance(part,dict))
    if not isinstance(raw,str):
        raise ValueError("Unexpected Meta content")
    raw=raw.strip()
    if raw.startswith("```"):
        raw=raw.split("\n",1)[1].rsplit("```",1)[0].strip()
    return json.loads(raw)

def execute(plan,output,key,model):
    ids=validate_plan(plan)
    output=Path(output)
    if output.exists(): raise FileExistsError("Existing attempt; no retry")
    output.parent.mkdir(parents=True,exist_ok=True)
    steps=plan["steps"]
    turns=[]
    with output.open("x",encoding="utf-8") as f:
        json.dump({"status":"ATTEMPT_STARTED","steps_total":len(steps)},f)
    for index,step in enumerate(steps,1):
        try:
            result=check_response(request_muse(step,plan,turns,key,model),step,ids)
            turns.append(result)
        except Exception as exc:
            failure={"schema":"TERRA_COUNCIL_009D_V1","status":"STOP_REVIEW_NO_RETRY",
                     "completed":len(turns),"turns":turns,"error_type":type(exc).__name__,
                     "http_status":getattr(exc,"code",None)}
            output.write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding="utf-8")
            raise RuntimeError("Step failed; check logs and existing attempt before retry") from None
        output.write_text(json.dumps({"schema":"TERRA_COUNCIL_009D_V1",
          "status":"IN_PROGRESS","completed":index,"turns":turns,
          "scientific_review":False,"audio_authorized":False},ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"STEP {index}/{len(steps)}: {step['role']} {step['phase']}",flush=True)
    record=json.loads(output.read_text(encoding="utf-8"))
    record["status"]="SCIENTIFIC_REVIEW_REQUIRED"
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--authorize-meta",action="store_true")
    args=p.parse_args()
    plan=json.loads(Path(args.plan).read_text(encoding="utf-8-sig"))
    validate_plan(plan)
    if not args.execute:
        print(json.dumps({"status":"PREVIEW_ONLY","planned_meta_calls":len(plan["steps"]),
                          "actual_meta_calls":0,"elevenlabs_calls":0}))
        return
    if not args.authorize_meta:raise SystemExit("Explicit Meta authorization required")
    key=os.environ.get("META_API_KEY") or os.environ.get("META_AI_API_KEY")
    if not key:raise SystemExit("META_API_KEY missing")
    execute(plan,args.output,key,args.model)

if __name__=="__main__":main()
