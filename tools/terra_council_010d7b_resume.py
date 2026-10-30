"""TERRA 010D7B: resume only T11 oral and audit from validated recovered extraction.
No overwrite, no retry, no automatic approvals/audio. Explicit authorization per call.
"""
import argparse,json,os
from pathlib import Path
from terra_council_010d_pipeline import read,validate_claims,verify_audit,call,AUDIT
from terra_council_010d6_runner import (digest,output,safe_previous,ORAL_SYSTEM,ROLE_GUIDANCE)
from terra_council_010d5_full_council import build,ROLES,MISSIONS

def check(a):
 root=Path(a.workdir); packets=read(a.packets)
 plan=build(packets,root)
 t=packets["turns"][10]
 if t["turn"]!=11 or t["speaker"]!="scientific_chair":raise ValueError("Unexpected T11 source")
 src=t["scientific_source_text"];sha=digest(src)
 rec=read(root/"Boke-010D7-T11-extract-recovered.json")
 if rec.get("status")!="RECOVERED_CLAIMS_HUMAN_REVIEW_REQUIRED" or rec.get("source_sha256")!=sha:
  raise ValueError("Recovered source mismatch")
 if rec.get("scientific_approval") is not False or rec.get("audio_authorized") is not False:
  raise ValueError("Recovery control flags changed")
 raw=(root/"Boke-010D6-T11-extract-raw.json").read_bytes()
 import hashlib
 if hashlib.sha256(raw).hexdigest()!=rec.get("original_raw_sha256"):
  raise ValueError("Raw extraction provenance mismatch")
 claims=validate_claims({"claims":rec["claims"]},src)
 prior,excluded=safe_previous(root,plan,11)
 out=root/f"Boke-010D7B-T11-{a.stage}.json"
 other=root/"Boke-010D7B-T11-oral.json"
 if out.exists() or out.with_name(out.stem+"-raw.json").exists():raise ValueError("Output or raw journal already exists")
 if a.stage=="audit":
  oral=read(other)
  if oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or oral.get("source_sha256")!=sha or oral.get("recovery_sha256")!=digest(json.dumps(rec,ensure_ascii=False,sort_keys=True)):
   raise ValueError("Oral recovery chain invalid")
  speech=oral.get("spoken_text")
  if not isinstance(speech,str) or not speech.strip():raise ValueError("Empty oral")
  if not isinstance(oral.get("covered_claim_ids"),list):raise ValueError("Oral claim mapping absent")
 return root,src,sha,rec,claims,prior,excluded,out

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--packets",required=True);p.add_argument("--workdir",required=True)
 p.add_argument("--stage",choices=["oral","audit"],required=True)
 p.add_argument("--effort",default="high",choices=["minimal","low","medium","high","xhigh","max"])
 p.add_argument("--execute",action="store_true");p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 root,src,sha,rec,claims,prior,excluded,out=check(a)
 print(json.dumps({"status":"010D7B_PREVIEW","stage":a.stage,"turn":11,
  "prior_context":len(prior),"excluded":excluded,"potential_meta_calls":1,"actual_meta_calls":0,
  "audio_authorized":False}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit authorization required")
 if not(os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta key missing")
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT","stage":a.stage},f)
 try:
  if a.stage=="oral":
   role="president";model="muse-wonder-1.0"
   system=ORAL_SYSTEM.format(role=role,mission=MISSIONS[role],guide=ROLE_GUIDANCE[role])
   data={"source":src,"role":role,"claims":claims,"prior_audited_context":prior,
    "excluded_prior_turns_with_flags":excluded}
  else:
   model="muse-spark-1.3";system=AUDIT
   speech=read(root/"Boke-010D7B-T11-oral.json")["spoken_text"]
   data={"source":src,"claims":claims,"spoken_text":speech}
  response,usage=call(model,a.effort,system,data,out)
  if a.stage=="oral":
   if response.get("role")!="president" or not isinstance(response.get("spoken_text"),str) or not response["spoken_text"].strip():
    raise ValueError("Invalid oral")
   ids={c["claim_id"] for c in claims}
   for field in ("covered_claim_ids","metadata_omitted_claim_ids"):
    mapping=response.get(field)
    if not isinstance(mapping,list) or not set(mapping).issubset(ids):raise ValueError("Invalid claim mapping")
   if not isinstance(response.get("context_reference"),str):raise ValueError("Missing context reference")
   result={**response,"status":"ORAL_HUMAN_REVIEW_REQUIRED"}
  else:
   verify_audit(response,claims)
   result={**response,"oral_sha256":digest(speech),"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED"}
  result.update({"schema":"TERRA_COUNCIL_010D7B_V1","turn":11,"role":"president",
   "stage":a.stage,"source_sha256":sha,
   "recovery_sha256":digest(json.dumps(rec,ensure_ascii=False,sort_keys=True)),
   "model":model,"usage":usage,"scientific_approval":False,
   "decision_authorized":False,"audio_authorized":False})
  out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
  print(json.dumps({"status":result["status"],"stage":a.stage,"turn":11}),flush=True)
 except Exception as exc:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","stage":a.stage,
   "error_type":type(exc).__name__,"error":str(exc)[:350]}),encoding="utf-8")
  raise SystemExit("STOP_NO_RETRY: inspect raw journal; do not retry")
if __name__=="__main__":main()
