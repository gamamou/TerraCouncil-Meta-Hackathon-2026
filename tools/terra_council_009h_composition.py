"""009H: evidence-aware council composition. Offline preview only.

Selection is a documented proposal, not a Muse inference or an impact finding.
Never infer local mine impacts from screening data. No external requests.
"""
import argparse,json
from pathlib import Path
from terra_council_009g_exploratory import make_plan

def compose(manifest):
    plan=make_plan(manifest)  # enforce original 009F safeguards
    q=plan["question"].casefold()
    findings=manifest["claims"]
    kinds=" ".join(str(c.get("dataset","")).casefold()+" "+str(c.get("finding","")).casefold() for c in findings)
    roles=set(plan["active_experts"])
    reasons={role:["Directement mentionne dans la question"] for role in roles}
    mining_decision=("minier" in q or "mine" in q or "bauxite" in q)
    if mining_decision and ("investigation" in q or "garantie" in q or "developpement" in q or "développement" in q):
        roles.update(("environment","esg"))
        reasons.setdefault("environment",[]).append("Evaluation des incertitudes environnementales avant projet minier")
        reasons.setdefault("esg",[]).append("Examen des garanties environnementales, sociales et de gouvernance; aucune conformite presumee")
    if "worldpop" in kinds or "population" in kinds:
        if mining_decision:
            roles.add("communities")
            reasons.setdefault("communities",[]).append("Population dans le perimetre: examen des besoins de consultation, pas exposition etablie")
    if "cropland" in kinds or "terres cultivées" in kinds:
        # Include when development question asks to prioritize investigations:
        if mining_decision and "investigation" in q:
            roles.add("agriculture")
            reasons.setdefault("agriculture",[]).append("Occupation agricole observee en 2021; examiner si une investigation agricole est necessaire")
    ordered=[r for r in ("mining","environment","esg","communities","agriculture","energy","economy") if r in roles]
    steps=[{"role":"scientific_chair","phase":"opening"}]
    steps += [{"role":r,"phase":"position"} for r in ordered]
    steps.append({"role":"scientific_chair","phase":"cross_examination"})
    steps += [{"role":r,"phase":"rebuttal_and_revision"} for r in ordered]
    steps.append({"role":"scientific_chair","phase":"deliberation"})
    plan.update({"schema":"TERRA_COUNCIL_009H_COMPOSITION_V1",
       "active_experts":ordered,"steps":steps,
       "selection_reasons":reasons,
       "selection_method":"RULE_BASED_CONTEXTUAL_PROPOSAL_NOT_MUSE",
       "scientific_review_required":True,"decision_authorized":False,
       "audio_authorized":False,"meta_calls":0})
    return plan

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.manifest).read_text(encoding="utf-8-sig"))
    result=compose(data)
    dest=Path(a.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":"PREVIEW_REVIEW_REQUIRED",
      "experts":result["active_experts"],"reasons":result["selection_reasons"],
      "planned_calls":len(result["steps"]),"actual_meta_calls":0,
      "output":str(dest)},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
