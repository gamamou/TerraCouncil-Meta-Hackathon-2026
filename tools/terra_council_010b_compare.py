"""010B-COMPARE: compare two existing Muse scientific benchmark files offline.

No API requests. Comparisons are descriptive; not proof of model superiority.
"""
import argparse,json,hashlib
from pathlib import Path
def compare(a,b):
 for x in (a,b):
  if x.get("schema")!="TERRA_COUNCIL_010B_REASONING_V1" or x.get("status")!="SCIENTIFIC_REVIEW_REQUIRED":
   raise ValueError("Valid 010B scientific outputs required")
  if x.get("source_sha256") is None or x.get("decision_authorized") is not False:
   raise ValueError("Invalid provenance or decision gate")
 if a["source_sha256"]!=b["source_sha256"]:raise ValueError("Different FSDC manifest inputs")
 rows=[]
 for x in (a,b):
  usage=x.get("usage") or {}
  detail=usage.get("completion_tokens_details") or {}
  findings=x.get("findings",[])
  refs=sorted({r for f in findings for r in f.get("evidence_ids",[])})
  rows.append({"model":x.get("model"),"effort":x.get("effort"),
   "findings":len(findings),"unique_evidence_refs":refs,
   "investigations":len(x.get("priority_investigations",[])),
   "prompt_tokens":usage.get("prompt_tokens"),
   "completion_tokens":usage.get("completion_tokens"),
   "reasoning_tokens":detail.get("reasoning_tokens"),
   "total_tokens":usage.get("total_tokens")})
 return {"schema":"TERRA_COUNCIL_010B_COMPARISON_V1",
  "status":"HUMAN_SCIENTIFIC_COMPARISON_REQUIRED","source_sha256":a["source_sha256"],
  "models":rows,"scientific_superiority_established":False,
  "decision_authorized":False,"audio_authorized":False,"meta_calls":0,
  "review_criteria":["Accuracy of FSDC claims","Relevance of investigation priorities",
   "Uncertainty and non-causality","Distinction between study authorization and mine development",
   "Evidence-to-claim entailment","Novelty without unsupported inferences"]}
def main():
 p=argparse.ArgumentParser()
 for k in ("spark","wonder","output"):p.add_argument("--"+k,required=True)
 args=p.parse_args()
 a=json.loads(Path(args.spark).read_text(encoding="utf-8-sig"))
 b=json.loads(Path(args.wonder).read_text(encoding="utf-8-sig"))
 result=compare(a,b)
 with Path(args.output).open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
