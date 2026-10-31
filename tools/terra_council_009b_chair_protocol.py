"""TERRA-COUNCIL-009B — chair-led council protocol, offline scientific gate.

This prepares a debate plan only. It NEVER simulates expert findings or sends
requests to Muse/ElevenLabs. All scientific statements require evidence binding.
"""
import argparse, json
from pathlib import Path

PHASES = (
    "chair_opening",
    "expert_introductions",
    "initial_positions",
    "cross_examination",
    "expert_rebuttals",
    "position_revisions",
    "chair_deliberation",
)
REQUIRED_KEYS = ("evidence_id", "source_version", "claim", "evidence_status")
ALLOWED_STATUS = {"VERIFIED", "LIMITED", "UNAVAILABLE"}

def assemble_protocol(route, evidence=None):
    if route.get("schema") != "TERRA_COUNCIL_009_ROUTE_V1":
        raise ValueError("Route 009 required")
    experts = route.get("agents_selected", [])
    if len(experts) != len(set(experts)) or not isinstance(experts, list):
        raise ValueError("Invalid expert list")
    evidence = evidence or []
    for item in evidence:
        if not isinstance(item, dict) or any(k not in item for k in REQUIRED_KEYS):
            raise ValueError("Evidence must contain provenance, version and status")
        if item["evidence_status"] not in ALLOWED_STATUS:
            raise ValueError("Invalid evidence status")
    verified = [e for e in evidence if e["evidence_status"] == "VERIFIED"]
    opening = {
        "speaker": "scientific_chair",
        "question_original": route["question_original"],
        "reformulation": route.get("question_reformulated"),
        "experts_to_introduce": experts,
        "instruction": "Read the user's question accurately; disclose unresolved ambiguities."
    }
    rules = [
        "No fabricated findings, quotes, consensus, or source numbers",
        "Disagree on interpretations only with referenced scientific evidence",
        "Chair challenges weak arguments and requests specific responses",
        "No theatrical hostility, insults, or invented disputes",
        "Preserve dissent and allow explicit revision or abstention",
        "Chair does not overrule a scientific objection",
        "Claims without verified evidence remain unresolved"
    ]
    return {
        "schema": "TERRA_COUNCIL_009B_PROTOCOL_V1",
        "scientific_status": "READY_FOR_MODEL_DEBATE" if verified and experts else "BLOCKED_EVIDENCE_OR_EXPERTS",
        "execution_status": "PLAN_ONLY_NOT_EXECUTED",
        "chair_opening": opening,
        "phases": list(PHASES),
        "chair_role": "scientific_chair",
        "active_experts": experts,
        "evidence_ids_verified": [e["evidence_id"] for e in verified],
        "rules": rules,
        "debate_turns": [],
        "decision_brief_status": "NOT_GENERATED",
        "audio_status": "NOT_GENERATED",
        "meta_calls": 0,
        "elevenlabs_calls": 0,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--route", required=True)
    p.add_argument("--evidence", help="Optional FSDC evidence manifest JSON")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    route = json.loads(Path(args.route).read_text(encoding="utf-8-sig"))
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8-sig")) if args.evidence else []
    result = assemble_protocol(route, evidence)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": result["scientific_status"], "phases": len(PHASES),
                      "agents": result["active_experts"], "output": str(dest),
                      "meta_calls": 0, "elevenlabs_calls": 0}, ensure_ascii=False))

if __name__ == "__main__":
    main()
