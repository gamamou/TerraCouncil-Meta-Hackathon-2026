"""010D: offline side-by-side scientific oral benchmark for Muse and GPT-6.

Quantitative metrics are descriptive, not scientific equivalence tests.
"""
import argparse,hashlib,json,re,unicodedata
from pathlib import Path
from terra_council_010d_pipeline import source_info,validate_claims

def norm(s):
 return re.sub(r"\s+"," ",unicodedata.normalize("NFC",s)).strip()
def metrics(text):
 technical=re.findall(r"\b(?:AOI|FSDC|EPSG)\b",text,flags=re.I)
 numbers=re.findall(r"(?<!\w)\d+(?:[.,]\d+)?\s*%?",text)
 return {"words":len(text.split()),"technical_terms_spoken":technical,
  "numbers_spoken":numbers}
def compare(packets,extraction,muse,gpt):
 source,sha=source_info(packets)
 if extraction.get("source_sha256")!=sha or extraction.get("status")!="CLAIMS_HUMAN_REVIEW_REQUIRED":
  raise ValueError("Claims source or status mismatch")
 claims=validate_claims(extraction,source)
 if muse.get("source_sha256")!=sha or muse.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED":
  raise ValueError("Muse source or status mismatch")
 if gpt.get("schema")!="TERRA_COUNCIL_010D_GPT_REFERENCE_V1" or gpt.get("role")!="esg":
  raise ValueError("GPT reference invalid")
 if norm(gpt.get("scientific_source_text",""))!=norm(source):
  raise ValueError("GPT reference is not based on exact source")
 candidates=[]
 for label,obj in (("A",muse),("B",gpt)):
  spoken=obj["spoken_text"]
  candidates.append({"blind_label":label,"spoken_text":spoken,**metrics(spoken)})
 return {"schema":"TERRA_COUNCIL_010D_COMPARISON_V1",
  "status":"BLIND_HUMAN_REVIEW_REQUIRED","source_sha256":sha,
  "candidates":candidates,"identity_key":{"A":"Muse Wonder candidate","B":"ChatGPT GPT-6 manual reference"},
  "must_keep_claims":[{"id":x["claim_id"],"meaning":x["meaning"]}
   for x in claims if x["importance"]=="MUST_KEEP"],
  "rubric":{"scientific_fidelity":"0-5","semantic_omissions":"0-5",
   "oral_naturalness":"0-5","distinctive_esg_contribution":"0-5",
   "absence_of_unjustified_additions":"0-5"},
  "objective_superiority_established":False,
  "independent_audit_required":True,"human_approval":False,"audio_authorized":False,
  "meta_calls":0}
def main():
 p=argparse.ArgumentParser()
 for k in ("packets","claims","muse","gpt","output"):p.add_argument("--"+k,required=True)
 a=p.parse_args()
 result=compare(*(json.loads(Path(p).read_text(encoding="utf-8-sig"))
   for p in (a.packets,a.claims,a.muse,a.gpt)))
 with Path(a.output).open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 for row in result["candidates"]:
  print("CANDIDATE",row["blind_label"],"words",row["words"],
   "technical",row["technical_terms_spoken"],"numbers",row["numbers_spoken"])
 print("COMPARISON FOR HUMAN REVIEW; NO SCIENTIFIC APPROVAL")
if __name__=="__main__":main()
