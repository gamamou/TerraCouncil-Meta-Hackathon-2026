"""010D2: assemble a comparable, review-gated Muse/GPT semantic report.

No model calls. Never turns automated audit into scientific approval.
"""
import argparse,json
from pathlib import Path
from terra_council_010d_pipeline import source_info,validate_claims,verify_audit
from terra_council_010d2_gpt_audit import assemble
ALLOWED={"PRESERVED","PARTIAL","OMITTED","CONTRADICTED","METADATA_OMITTED"}
def load(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def summarize(audit,claims):
 verify_audit(audit,claims)
 verdict={r["claim_id"]:r["verdict"] for r in audit["assessments"]}
 must=[c["claim_id"] for c in claims if c["importance"]=="MUST_KEEP"]
 metadata=[c["claim_id"] for c in claims if c["importance"]=="METADATA_ONLY"]
 return {"must_keep_total":len(must),"must_keep_preserved":sum(verdict[x]=="PRESERVED" for x in must),
  "must_keep_at_risk":[x for x in must if verdict[x]!="PRESERVED"],
  "metadata_total":len(metadata),
  "metadata_omitted":sum(verdict[x]=="METADATA_OMITTED" for x in metadata),
  "unsupported_additions":audit.get("unsupported_additions",[]),
  "critical_omissions":audit.get("critical_omissions",[]),
  "numerical_mutations":audit.get("numerical_mutations",[])}
def report(packets,extract,gpt,muse_audit,gpt_audit):
 _,sha=assemble(packets,extract,gpt)
 claims=validate_claims(extract,source_info(packets)[0])
 if muse_audit.get("source_sha256")!=sha or muse_audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED":
  raise ValueError("Muse audit invalid/stale")
 if gpt_audit.get("source_sha256")!=sha or gpt_audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED":
  raise ValueError("GPT audit invalid/stale")
 return {"schema":"TERRA_COUNCIL_010D2_COMPARATIVE_AUDIT_V1",
  "status":"HUMAN_SCIENTIFIC_AND_ORAL_REVIEW_REQUIRED",
  "source_sha256":sha,
  "muse":summarize(muse_audit,claims),"gpt":summarize(gpt_audit,claims),
  "qualitative_rubric":{"scientific_fidelity":"0-5","oral_naturalness":"0-5",
   "rhythm_and_listening":"0-5","distinctive_esg_contribution":"0-5",
   "multi_agent_conversation_potential":"0-5"},
  "next_human_review":"Score both candidates blind and verify all essential claims against original source.",
  "model_superiority_established":False,"scientific_approval":False,"audio_authorized":False}
def main():
 p=argparse.ArgumentParser()
 for n in ("packets","claims","gpt","muse-audit","gpt-audit","output"):
  p.add_argument("--"+n,required=True)
 a=p.parse_args()
 result=report(*(load(getattr(a,n.replace("-","_"))) for n in
  ("packets","claims","gpt","muse-audit","gpt-audit")))
 with Path(a.output).open("x",encoding="utf-8") as f:
  json.dump(result,f,ensure_ascii=False,indent=2)
 for name in ("muse","gpt"):
  item=result[name]
  print(name.upper(),":",item["must_keep_preserved"],"/",item["must_keep_total"],
   "essential claims preserved; at risk:",item["must_keep_at_risk"],
   "; added:",item["unsupported_additions"])
 print("HUMAN REVIEW REQUIRED; NO AUDIO AUTHORIZED")
if __name__=="__main__":main()
