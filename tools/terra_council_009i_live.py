"""TERRA-COUNCIL-009I — guarded Muse execution of approved 009H exploratory roster.

Offline by default. Requires explicit --execute --authorize-meta.
Scientific review required; never grants project authorization or audio approval.
"""
import argparse, hashlib, json, os
from pathlib import Path
from terra_council_009d_muse import request_muse, check_response

def validate(plan, manifest):
    if plan.get("schema") != "TERRA_COUNCIL_009H_COMPOSITION_V1":
        raise ValueError("Expected 009H plan")
    if manifest.get("schema") != "TERRA_COUNCIL_009F_EVIDENCE_V1":
        raise ValueError("Expected 009F manifest")
    if plan.get("decision_authorized") is not False or manifest.get("decision_authorized") is not False:
        raise ValueError("Decision gate invalid")
    if plan.get("question") != manifest.get("question"):
        raise ValueError("Question mismatch")
    if manifest.get("scientific_status") != "EXPLORATORY_DISCUSSION_ONLY":
        raise ValueError("Non-exploratory manifest")
    if manifest.get("human_review_required") is not True:
        raise ValueError("Human review flag missing")
    claims=manifest.get("claims",[])
    if not claims or any(c.get("admissibility") != "ADMISSIBLE_FOR_EXPLORATORY_DEBATE"
                         or c.get("decision_admissibility") != "NOT_ADMISSIBLE_FOR_DECISION"
                         or c.get("original_validation_status") != "SCREENED_NOT_FIELD_VALIDATED"
                         for c in claims):
        raise ValueError("Unadmitted evidence")
    ids=[c["evidence_id"] for c in claims]
    if len(ids)!=len(set(ids)) or set(ids)!={e["evidence_id"] for e in plan.get("evidence",[])}:
        raise ValueError("Evidence IDs mismatch")
    roles=plan.get("active_experts",[])
    steps=plan.get("steps",[])
    if not roles or len(steps)!=2*len(roles)+3:
        raise ValueError("Unexpected debate length")
    expected=[{"role":"scientific_chair","phase":"opening"}]
    expected += [{"role":r,"phase":"position"} for r in roles]
    expected += [{"role":"scientific_chair","phase":"cross_examination"}]
    expected += [{"role":r,"phase":"rebuttal_and_revision"} for r in roles]
    expected += [{"role":"scientific_chair","phase":"deliberation"}]
    if steps!=expected: raise ValueError("Invalid chair or debate sequence")
    return set(ids)

def run(plan, manifest, output, key, model, fingerprint):
    allowed=validate(plan,manifest)
    output=Path(output)
    if output.exists():raise FileExistsError("Prior attempt exists: no repeat")
    output.parent.mkdir(parents=True,exist_ok=True)
    turns=[]
    with output.open("x",encoding="utf-8") as f:
        json.dump({"schema":"TERRA_COUNCIL_009I_V1","status":"ATTEMPT_STARTED",
                   "source_sha256":fingerprint,"turns":[]},f)
    for n,step in enumerate(plan["steps"],1):
        context=dict(plan)
        context["question"]=plan["question"] + (
            "\nMANDAT STRICT: examen exploratoire des investigations et garanties; "
            "pas de constat d'exposition, de causalité minière, de conformité ESG, "
            "ni d'autorisation. WorldCover 2021 n'établit aucune tendance 2026. "
            "Président: poser des questions rigoureuses, sans fabriquer de désaccord.")
        try:
            candidate=request_muse(step,context,turns,key,model)
            response=check_response(candidate,step,allowed)
            turns.append(response)
            status="IN_PROGRESS"
        except Exception as exc:
            status="STOP_REVIEW_NO_RETRY"
            output.write_text(json.dumps({"schema":"TERRA_COUNCIL_009I_V1",
              "status":status,"steps_completed":len(turns),"turns":turns,
              "source_sha256":fingerprint,"error_type":type(exc).__name__,
              "http_status":getattr(exc,"code",None),
              "scientific_review_required":True,"decision_authorized":False,
              "audio_authorized":False},ensure_ascii=False,indent=2),encoding="utf-8")
            raise SystemExit("Appel interrompu. Consulter le journal; ne pas relancer aveuglément.")
        output.write_text(json.dumps({"schema":"TERRA_COUNCIL_009I_V1",
          "status":status,"steps_completed":n,"steps_total":len(plan["steps"]),
          "turns":turns,"source_sha256":fingerprint,
          "scientific_review_required":True,"decision_authorized":False,
          "audio_authorized":False},ensure_ascii=False,indent=2),encoding="utf-8")
        print(f"INTERVENTION {n}/{len(plan['steps'])}: {step['role']} - {step['phase']}",flush=True)
    record=json.loads(output.read_text(encoding="utf-8"))
    record["status"]="SCIENTIFIC_REVIEW_REQUIRED"
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
    print("DEBAT PRODUIT - REVUE SCIENTIFIQUE REQUISE",flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plan",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--authorize-meta",action="store_true")
    a=p.parse_args()
    raw_plan=Path(a.plan).read_bytes()
    raw_manifest=Path(a.manifest).read_bytes()
    plan=json.loads(raw_plan.decode("utf-8-sig"))
    manifest=json.loads(raw_manifest.decode("utf-8-sig"))
    validate(plan,manifest)
    print(json.dumps({"status":"VALIDATED_PREVIEW","experts":plan["active_experts"],
          "planned_muse_calls":len(plan["steps"]),"actual_muse_calls":0,
          "elevenlabs_calls":0,"decision_authorized":False},ensure_ascii=False),flush=True)
    if not a.execute:return
    if not a.authorize_meta:raise SystemExit("Explicit --authorize-meta required")
    key=os.environ.get("META_API_KEY") or os.environ.get("META_AI_API_KEY")
    if not key:raise SystemExit("Meta API key missing in this terminal")
    fingerprint=hashlib.sha256(raw_plan+b"\n"+raw_manifest).hexdigest()
    run(plan,manifest,a.output,key,a.model,fingerprint)
if __name__=="__main__":main()
