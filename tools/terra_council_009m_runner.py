"""009M — execute 009K agenda with Muse. No TTS, no automatic retries."""
import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from meta_scientific_dialogue_004 import meta_call

RULES = """Tu incarnes uniquement le role et la phase demandes.
Renvoie JSON strict: {"role":"...","phase":"...","text":"...","evidence_ids":[]}.
Respecte max_words. Dialogue direct, court, vivant et scientifique.
Reponds aux vraies positions deja exprimees; aucun conflit invente.
Aucun chiffre, fait, impact, conformite ESG ou causalite non appuyes.
Donnees uniquement exploratoires; aucune autorisation miniere.
Le president presente les experts, interroge et conclut avec les
priorites, arbitrages, conditions et incertitudes."""
def validate(agenda):
    if agenda.get("schema")!="TERRA_COUNCIL_009K_AGENDA_V1":
        raise ValueError("Wrong agenda")
    if agenda.get("decision_authorized") is not False:
        raise ValueError("Decision guard")
    steps=agenda.get("steps",[])
    if len(steps)!=19 or steps[0]["role"]!="scientific_chair" or steps[-1]["phase"]!="decision_brief":
        raise ValueError("Wrong sequence")
    if not agenda.get("evidence_ids"):
        raise ValueError("Evidence references missing")
    return steps

def check(result,step,allowed):
    if result.get("role")!=step["role"] or result.get("phase")!=step["phase"]:
        raise ValueError("Unexpected speaker/phase")
    spoken=result.get("text","")
    refs=result.get("evidence_ids",[])
    if not isinstance(spoken,str) or not spoken.strip() or len(spoken.split())>step["max_words"]:
        raise ValueError("Speech is empty or oversized")
    if not isinstance(refs,list) or any(x not in allowed for x in refs):
        raise ValueError("Invalid evidence references")
    if step["role"]!="scientific_chair" and not refs:
        raise ValueError("Expert lacks evidence reference")
    return {"role":step["role"],"phase":step["phase"],"topic":step.get("topic"),
            "text":spoken,"evidence_ids":refs}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--agenda",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--source",required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--authorize-meta",action="store_true")
    a=p.parse_args()
    agenda=json.loads(Path(a.agenda).read_text(encoding="utf-8-sig"))
    steps=validate(agenda)
    manifest=json.loads(Path(a.manifest).read_text(encoding="utf-8-sig"))
    source=json.loads(Path(a.source).read_text(encoding="utf-8-sig"))
    if manifest.get("schema")!="TERRA_COUNCIL_009F_EVIDENCE_V1" or manifest.get("decision_authorized") is not False:
        raise ValueError("Exploratory 009F manifest required")
    if source.get("schema")!="TERRA_COUNCIL_009I_V1" or source.get("status")!="SCIENTIFIC_REVIEW_REQUIRED":
        raise ValueError("Completed 009I debate required")
    claims=manifest.get("claims",[])
    ids={c.get("evidence_id") for c in claims if c.get("admissibility")=="ADMISSIBLE_FOR_EXPLORATORY_DEBATE" and c.get("original_validation_status")=="SCREENED_NOT_FIELD_VALIDATED"}
    if not claims or len(ids)!=len(claims) or ids!=set(agenda["evidence_ids"]):
        raise ValueError("Exploratory evidence mismatch")
    if manifest.get("question")!=agenda.get("question"):
        raise ValueError("Question mismatch")
    scientific_context=[{"evidence_id":c["evidence_id"],"finding":c["finding"],
                         "limitations":c.get("limitations"),"method":c.get("method"),
                         "admissibility":c["admissibility"]} for c in claims]
    print(json.dumps({"status":"READY","steps":len(steps),"meta_calls":0,"audio_calls":0}),flush=True)
    if not a.execute:return
    if not a.authorize_meta:raise SystemExit("--authorize-meta required")
    if not (os.environ.get("META_API_KEY") or os.environ.get("META_AI_API_KEY")):
        raise SystemExit("Meta API key not configured")
    output=Path(a.output)
    if output.exists():raise SystemExit("Output exists; do not retry")
    output.parent.mkdir(parents=True,exist_ok=True)
    turns=[]
    with output.open("x",encoding="utf-8") as f:
        json.dump({"status":"STARTED","turns":[]},f)
    for n,step in enumerate(steps,1):
        state={"schema":"TERRA_COUNCIL_009M_V1","status":"CALL_IN_FLIGHT",
               "step":n,"turns":turns,"decision_authorized":False,
               "audio_authorized":False,"scientific_review_required":True}
        output.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        try:
            data={"question":agenda["question"],"agents":agenda["active_experts"],
                  "evidence":scientific_context,"step":step,"prior":turns,
                  "source_009I_relevant":[{"role":t["role"],"phase":t["phase"],"text":t["text"][:600]}
                    for t in source["turns"] if t["role"]==step["role"]][-2:]}
            answer=meta_call(a.model,RULES,data)
            turns.append(check(answer,step,set(agenda["evidence_ids"])))
        except Exception as error:
            state["status"]="STOP_DO_NOT_RETRY"
            state["error_type"]=type(error).__name__
            output.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
            raise SystemExit("Stopped: inspect request history before rerun")
        state.update({"status":"IN_PROGRESS","turns":turns})
        output.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        print("TURN",n,"/",len(steps),step["role"],step["phase"],flush=True)
    state["status"]="SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED"
    output.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    print("19 turns completed. Scientific review required.")
if __name__=="__main__":main()
