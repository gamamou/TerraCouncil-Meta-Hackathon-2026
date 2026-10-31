"""DEMO-013: integrated scientific council artifacts (replay by default).
Spark/Wonder own scientific decisions. Python only orchestrates, audits, archives.
"""
import argparse,hashlib,json,os
from pathlib import Path
from datetime import datetime,timezone
from terra_demo_001_faith_gateway import load
from tools.terra_meta_demo_010b_adaptive import run
from tools.terra_meta_demo_011_dossier import build
from tools.terra_meta_demo_012_action_plan import plan

def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode("utf8")).hexdigest()

def passport(trace,dossier,actions,session):
    return {"schema_version":"DEMO-013-PASSPORT-PREVIEW","passport_status":"UNREVIEWED_INTERNAL",
        "session_id":session,"created_utc":datetime.now(timezone.utc).isoformat(),
        "question":trace.get("question"),
        "source_snapshot_sha256":dossier["snapshot_integrity"]["expected_sha256"],
        "trace_sha256":canonical_sha(trace),"dossier_sha256":canonical_sha(dossier),
        "action_plan_sha256":canonical_sha(actions),
        "research_coverage":dossier["research_coverage"],
        "scientific_readiness":dossier["scientific_readiness"]["decision_readiness"],
        "model_trace_stages":[s.get("stage") for s in trace.get("steps",[])],
        "audio":{"status":"NOT_GENERATED","reference":None},
        "human_review":{"status":"PENDING","approved":False},
        "note":"This is a draft traceability passport, not a certified public release or approved scientific decision."}

def write_bundle(data,trace,folder,session):
    if trace.get("status")!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":
        raise ValueError("Trace incomplete: no scientific dossier released")
    folder=Path(folder)
    if folder.exists():raise FileExistsError("Refusing to overwrite existing session folder")
    dossier=build(data,trace)
    actions=plan(dossier)
    p=passport(trace,dossier,actions,session)
    folder.mkdir(parents=True)
    for name,value in (("01_trace.json",trace),("02_scientific_dossier.json",dossier),
                        ("03_investigation_plan.json",actions),("04_passport_preview.json",p)):
        (folder/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return {"status":"BUNDLE_GENERATED_NEEDS_HUMAN_REVIEW",
            "folder":str(folder),"decision_readiness":p["scientific_readiness"],
            "action_count":len(actions["tasks"]),"passport_status":p["passport_status"],
            "audio_status":p["audio"]["status"],"qa_warnings":dossier["qa"]["warnings"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--trace",help="Existing completed council trace; avoids Meta calls")
    ap.add_argument("--question",help="Question for NEW Meta run")
    ap.add_argument("--execute",action="store_true",help="Explicitly authorize potentially billed Meta calls")
    ap.add_argument("--max-lookups",type=int,default=5)
    ap.add_argument("--output-dir",required=True)
    a=ap.parse_args()
    if bool(a.trace)==bool(a.execute):
        raise SystemExit("Choose exactly one: --trace (replay) OR --execute with --question")
    data=load(a.snapshot)
    folder=Path(a.output_dir)
    if folder.exists():raise SystemExit("Output folder already exists; refusing overwrite")
    session=folder.name
    if a.trace:
        trace=json.loads(Path(a.trace).read_text(encoding="utf-8-sig"))
    else:
        if not a.question:raise SystemExit("--question required for --execute")
        key=os.environ.get("MODEL_API_KEY")
        if not key:raise SystemExit("MODEL_API_KEY missing")
        folder.mkdir(parents=True)
        tracefile=folder/"00_in_progress_meta_trace.json"
        trace=run(data,a.question,key,tracefile,max_lookups=a.max_lookups)
        if trace.get("status")!="GENERATED_NEEDS_SCIENTIFIC_REVIEW":
            raise SystemExit("Meta cycle incomplete. Retain trace and do not retry automatically.")
        # Preserve previous checkpoint while moving final bundle into a new subfolder.
        folder=folder/"artifacts"
    print(json.dumps(write_bundle(data,trace,folder,session),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
