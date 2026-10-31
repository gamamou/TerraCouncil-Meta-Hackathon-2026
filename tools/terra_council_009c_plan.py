"""009C: compile an auditable Muse council execution plan; no network or TTS."""
import argparse
import json
from pathlib import Path
from terra_council_009b_chair_protocol import assemble_protocol

SCHEMA = "TERRA_COUNCIL_009C_EXECUTION_PLAN_V1"

def compile_plan(route, evidence):
    protocol = assemble_protocol(route, evidence)
    if protocol["scientific_status"] != "READY_FOR_MODEL_DEBATE":
        raise ValueError("FSDC evidence is required before a live debate")
    if route.get("question_review_required"):
        raise ValueError("Question requires clarification")
    admissible = [e for e in evidence if e["evidence_status"] == "VERIFIED"]
    if len(admissible) != len(evidence):
        raise ValueError("Mixed evidence statuses require prior review")
    if len(set(e["evidence_id"] for e in admissible)) != len(admissible):
        raise ValueError("Duplicate evidence IDs")
    roles = protocol["active_experts"]
    steps = [{"role":"scientific_chair","phase":"opening"}]
    steps.extend({"role":role,"phase":"position"} for role in roles)
    steps.append({"role":"scientific_chair","phase":"cross_examination"})
    steps.extend({"role":role,"phase":"rebuttal_and_revision"} for role in roles)
    steps.append({"role":"scientific_chair","phase":"deliberation"})
    return {
        "schema": SCHEMA, "question": route["question_original"],
        "active_experts": roles, "steps": steps,
        "evidence": admissible, "status": "PREVIEW_REVIEW_REQUIRED",
        "scientific_review_required": True,
        "muse_calls_executed": 0, "elevenlabs_calls_executed": 0,
        "audio_authorized": False, "pdf_authorized": False,
        "rules": protocol["rules"],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--route",required=True)
    parser.add_argument("--evidence",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    route=json.loads(Path(args.route).read_text(encoding="utf-8-sig"))
    evidence=json.loads(Path(args.evidence).read_text(encoding="utf-8-sig"))
    result=compile_plan(route,evidence)
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("x",encoding="utf-8") as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2)
    print(json.dumps({"status":result["status"],
                      "steps":len(result["steps"]),
                      "experts":result["active_experts"],
                      "output":str(target),
                      "muse_calls_executed":0},ensure_ascii=False))

if __name__=="__main__":
    main()
