"""DEMO-012: evidence-gap action planning from a DEMO-011 decision dossier.
Administrative investigation tasks only; never prescribe site treatment in Python.
"""
import argparse, json
from pathlib import Path

GAPS={
 "RESEARCH_COVERAGE_INCOMPLETE":("Complete available FAITH evidence consultation","FAITH gateway query log","Research lead","Confirm required sources queried with identifiers and versioned trace"),
 "TRACE_HAS_NO_SNAPSHOT_HASH":("Establish immutable dataset-to-trace provenance","Snapshot SHA-256 and trace digest","Data steward","Verify hash matches the exact source snapshot"),
 "TRACE_SNAPSHOT_MISMATCH":("Resolve source-trace mismatch before using conclusions","Reconciled snapshot and trace","Data steward","Re-run offline validation using the correct immutable snapshot"),
 "NO_FINAL_SPARK_REVISION":("Obtain complete deliberation before interpretation","Final Spark output reviewed by Wonder","Council coordinator","Require a completed trace, without automatic model retry"),
 "UNKNOWN_SITE_REFERENCE":("Verify unsupported site identifiers","Source permit identity evidence","Geospatial analyst","Match identifier to source data; do not infer spatial joins"),
 "UNKNOWN_SOLUTION_REFERENCE":("Verify unsupported catalog references","FSDC rehabilitation catalog","Scientific reviewer","Check exact solution_id in source catalog")
}
CHECKPOINTS={
 "site_footprint_evidence_present":("Confirm mining footprint by admissible imagery or field verification","Geospatial analyst","Georeferenced footprint observation, date, method, and uncertainty"),
 "site_spatial_evidence_present":("Collect verified site-specific spatial context","Geospatial analyst","Spatial joins with source CRS, radius, date, and provenance"),
 "site_degradation_diagnostics_present":("Document observed site degradation before proposing treatment","Environmental scientist","Field diagnostic with precise location, measurement, and quality status"),
 "catalog_consulted":("Consult rehabilitation catalog and its prerequisites","Restoration specialist","Exact catalog records, limitations, and required validation")
}

def plan(dossier):
    if dossier.get("schema_version")!="DEMO-011":raise ValueError("Expected DEMO-011 dossier")
    readiness=dossier["scientific_readiness"]
    warnings=set(dossier.get("qa",{}).get("warnings",[]))
    tasks=[]
    def add(code,title,owner,evidence,gate):
        tasks.append({"task_id":"INV-%03d"%(len(tasks)+1),"gap_code":code,
          "action":title,"proposed_owner_role":owner,
          "evidence_to_collect":evidence,"completion_criterion":gate,
          "status":"PROPOSED_NOT_AUTHORIZED","site_scope":"NOT_ASSIGNED"})
    for code in sorted(warnings):
        if code in GAPS:
            title,evidence,owner,gate=GAPS[code];add(code,title,owner,evidence,gate)
    for code,(title,owner,evidence) in CHECKPOINTS.items():
        if not readiness.get("checkpoints",{}).get(code,False):
            add(code,title,owner,evidence,
                "Qualified scientist validates source suitability and records evidence status")
    if not readiness.get("coverage",{}).get("is_complete",False) and "RESEARCH_COVERAGE_INCOMPLETE" not in warnings:
        add("COVERAGE_INCOMPLETE","Complete required dataset queries","FAITH research lead",
          "Documented retrievals of missing available entities","All required accessible sources consulted")
    return {"schema_version":"DEMO-012","type":"SCIENTIFIC_INVESTIGATION_PLAN",
      "question":dossier.get("question"),
      "decision_readiness":readiness.get("decision_readiness"),
      "evidence_snapshot_sha256":dossier.get("snapshot_integrity",{}).get("expected_sha256"),
      "tasks":tasks,
      "authorization":"PLANNING_ONLY_REQUIRES_HUMAN_APPROVAL",
      "scientific_boundary":"These tasks address observed evidence gaps. They are not site-level findings, prioritization rankings, or approved rehabilitation prescriptions.",
      "source_dossier_warnings":sorted(warnings)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dossier",required=True);ap.add_argument("--output",required=True)
    args=ap.parse_args();out=Path(args.output)
    if out.exists():raise SystemExit("Refusing to overwrite output")
    dossier=json.loads(Path(args.dossier).read_text(encoding="utf-8-sig"))
    result=plan(dossier);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"output":str(out),"investigations":len(result["tasks"]),
       "authorization":result["authorization"]},ensure_ascii=False))
if __name__=="__main__":main()
