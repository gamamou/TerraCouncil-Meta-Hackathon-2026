"""TERRA-META-011A: immutable Boké council consolidation; offline only.

Reports individual source fidelity and unresolved alerts. Does not claim
cross-turn semantic validation, decision approval, or audio approval.
"""
import argparse,hashlib,json,re
from pathlib import Path
from terra_council_010d_pipeline import read,validate_claims,verify_audit
from terra_council_010d5_full_council import ROLES
from terra_council_010d3_dialogue import path as d3path

def sha(text):return hashlib.sha256(text.encode("utf-8")).hexdigest()
def paths(root,n):
 if n<=3:return d3path(root,n,"oral"),d3path(root,n,"audit"),None
 if n==4:
  return root/"Boke-010D4-ESG-Oral.json",root/"Boke-010D4-ESG-Audit.json",None
 if n==11:
  return root/"Boke-010D7B-T11-oral.json",root/"Boke-010D7B-T11-audit.json",root/"Boke-010D7-T11-extract-recovered.json"
 prefix=f"Boke-010D6-T{n:02d}-"
 return root/(prefix+"oral.json"),root/(prefix+"audit.json"),root/(prefix+"extract.json")
def assemble(root,packets):
 turns=packets.get("turns")
 if packets.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or not isinstance(turns,list) or len(turns)!=19:raise ValueError("Expected 19 original packets")
 items=[]
 for n,t in enumerate(turns,1):
  role=ROLES.get(t.get("speaker"))
  source=t.get("scientific_source_text")
  if t.get("turn")!=n or role is None or not isinstance(source,str) or not source.strip():raise ValueError(f"Invalid source at T{n:02d}")
  op,ap,ep=paths(root,n)
  if not op.exists() or not ap.exists():raise ValueError(f"Missing oral/audit T{n:02d}")
  oral,audit=read(op),read(ap)
  source_hash=sha(source); speech=oral.get("spoken_text")
  if not isinstance(speech,str) or not speech.strip():raise ValueError(f"Empty oral T{n:02d}")
  if oral.get("source_sha256")!=source_hash or audit.get("source_sha256")!=source_hash:raise ValueError(f"Source hash mismatch T{n:02d}")
  if audit.get("oral_sha256")!=sha(speech):raise ValueError(f"Oral hash mismatch T{n:02d}")
  if oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED":raise ValueError(f"Invalid review states T{n:02d}")
  if n==11:
   rec=read(ep)
   if rec.get("status")!="RECOVERED_CLAIMS_HUMAN_REVIEW_REQUIRED" or rec.get("source_sha256")!=source_hash:raise ValueError("Invalid T11 recovery")
   if not rec.get("original_raw_sha256"):raise ValueError("Missing T11 raw provenance")
   raw=(root/"Boke-010D6-T11-extract-raw.json").read_bytes()
   if hashlib.sha256(raw).hexdigest()!=rec["original_raw_sha256"]:raise ValueError("T11 raw content changed")
   chain=sha(json.dumps(rec,ensure_ascii=False,sort_keys=True))
   if oral.get("recovery_sha256")!=chain or audit.get("recovery_sha256")!=chain:raise ValueError("T11 recovery chain changed")
   claims=validate_claims({"claims":rec["claims"]},source)
  elif ep is not None:
   extraction=read(ep)
   if extraction.get("source_sha256")!=source_hash or extraction.get("status")!="CLAIMS_HUMAN_REVIEW_REQUIRED":raise ValueError(f"Invalid extract T{n:02d}")
   claims=validate_claims(extraction,source)
  else:
   claims=None
  if claims is not None:verify_audit(audit,claims)
  alerts=[]
  for field in ("unsupported_additions","critical_omissions","numerical_mutations"):
   value=audit.get(field,[])
   if not isinstance(value,list):raise ValueError(f"Invalid alert structure T{n:02d}")
   alerts.extend([{"type":field,"detail":v} for v in value])
  assessments=audit.get("assessments",[])
  if not isinstance(assessments,list) or not assessments:raise ValueError(f"Missing assessments T{n:02d}")
  alerts.extend([{"type":"claim_verdict","claim_id":v.get("claim_id"),"verdict":v.get("verdict"),"detail":v.get("reason","")} for v in assessments if v.get("verdict") in ("PARTIAL","OMITTED","CONTRADICTED")])
  items.append({"turn":n,"role":role,"source_sha256":source_hash,"oral_sha256":sha(speech),
   "original_oral_file":op.name,"original_audit_file":ap.name,"original_extract_file":ep.name if ep else None,
   "spoken_text":speech,"audit_status":audit["status"],"alert_count":len(alerts),"alerts":alerts,
   "essential_claims":sum(c["importance"]=="MUST_KEEP" for c in claims) if claims is not None else None,
   "essential_preserved":sum(c["importance"]=="MUST_KEEP" and any(a.get("claim_id")==c["claim_id"] and a.get("verdict")=="PRESERVED" for a in assessments) for c in claims) if claims is not None else None,
   "scientific_approval":False,"audio_authorized":False})
 return {"schema":"TERRA_META_011A_COUNCIL_CONSOLIDATION_V1",
  "status":"OFFLINE_COUNCIL_REVIEW_REQUIRED",
  "turn_count":len(items),"flagged_turns":[i["turn"] for i in items if i["alert_count"]>0],
  "source_integrity":"HASH_CHECKS_PASSED",
  "cross_turn_dialogue_validation":"NOT_PERFORMED",
  "scientific_approval":False,"audio_authorized":False,"decision_authorized":False,
  "turns":items}

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--packets",required=True);parser.add_argument("--workdir",required=True)
 parser.add_argument("--output",required=True)
 a=parser.parse_args();root=Path(a.workdir)
 output=Path(a.output)
 if output.exists():raise SystemExit("Refusing to overwrite existing consolidation")
 report=assemble(root,read(a.packets))
 with output.open("x",encoding="utf-8") as f:json.dump(report,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":report["status"],"turns":report["turn_count"],
 "flagged_turns":report["flagged_turns"],"source_integrity":report["source_integrity"],
 "audio_authorized":False,"meta_calls":0},ensure_ascii=False))
if __name__=="__main__":main()
