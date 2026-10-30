"""010D6: safe staged continuation of the FSDC Council, starting at T05.

Each invocation may perform at most 3 authorized Meta calls (extract/oral/audit).
Stops on review flags, errors, stale hashes. Prior flagged interventions
are excluded from conversational context, not erased from scientific record.
No ElevenLabs, no automatic scientific approval.
"""
import argparse,hashlib,json,os
from pathlib import Path
from terra_council_010d_pipeline import read,EXTRACT,AUDIT,validate_claims,verify_audit,call
from terra_council_010d5_full_council import build,ROLES,MISSIONS
from terra_council_010d3_dialogue import path as d3path

ROLE_GUIDANCE={
 "president":"Faire une transition concise et poser une question precise sans repondre au nom des experts.",
 "mining":"Nouvelle question de methodologie miniere, sans fait de gisement suppose.",
 "environment":"Developper une contribution environnementale distincte sur habitats et eau; preuves seulement.",
 "esg":"Preciser la gouvernance des preuves, non la conformite constatee.",
 "communities":"Distinguer enquete sociale et estimation population. Ne jamais deduire des personnes affectees de WorldPop.",
 "agriculture":"Distinguer cartographie de classes et enquete agricole. Ne jamais deduire pertes ou rendements de WorldCover."
}
ORAL_SYSTEM="""Tu realises un conseil scientifique francophone, dialogue vivant et non une
suite de rapports. Role: {role}. Mission: {mission}
Instruction particuliere: {guide}
Utilise la source scientifique du tour comme limite absolue des nouvelles
affirmations. Les paroles precedentes sont un contexte de dialogue, jamais
une source de faits; ne les repete pas. Pose ou repond a une question seulement
si la source et le contexte le justifient.
Conserve le sens de toutes les propositions MUST_KEEP, y compris conditions,
incertitudes et seuil de preuve. Regroupe-les avec intelligence; ne les lis
pas mecaniquement et ne supprime aucune reserve critique.
METADATA_ONLY peut rester non prononce. Aucun impact, exposition, conformite,
autorisation ou desaccord invente. Environ 75 a 145 mots.
JSON strict: {{"role":"{role}","spoken_text":"...",
"covered_claim_ids":["C01"],"metadata_omitted_claim_ids":["C02"],
"context_reference":"reference exacte ou aucune"}}."""
def digest(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def output(root,turn,stage):return Path(root)/f"Boke-010D6-T{turn:02d}-{stage}.json"
def safe_previous(root,plan,turn):
 source={t["turn"]:t for t in plan["turns"]}
 included=[];excluded=[]
 for t in plan["prior_audited_context"]:
  if t["turn"]>=turn:continue
  item=source[t["turn"]]
  if item["status"]=="AUDITED_WITH_FLAGS_REVIEW_REQUIRED":
   excluded.append(t["turn"]);continue
  included.append({"turn":t["turn"],"role":t["role"],"spoken_text":t["spoken_text"]})
 for i in range(5,turn):
  o=output(root,i,"oral");a=output(root,i,"audit")
  if not o.exists() or not a.exists():raise ValueError(f"Missing earlier 010D6 turn {i}")
  oral,audit=read(o),read(a)
  if audit.get("oral_sha256")!=digest(oral.get("spoken_text","")):raise ValueError("Prior oral hash mismatch")
  if audit.get("source_sha256")!=oral.get("source_sha256"):raise ValueError("Prior source mismatch")
  if oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED":
   raise ValueError(f"Prior turn {i} has invalid review status")
  if not isinstance(audit.get("assessments"),list) or not audit["assessments"]:
   raise ValueError(f"Missing semantic assessments at T{i}")
  flags=audit.get("unsupported_additions",[])+audit.get("critical_omissions",[])+audit.get("numerical_mutations",[])
  bad=[x for x in audit["assessments"] if x["verdict"] in ("PARTIAL","OMITTED","CONTRADICTED")]
  if flags or bad:
   excluded.append(i)
   continue
  included.append({"turn":i,"role":oral["role"],"spoken_text":oral["spoken_text"]})
 return included,excluded
def main():
 p=argparse.ArgumentParser()
 for n in ("packets","workdir"):p.add_argument("--"+n,required=True)
 p.add_argument("--turn",type=int,required=True)
 p.add_argument("--execute",action="store_true");p.add_argument("--authorize-meta",action="store_true")
 p.add_argument("--effort",default="high",choices=("minimal","low","medium","high","xhigh","max"))
 a=p.parse_args()
 if not 5<=a.turn<=19:raise SystemExit("010D6 starts at T05")
 packets=read(a.packets);root=Path(a.workdir)
 plan=build(packets,root);t=packets["turns"][a.turn-1]
 if t.get("turn")!=a.turn or t.get("speaker") not in ROLES:raise ValueError("Invalid scientific turn")
 role=ROLES[t["speaker"]];src=t["scientific_source_text"];sha=digest(src)
 prior,excluded=safe_previous(root,plan,a.turn)
 paths={stage:output(root,a.turn,stage) for stage in ("extract","oral","audit")}
 if any(v.exists() for v in paths.values()):
  raise SystemExit("Existing stage journal detected: inspect it; no overwrite or retry")
 print(json.dumps({"status":"010D6_PREVIEW","turn":a.turn,"role":role,
  "previous_audited_context":len(prior),"excluded_flagged_turns":excluded,
  "potential_meta_calls":3,"actual_meta_calls":0,"audio_authorized":False}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit Meta authorization required")
 if not(os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta API key missing")
 root.mkdir(parents=True,exist_ok=True)
 for stage in ("extract","oral","audit"):
  out=paths[stage]
  with out.open("x",encoding="utf-8") as f:
   json.dump({"status":"CALL_IN_FLIGHT","stage":stage,"turn":a.turn},f)
  try:
   if stage=="extract":
    model="muse-wonder-1.0";system=EXTRACT;data={"source":src,"role":role}
   elif stage=="oral":
    model="muse-wonder-1.0"
    system=ORAL_SYSTEM.format(role=role,mission=MISSIONS[role],guide=ROLE_GUIDANCE[role])
    data={"source":src,"role":role,"claims":claims,"prior_audited_context":prior,
          "excluded_prior_turns_with_flags":excluded}
   else:
    model="muse-spark-1.3";system=AUDIT
    data={"source":src,"claims":claims,"spoken_text":speech}
   response,usage=call(model,a.effort,system,data,out)
   if stage=="extract":
    claims=validate_claims(response,src)
    result={"claims":claims,"status":"CLAIMS_HUMAN_REVIEW_REQUIRED"}
   elif stage=="oral":
    if response.get("role")!=role or not isinstance(response.get("spoken_text"),str) or not response["spoken_text"].strip():
     raise ValueError("Invalid speaker/oral text")
    allids={c["claim_id"] for c in claims}
    for k in ("covered_claim_ids","metadata_omitted_claim_ids"):
     ids=response.get(k)
     if not isinstance(ids,list) or not set(ids).issubset(allids):
      raise ValueError("Invalid claim mapping")
    if not isinstance(response.get("context_reference"),str):raise ValueError("Missing dialogue context reference")
    speech=response["spoken_text"];result={**response,"status":"ORAL_HUMAN_REVIEW_REQUIRED"}
   else:
    verify_audit(response,claims)
    result={**response,"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED","oral_sha256":digest(speech)}
   result.update({"schema":"TERRA_COUNCIL_010D6_V1","turn":a.turn,"role":role,
    "stage":stage,"model":model,"usage":usage,"source_sha256":sha,
    "scientific_approval":False,"decision_authorized":False,"audio_authorized":False})
   out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
   print(json.dumps({"turn":a.turn,"stage":stage,"status":result["status"]},ensure_ascii=False),flush=True)
   if stage=="audit":
    essential={c["claim_id"] for c in claims if c["importance"]=="MUST_KEEP"}
    preserved={x["claim_id"] for x in result["assessments"] if x["verdict"]=="PRESERVED"}
    flags=result.get("unsupported_additions",[])+result.get("critical_omissions",[])
    if not essential.issubset(preserved) or flags:
     print("SCIENTIFIC_REVIEW_BLOCK: audit concerns; do not continue to next turn",flush=True)
     return
  except Exception as exc:
   out.write_text(json.dumps({"status":"STOP_NO_RETRY","stage":stage,
    "error_type":type(exc).__name__,"error":str(exc)[:350]}),encoding="utf-8")
   raise SystemExit("STOP_NO_RETRY: inspect journal and raw response, no automatic retry")
 print("TURN_COMPLETE_SEMANTIC_HUMAN_REVIEW_REQUIRED; NO AUDIO",flush=True)
if __name__=="__main__":main()
