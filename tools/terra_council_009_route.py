"""TERRA-COUNCIL-009: deterministic scientific routing gate (offline, no API calls).

Muse may propose a route later; this gate validates it against the declared
agent/capability registries. All evidence remains NOT VERIFIED until the
respective FAITH/FSDC adapters return provenance-bearing material.
"""
import argparse
import json
from pathlib import Path

AGENTS = {
    "mining": {"label": "Mines", "terms": ("mine", "minier", "bauxite", "permis", "résidu minier", "simandou")},
    "environment": {"label": "Environnement", "terms": ("environnement", "eau", "pollution", "poussière", "inondation", "biodiversité", "climat")},
    "agriculture": {"label": "Agriculture", "terms": ("agriculture", "agricole", "culture", "riz", "irrigation", "sols cultivés")},
    "energy": {"label": "Énergie", "terms": ("énergie", "électricité", "solaire", "réseau électrique")},
    "esg": {"label": "ESG", "terms": ("esg", "durabilité", "social", "gouvernance", "conformité environnementale")},
    "communities": {"label": "Communautés", "terms": ("communauté", "communautés", "population", "déplacement", "santé publique")},
    "economy": {"label": "Économie", "terms": ("coût", "investissement", "rentabilité", "économique", "financement")},
}
CAPABILITIES = {
    "FMI_CPDM": {"domains": ("mining",), "status": "ADAPTER_NOT_CONNECTED"},
    "FSMI": {"domains": ("mining", "environment", "esg"), "status": "ADAPTER_NOT_CONNECTED"},
    "FEI": {"domains": ("environment",), "status": "ADAPTER_NOT_CONNECTED"},
    "FAI": {"domains": ("agriculture",), "status": "ADAPTER_NOT_CONNECTED"},
    "FCEI": {"domains": ("energy",), "status": "ADAPTER_NOT_CONNECTED"},
}
STOP_WORDS = ("intervention fictive",)

def propose_route(question, muse_proposal=None):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("A non-empty user question is required")
    q = question.casefold().strip()
    matched = {
        agent: [term for term in info["terms"] if term in q]
        for agent, info in AGENTS.items()
    }
    matched = {key: terms for key, terms in matched.items() if terms}
    if muse_proposal is not None:
        if not isinstance(muse_proposal, list) or any(x not in AGENTS for x in muse_proposal):
            raise ValueError("Muse selected an unknown agent")
        # No agent silently discarded when a domain is explicitly invoked.
        if not set(matched).issubset(set(muse_proposal)):
            raise ValueError("Muse omitted an explicitly relevant domain")
        selected = sorted(set(muse_proposal))
        routing_method = "MUSE_PROPOSAL_GATED"
    else:
        selected = sorted(matched)
        routing_method = "OFFLINE_KEYWORD_BASELINE_NOT_MUSE"
    needs_review = not selected or any(x in q for x in STOP_WORDS)
    capacity = {
        name: dict(status=data["status"], evidence_status="NO_EVIDENCE_LOADED")
        for name, data in CAPABILITIES.items()
        if set(data["domains"]) & set(selected)
    }
    return {
        "schema": "TERRA_COUNCIL_009_ROUTE_V1",
        "question_original": question,
        "question_reformulated": None,
        "question_review_required": needs_review,
        "routing_method": routing_method,
        "chair": "scientific_chair",
        "agents_selected": selected,
        "selection_reasons": {k: matched.get(k, ["Muse proposal; requires scientific review"]) for k in selected},
        "capabilities": capacity,
        "scientific_status": "NOT_EVIDENCE_VALIDATED",
        "brief_status": "NOT_AUTHORIZED",
        "audio_status": "NOT_AUTHORIZED",
        "next_step": "Connect and validate FAITH capabilities, obtain FSDC evidence, deliberate, review",
        "meta_calls": 0,
        "elevenlabs_calls": 0,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--question", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--muse-agents-json", help="Optional JSON list of Muse proposed agents")
    args = p.parse_args()
    proposal = json.loads(args.muse_agents_json) if args.muse_agents_json else None
    result = propose_route(args.question, proposal)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
