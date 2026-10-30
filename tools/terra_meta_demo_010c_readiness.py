"""DEMO-010C: read-only decision-readiness assessment for 010B trace.
No scoring, site matching, approvals, or fabricated geospatial context.
"""
import argparse, hashlib, json
from pathlib import Path
from terra_demo_001_faith_gateway import load
from tools.terra_meta_demo_010b_adaptive import coverage

def evaluate(snapshot,trace):
    observations=[{"action":s["action"],"result":s["result"]}
      for s in trace.get("steps",[]) if s.get("stage","").startswith("FAITH_TOOL_RESULT_")
      and isinstance(s.get("result"),list)]
    cov=coverage(snapshot,observations,trace.get("question",""))
    observed={r.get("shape_uid") for r in snapshot.get("MiningPermit",[])
      if r.get("has_observed_footprint") is True}
    spatial={r.get("shape_uid") for r in snapshot.get("PermitSpatialContext",[])
      if r.get("shape_uid")}
    diagnosed={r.get("shape_uid") for r in snapshot.get("SiteRehabilitationRecommendation",[])
      if r.get("shape_uid") and r.get("identified_degradations")}
    has_catalog="RehabilitationSolution" in cov["consulted"]
    checkpoints={
      "available_required_sources_consulted":cov["is_complete"],
      "site_footprint_evidence_present":bool(observed),
      "site_spatial_evidence_present":bool(spatial),
      "site_degradation_diagnostics_present":bool(diagnosed),
      "catalog_consulted":has_catalog,
      "model_revision_present":any(s.get("stage")=="SPARK_REVISION" for s in trace.get("steps",[])),
      "citation_ids_valid":not any(trace.get("citation_check",{}).get(k,[]) for k in
                                 ("unknown_site_ids","unknown_solution_ids"))}
    note=[]
    if not cov["is_complete"]:note.append("Required accessible sources not all consulted.")
    if not observed:note.append("No positively observed footprint in provided mining permits.")
    if not diagnosed:note.append("No site-specific documented degradation in provided diagnostics.")
    if not spatial:note.append("No linked site-level spatial evidence.")
    if not has_catalog:note.append("Catalog not consulted in research trace.")
    if trace.get("status")!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":
      note.append("Model research cycle not completed.")
    # Gate applies to permission to assert site rehabilitation, not actual site ranking.
    can_prescribe=(bool(observed) and bool(diagnosed) and bool(spatial) and has_catalog
      and checkpoints["citation_ids_valid"] and cov["is_complete"])
    decision="RESEARCH_INCOMPLETE" if not cov["is_complete"] else (
      "EVIDENCE_NOT_READY_FOR_SITE_PRESCRIPTIONS" if not can_prescribe else
      "EVIDENCE_PRESENT_REQUIRES_HUMAN_SCIENTIFIC_REVIEW")
    return {"schema_version":"010C","decision_readiness":decision,
      "authorization":"NOT_AUTHORIZED_AUTOMATICALLY",
      "coverage":cov,"checkpoints":checkpoints,"limitations":note,
      "claim_boundary":"A complete tool search does not validate the underlying scientific evidence; no automatic site priority, treatment or approval.",
      "trace_status":trace.get("status")}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True);ap.add_argument("--trace",required=True)
    ap.add_argument("--output")
    args=ap.parse_args()
    snapshot=load(args.snapshot)
    trace=json.loads(Path(args.trace).read_text(encoding="utf-8-sig"))
    result=evaluate(snapshot,trace)
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
      target=Path(args.output)
      if target.exists():raise SystemExit("Refusing existing output")
      target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text+"\n",encoding="utf8")
    print(text)
if __name__=="__main__":main()
