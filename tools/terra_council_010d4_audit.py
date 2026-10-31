"""010D4: independent semantic audit of directed ESG candidate; no audio."""
import argparse,hashlib,json,os
from pathlib import Path
from terra_council_010d_pipeline import read,source_info,validate_claims,AUDIT,verify_audit,call
from terra_council_010d4_director import validate_candidate
def main():
 p=argparse.ArgumentParser()
 for k in ("packets","claims","oral","output"):p.add_argument("--"+k,required=True)
 p.add_argument("--effort",default="high",choices=("minimal","low","medium","high","xhigh","max"))
 p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 source,sha=source_info(read(a.packets))
 extracted=read(a.claims)
 if extracted.get("status")!="CLAIMS_HUMAN_REVIEW_REQUIRED" or extracted.get("source_sha256")!=sha:
  raise ValueError("Claims missing/stale")
 claims=validate_claims(extracted,source)
 oral=read(a.oral)
 if oral.get("schema")!="TERRA_COUNCIL_010D4_ORAL_V1" or oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or oral.get("source_sha256")!=sha:
  raise ValueError("Directed oral missing or stale")
 validate_candidate(oral,claims)
 spoken=oral["spoken_text"];digest=hashlib.sha256(spoken.encode("utf-8")).hexdigest()
 if oral.get("spoken_sha256")!=digest:raise ValueError("Oral hash mismatch")
 out=Path(a.output)
 print(json.dumps({"status":"010D4_AUDIT_PREVIEW","claims":len(claims),"model":"muse-spark-1.3",
  "calls_if_authorized":1,"actual_meta_calls":0,"audio_authorized":False}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit Meta authorization required")
 if not (os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta key missing")
 if out.exists():raise SystemExit("Audit exists; no overwrite")
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT"},f)
 try:
  result,usage=call("muse-spark-1.3",a.effort,AUDIT,
   {"source":source,"claims":claims,"spoken_text":spoken},out)
  verify_audit(result,claims)
 except Exception as exc:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","error_type":type(exc).__name__,
   "error":str(exc)[:350]}),encoding="utf-8")
  raise SystemExit("STOP_NO_RETRY; inspect raw and journal")
 result.update({"schema":"TERRA_COUNCIL_010D4_AUDIT_V1",
  "status":"SEMANTIC_HUMAN_REVIEW_REQUIRED","source_sha256":sha,
  "oral_sha256":digest,"usage":usage,"scientific_approval":False,
  "audio_authorized":False,"decision_authorized":False})
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 must={x["claim_id"] for x in claims if x["importance"]=="MUST_KEEP"}
 passed={x["claim_id"] for x in result["assessments"] if x["verdict"]=="PRESERVED"}
 print(json.dumps({"status":result["status"],"must_keep_preserved":len(must&passed),
  "must_keep_total":len(must),"unsupported_additions":result.get("unsupported_additions",[]),
  "audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
