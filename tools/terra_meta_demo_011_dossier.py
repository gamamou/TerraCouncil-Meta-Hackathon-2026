"""DEMO-011 — Assemble a source-grounded decision dossier from existing Meta trace.
No new model calls. Does not prescribe or rank sites in Python.
"""
import argparse,hashlib,json,re
from pathlib import Path
from terra_demo_001_faith_gateway import load
from tools.terra_meta_demo_010c_readiness import evaluate

def build(snapshot,trace):
    readiness=evaluate(snapshot,trace)
    stages={s.get("stage"):s for s in trace.get("steps",[])}
    responses={k:stages.get(k,{}).get("response") for k in
        ("SPARK_RESEARCH_PLAN","WONDER_CRITIQUE","SPARK_REVISION")}
    sources=[]
    for step in trace.get("steps",[]):
        if step.get("stage","").startswith("FAITH_TOOL_RESULT_"):
            records=step.get("result",[])
            sources.append({"stage":step["stage"],"entity":step.get("action",{}).get("entity"),
                            "records_returned":len(records) if isinstance(records,list) else None,
                            "record_ids":[r.get("shape_uid") or r.get("solution_id") for r in records
                                          if isinstance(r,dict)][:100] if isinstance(records,list) else []})
    raw_final=responses["SPARK_REVISION"] or ""
    sites={x.get("shape_uid") for t in ("PilotCandidate","MiningPermit") for x in snapshot.get(t,[])}
    solutions={x.get("solution_id") for x in snapshot.get("RehabilitationSolution",[])}
    site_refs=sorted(set(re.findall(r"GUIDSHAPE:[A-Z0-9-]+",raw_final)))
    sol_refs=sorted(set(re.findall(r"SOL-CAT-[0-9]{5}",raw_final)))
    expected=hashlib.sha256(json.dumps(snapshot,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    supplied=trace.get("snapshot_sha256")
    snapshot_match=(supplied==expected) if supplied else None
    warnings=[]
    if snapshot_match is False:warnings.append("TRACE_SNAPSHOT_MISMATCH")
    if snapshot_match is None:warnings.append("TRACE_HAS_NO_SNAPSHOT_HASH")
    if set(site_refs)-sites:warnings.append("UNKNOWN_SITE_REFERENCE")
    if set(sol_refs)-solutions:warnings.append("UNKNOWN_SOLUTION_REFERENCE")
    if not raw_final:warnings.append("NO_FINAL_SPARK_REVISION")
    if trace.get("status")!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":warnings.append("TRACE_NOT_COMPLETED")
    if not readiness["coverage"]["is_complete"]:warnings.append("RESEARCH_COVERAGE_INCOMPLETE")
    valid=(not warnings and readiness["decision_readiness"]=="EVIDENCE_PRESENT_REQUIRES_HUMAN_SCIENTIFIC_REVIEW")
    return {"schema_version":"DEMO-011","dossier_type":"SCIENTIFIC_DECISION_SUPPORT_NOT_APPROVAL",
            "question":trace.get("question"),"trace_status":trace.get("status"),
            "snapshot_integrity":{"expected_sha256":expected,"trace_sha256":supplied,"match":snapshot_match},
            "research_coverage":readiness["coverage"],"sources_consulted":sources,
            "scientific_readiness":readiness,"council":{"spark_plan":responses["SPARK_RESEARCH_PLAN"],
              "wonder_critique":responses["WONDER_CRITIQUE"],"spark_revision":responses["SPARK_REVISION"]},
            "references":{"site_ids":site_refs,"solution_ids":sol_refs,
              "invalid_site_ids":sorted(set(site_refs)-sites),
              "invalid_solution_ids":sorted(set(sol_refs)-solutions)},
            "qa":{"warnings":warnings,"automated_release_allowed":False,
              "scientific_human_review_required":True,
              "basis":"Identifiers and source presence mechanically checked; model factual assertions not independently verified."},
            "review_checklist":["Check precise evidence for every model empirical claim.",
              "Confirm permit identity and geospatial link, without inferential joins.",
              "Obtain field validation and site-level degradation diagnosis before rehabilitation interventions.",
              "Review each catalog prerequisite and limitation against site measurements.",
              "Obtain qualified human scientific and administrative approval."]}

def main():
    p=argparse.ArgumentParser();p.add_argument("--snapshot",required=True)
    p.add_argument("--trace",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();dst=Path(a.output)
    if dst.exists():raise SystemExit("Refusing overwrite of existing dossier")
    data=load(a.snapshot);trace=json.loads(Path(a.trace).read_text(encoding="utf-8-sig"))
    dossier=build(data,trace)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(dossier,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"dossier":str(dst),"readiness":dossier["scientific_readiness"]["decision_readiness"],
                      "qa_warnings":dossier["qa"]["warnings"],"release_allowed":False},ensure_ascii=False))
if __name__=="__main__":main()
