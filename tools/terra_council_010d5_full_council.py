"""010D5 — Whole-council dialogue director: 19-turn OFFLINE plan.

No model calls. Keeps scientific source unchanged. Only audited turns
may serve as dialogue context. Unsupported additions remain flagged,
not treated as evidence. No blanket claim waivers or audio approval.
"""
import argparse,hashlib,json,re
from pathlib import Path
from terra_council_010d_pipeline import read
from terra_council_010d3_dialogue import path as d3path

ROLES={
 "scientific_chair":"president","chair":"president","president":"president",
 "mining":"mining","environment":"environment","esg":"esg",
 "communities":"communities","agriculture":"agriculture"}
MISSIONS={
 "president":"Poser une question precise, verifier ce qui reste inconnu; conduire la deliberation sans faire les analyses des experts.",
 "mining":"Distinguer limites des preuves et investigations relatives au perimetre et aux aspects miniers; aucune caracterisation de gisement sans source.",
 "environment":"Examiner limites de la cartographie, habitats et eau; ne pas inferer biodiversite ou impact.",
 "esg":"Analyser tracabilite, protocoles, acces a la preuve et criteres de decision; ne pas affirmer de conformite.",
 "communities":"Formuler les questions demographiques et sociales a investiguer; WorldPop ne donne pas de personnes affectees.",
 "agriculture":"Formuler les questions agricoles et de terrain a investiguer; WorldCover ne prouve pas des pertes agricoles."
}
def hashtext(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def build(packets,workdir):
 turns=packets.get("turns")
 if packets.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or not isinstance(turns,list) or len(turns)!=19:
  raise ValueError("Need exactly 19 009O oral packets")
 result=[];prior=[]
 for i,t in enumerate(turns,1):
  role=ROLES.get(t.get("speaker"))
  src=t.get("scientific_source_text")
  if t.get("turn")!=i or role is None or not isinstance(src,str) or not src.strip():
   raise ValueError("Unknown role, empty source or turn order")
  sha=hashtext(src);state="SCIENTIFIC_ORAL_NOT_YET_AUDITED"
  alerts=[]
  if i<=3:
   op=d3path(workdir,i,"oral");ap=d3path(workdir,i,"audit")
   if not op.exists() or not ap.exists():raise ValueError(f"Required 010D3 audit missing at {i}")
   oral,audit=read(op),read(ap)
   if oral.get("source_sha256")!=sha or audit.get("source_sha256")!=sha:
    raise ValueError(f"Source mismatch at {i}")
   if audit.get("oral_sha256")!=hashtext(oral.get("spoken_text","")):
    raise ValueError(f"Oral text/audit mismatch at {i}")
   if audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED" or oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED":
    raise ValueError(f"Audit statuses invalid at {i}")
   alerts=list(audit.get("unsupported_additions",[]))+list(audit.get("critical_omissions",[]))
   state="AUDITED_WITH_FLAGS_REVIEW_REQUIRED" if alerts else "AUDITED_HUMAN_REVIEW_REQUIRED"
   prior.append({"turn":i,"role":role,"spoken_text":oral["spoken_text"],
     "scientific_source_sha256":sha,"audit_alerts":alerts})
  elif i==4:
   # 010D4 approved? No: audited, still human-review-required.
   op=Path(workdir)/"Boke-010D4-ESG-Oral.json"
   ap=Path(workdir)/"Boke-010D4-ESG-Audit.json"
   if op.exists() and ap.exists():
    oral,audit=read(op),read(ap)
    if (oral.get("source_sha256")!=sha or audit.get("source_sha256")!=sha or
        audit.get("oral_sha256")!=hashtext(oral.get("spoken_text",""))):
     raise ValueError("ESG candidate/audit mismatch")
    if oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED":
     raise ValueError("Invalid ESG audit status")
    alerts=list(audit.get("unsupported_additions",[]))+list(audit.get("critical_omissions",[]))
    state="AUDITED_WITH_FLAGS_REVIEW_REQUIRED" if alerts else "AUDITED_HUMAN_REVIEW_REQUIRED"
    prior.append({"turn":i,"role":role,"spoken_text":oral["spoken_text"],
     "scientific_source_sha256":sha,"audit_alerts":alerts})
  result.append({"turn":i,"role":role,"source_sha256":sha,"source_present":True,
   "phase":"scientific_claims_to_oral","mission":MISSIONS[role],
   "status":state,"must_preserve":"TO_BE_EXTRACTED_FROM_IMMUTABLE_SOURCE",
   "redundancy_policy":"Preserve all mandatory claims; concise cross-reference to earlier statements only after scientific audit.",
   "allowed_prior_turns":[x["turn"] for x in prior if x["turn"]<i],
   "source_facts_only":True,"human_scientific_review_required":True})
 return {"schema":"TERRA_COUNCIL_010D5_WHOLE_COUNCIL_PLAN_V1",
  "status":"OFFLINE_FULL_COUNCIL_PLAN_HUMAN_REVIEW_REQUIRED",
  "turns":result,"prior_audited_context":prior,
  "turn_count":19,"available_audited_count":len(prior),
  "scientific_approval":False,"audio_authorized":False,
  "decision_authorized":False,"meta_calls":0,"elevenlabs_calls":0}
def main():
 p=argparse.ArgumentParser()
 for k in ("packets","workdir","output"):p.add_argument("--"+k,required=True)
 a=p.parse_args();data=build(read(a.packets),a.workdir)
 output=Path(a.output)
 with output.open("x",encoding="utf-8") as f:json.dump(data,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":data["status"],"turns":data["turn_count"],
  "audited":data["available_audited_count"],"remaining":19-data["available_audited_count"],
  "api_calls":0,"audio_authorized":False},ensure_ascii=False))
 for t in data["turns"]:
  print(f"T{t['turn']:02d} {t['role']:13s} {t['status']}")
if __name__=="__main__":main()
