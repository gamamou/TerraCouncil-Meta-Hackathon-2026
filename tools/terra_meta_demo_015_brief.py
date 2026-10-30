"""DEMO-014/015: Meta-authored question family + brief from existing council trace.
No Python semantic classifier, recommendation engine, or approval.
Offline replay makes an evidence-linked brief without inventing new conclusions.
Optional Meta authoring uses explicit --execute and preserves raw response.
"""
import argparse,json,os
from pathlib import Path
from council import meta_call,SPARK
FAMILIES=("diagnostic","solutions","strategic_arbitration","risk","multisector","simple")
def assemble(dossier,actions,passport,classification=None):
    if dossier.get("schema_version")!="DEMO-011":raise ValueError("Expected DEMO-011")
    original=dossier.get("council",{})
    recommendation=original.get("spark_revision") or ""
    return {"schema_version":"DEMO-015","status":"DRAFT_NEEDS_HUMAN_REVIEW",
      "question":dossier.get("question"),"family":{"status":"NOT_CLASSIFIED_BY_MODEL" if classification is None else "META_CLASSIFIED",
       "meta_output":classification},
      "executive_brief":{"heading":"Scientific Council Brief",
       "scientific_readiness":dossier["scientific_readiness"]["decision_readiness"],
       "research_coverage":dossier["research_coverage"],
       "council_recommendations_verbatim":recommendation,
       "critic_assessment_verbatim":original.get("wonder_critique"),
       "evidence_limitations":dossier["scientific_readiness"].get("limitations",[])},
      "follow_up":{"proposed_investigations":actions.get("tasks",[]),
       "tracking_state":"NOT_STARTED_PENDING_HUMAN_AUTHORIZATION"},
      "passport":{"session_id":passport.get("session_id"),
       "status":passport.get("passport_status"),"human_review":passport.get("human_review")},
      "audio":{"status":"NOT_GENERATED","family_adaptation":"PENDING_META_CLASSIFICATION"},
      "disclosure":"This draft quotes model output; it does not independently verify scientific claims."}

def classify(question,key,caller=meta_call):
    instruction=("Classify the question for TerraCouncil audio and council format. "+
     "You may select one or more relevant families among: "+", ".join(FAMILIES)+
     ". Return concise JSON with fields families (array), rationale, suggested_debate_format, "+
     "voice_roles, expected_length. Do not make scientific findings or rank sites.")
    result=caller(SPARK,instruction,{"question":question},key)
    if not isinstance(result,str) or not result.strip():raise ValueError("Empty Meta classification")
    return {"model":SPARK,"raw_response":result}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--session",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--execute-classification",action="store_true")
    a=p.parse_args();root=Path(a.session)
    d=json.loads((root/"02_scientific_dossier.json").read_text(encoding="utf-8-sig"))
    actions=json.loads((root/"03_investigation_plan.json").read_text(encoding="utf-8-sig"))
    passport=json.loads((root/"04_passport_preview.json").read_text(encoding="utf-8-sig"))
    out=Path(a.output)
    if out.exists():raise SystemExit("Refusing overwrite")
    classification=None
    if a.execute_classification:
        key=os.environ.get("MODEL_API_KEY")
        if not key:raise SystemExit("MODEL_API_KEY missing")
        # Save raw response immediately after the only Meta call.
        classification=classify(d.get("question",""),key)
        checkpoint=out.with_suffix(".classification.json")
        if checkpoint.exists():raise SystemExit("Classification checkpoint already exists")
        checkpoint.parent.mkdir(parents=True,exist_ok=True)
        checkpoint.write_text(json.dumps(classification,ensure_ascii=False,indent=2),encoding="utf8")
    output=assemble(d,actions,passport,classification)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"brief":str(out),"family_status":output["family"]["status"],
      "recommendations_source":"SPARK_REVISION_VERBATIM",
      "tracking":"NOT_STARTED_PENDING_HUMAN_AUTHORIZATION"},ensure_ascii=False))
if __name__=="__main__":main()
