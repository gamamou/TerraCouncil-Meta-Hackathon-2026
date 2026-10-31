"""009K: compile a short-turn, chair-led debate plan from a reviewed 009I run.

No synthetic debate text, network or audio. The source is preserved unchanged.
"""
import argparse, hashlib, json
from pathlib import Path

ROLES=("mining","environment","esg","communities","agriculture")
TOPICS=(
 ("sequencing","Prioriser les investigations en parallèle ou en séquence, en explicitant les dépendances"),
 ("water","Coordonner les mesures relatives à l'eau sans confondre leurs objets"),
 ("assurance","Définir les garanties ESG, la consultation et la revue indépendante"),
)
def compile_agenda(source,manifest):
    if source.get("schema")!="TERRA_COUNCIL_009I_V1" or source.get("status")!="SCIENTIFIC_REVIEW_REQUIRED":
        raise ValueError("Completed 009I review transcript required")
    turns=source.get("turns",[])
    expected=[("scientific_chair","opening")]+[(r,"position") for r in ROLES]+[("scientific_chair","cross_examination")]+[(r,"rebuttal_and_revision") for r in ROLES]+[("scientific_chair","deliberation")]
    if [(t.get("role"),t.get("phase")) for t in turns]!=expected:
        raise ValueError("Source roles/order do not match Boké session")
    allowed={c["evidence_id"] for c in manifest.get("claims",[]) if c.get("admissibility")=="ADMISSIBLE_FOR_EXPLORATORY_DEBATE"}
    if len(allowed)!=len(manifest.get("claims",[])) or not allowed:
        raise ValueError("Exploratory evidence invalid")
    if source.get("decision_authorized") is not False or manifest.get("decision_authorized") is not False:
        raise ValueError("Decision must remain blocked")
    for turn in turns:
        if not isinstance(turn.get("text"),str) or not turn["text"].strip():
            raise ValueError("Empty turn")
        if not set(turn.get("evidence_ids",[])).issubset(allowed):
            raise ValueError("Unknown evidence ID")
    # Shorter speaking turns, with targeted moderator prompts. These are
    # questions, NOT fabricated statements attributed to experts.
    steps=[{"role":"scientific_chair","phase":"opening","max_words":160}]
    steps += [{"role":r,"phase":"initial_position","max_words":150} for r in ROLES]
    for topic,instruction in TOPICS:
        steps.append({"role":"scientific_chair","phase":"targeted_question",
                      "topic":topic,"instruction":instruction,"max_words":85})
        responders={"sequencing":["mining","environment","esg"],
                    "water":["environment","agriculture","communities"],
                    "assurance":["esg","communities","mining"]}[topic]
        steps += [{"role":r,"phase":"response_to_prior","topic":topic,"max_words":120} for r in responders]
    steps.append({"role":"scientific_chair","phase":"decision_brief",
                  "required_sections":["immediate_priorities","tradeoffs","decision_conditions","uncertainties"],
                  "max_words":330})
    return {"schema":"TERRA_COUNCIL_009K_AGENDA_V1",
      "status":"EDITORIAL_PLAN_REVIEW_REQUIRED","source_kind":"009I_MUSE_TRANSCRIPT",
      "source_turns":len(turns),"question":manifest.get("question"),
      "active_experts":list(ROLES),"evidence_ids":sorted(allowed),
      "steps":steps,"decision_authorized":False,"audio_authorized":False,
      "meta_calls":0,"elevenlabs_calls":0,
      "scientific_constraints":[
        "No fabricated disagreement, consensus, source or metric",
        "Investigations prioritized, not mining authorization",
        "Screened WorldCover 2021 and WorldPop 2026 not site-validated",
        "Expert responses must address preceding speaker directly",
        "Abstain when evidence cannot support a claim",
        "Preserve source 009I and its human-review status"]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--debate",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    raw=Path(a.debate).read_bytes()
    source=json.loads(raw.decode("utf-8-sig"))
    manifest=json.loads(Path(a.manifest).read_text(encoding="utf-8-sig"))
    result=compile_agenda(source,manifest)
    result["source_sha256"]=hashlib.sha256(raw).hexdigest()
    dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":result["status"],"steps":len(result["steps"]),
      "source_turns":result["source_turns"],"meta_calls":0,
      "output":str(dest)},ensure_ascii=False))
if __name__=="__main__":main()
