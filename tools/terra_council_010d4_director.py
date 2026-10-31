"""010D4: evidence-locked dialogue direction, offline diagnostic and ESG continuation.

First produce a plan from audited T01..T03 + 010D ESG source/claims.
Optionally create exactly one directed ESG oral candidate through Muse Wonder.
No automatic scientific approval, no ElevenLabs or retries.
"""
import argparse,hashlib,json,os,re
from pathlib import Path
from terra_council_010d_pipeline import read,validate_claims,call,source_info
from terra_council_010d3_dialogue import path,previous_context

STOPWORDS={"nous","vous","avec","pour","dans","plus","toute","avant","apres","cette",
"comme","sans","sont","doit","etre","dont","leur","les","des","une","aux",
"sur","par","qui","que","quel","quels","notre","votre","mais","meme",
"aussi","tout","tous","elles","leur","entre","alors","cote","cela",
"ici","etude","scientifique","donnees","expert","president"}
TOPICS={
 "study_perimeter":("périmètre","rectangulaire","emprise","rectangle","aoi"),
 "procedural_guarantees":("protocoles","traçables","tracables","brutes","revue indépendante","critères de décision"),
 "data_limitations":("worldpop","worldcover","recensement","biodiversité","exploratoires"),
 "investigation_design":("saisons","relevés","releves","terrain","hydrogéologie","géotechnique"),
 "decision_gate":("autorisation","développement","conformité","faisabilité","causalité")
}
def norm(s):
 import unicodedata
 return "".join(c for c in unicodedata.normalize("NFD",s.lower()) if unicodedata.category(c)!="Mn")
def topic_hits(s):
 x=norm(s)
 return sorted([t for t,words in TOPICS.items() if any(norm(w) in x for w in words)])
def words(s):return set(re.findall(r"[a-zà-ÿ]{4,}",norm(s)))-STOPWORDS
def plan_context(workdir,packets,claims_path):
 src,sha=source_info(packets)
 prior=previous_context(workdir,4)
 audits=[]
 for t in prior:
  i=t["turn"];au=read(path(workdir,i,"audit"))
  added=au.get("unsupported_additions",[])
  if added and not isinstance(added,list):raise ValueError("Invalid additions")
  audits.append({"turn":i,"role":t["role"],"unsupported_additions":added,
   "critical_omissions":au.get("critical_omissions",[])})
 extracted=read(claims_path)
 if extracted.get("source_sha256")!=sha or extracted.get("status")!="CLAIMS_HUMAN_REVIEW_REQUIRED":
  raise ValueError("010D ESG claim manifest does not match source")
 claims=validate_claims(extracted,src)
 must=[{"claim_id":c["claim_id"],"meaning":c["meaning"]} for c in claims if c["importance"]=="MUST_KEEP"]
 summary=[{"turn":t["turn"],"role":t["role"],"topics":topic_hits(t["spoken_text"])} for t in prior]
 return {"schema":"TERRA_COUNCIL_010D4_DIRECTOR_V1",
  "status":"DIRECTOR_PREVIEW_HUMAN_REVIEW_REQUIRED","source_sha256":sha,
  "current_turn":4,"current_role":"esg",
  "already_addressed":summary,"previous_audit_alerts":audits,
  "planned_distinct_contribution":"Expliquer les mecanismes ESG de gouvernance des preuves, sans reenumerer toutes les etudes techniques.",
  "natural_transition":"Rebondir sur les besoins de terrain cites par Mines et Environnement: qui fixe les regles, conserve la preuve et autorise une revue independante ?",
  "must_preserve":must,
  "data_not_to_invent":["conformite","exposition","impact minier","autorisation","validation terrain"],
  "provenance_only_ids":[c["claim_id"] for c in claims if c["importance"]=="METADATA_ONLY"],
  "prior_audited_turns":prior,
  "audio_authorized":False,"scientific_approval":False,"decision_authorized":False}
SYSTEM="""Tu es directeur oral d'un Conseil scientifique multi-agents.
Rends l'expert ESG vivant et intellectuellement distinct dans un dialogue.
Les paroles precedentes servent UNIQUEMENT de contexte, et ne sont pas des
preuves. Ne les paraphrase pas longuement; une courte reference suffit.
Dans cette intervention, l'apport distinct doit etre la gouvernance des preuves
(qui definit les protocoles, les criteres avant les resultats, la tracabilite,
la conservation et la revue independante), sans inventer d'institution ni de
procedure deja mise en oeuvre. Ne pas attribuer a autrui des propos absents.
Chaque proposition MUST_KEEP du dossier doit conserver son sens. Certaines
peuvent etre regroupees en une phrase concise, mais aucune ne doit disparaitre.
Les valeurs numeriques METADATA_ONLY restent hors narration.
Les limites des donnees restent explicites. Ne cree aucun fait, accord,
contradiction, exposition ou autorisation. Pas de faux dialogue.
La prose doit etre prononcable et viser 95-155 mots.
Retourne JSON strict:
{"role":"esg","spoken_text":"...","covered_claim_ids":["C01"],
"metadata_omitted_claim_ids":["C12"],"context_reference":"..."}."""
def validate_candidate(obj,claims):
 if not isinstance(obj,dict) or obj.get("role")!="esg":raise ValueError("Wrong role")
 speech=obj.get("spoken_text")
 if not isinstance(speech,str) or not 55<=len(speech.split())<=170:
  raise ValueError("Unexpected oral length")
 ids={c["claim_id"] for c in claims}
 for k in ("covered_claim_ids","metadata_omitted_claim_ids"):
  v=obj.get(k)
  if not isinstance(v,list) or len(v)!=len(set(v)) or not set(v).issubset(ids):
   raise ValueError("Invalid claim IDs")
 if not isinstance(obj.get("context_reference"),str):raise ValueError("Missing context reference")
 return True
def main():
 p=argparse.ArgumentParser()
 for n in ("packets","workdir","claims"):p.add_argument("--"+n,required=True)
 p.add_argument("--stage",choices=("director","oral"),default="director")
 p.add_argument("--effort",default="high",choices=("minimal","low","medium","high","xhigh","max"))
 p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 packets=read(a.packets)
 director=plan_context(a.workdir,packets,a.claims)
 out=Path(a.workdir)/("Boke-010D4-Director.json" if a.stage=="director" else "Boke-010D4-ESG-Oral.json")
 if a.stage=="director":
  if out.exists():raise SystemExit("Director plan already exists; no overwrite")
  with out.open("x",encoding="utf-8") as f:json.dump(director,f,ensure_ascii=False,indent=2)
  print(json.dumps({"status":director["status"],"prior_turns":3,
   "prior_audit_alerts":director["previous_audit_alerts"],
   "essential_claims":len(director["must_preserve"]),"meta_calls":0,
   "output":str(out)},ensure_ascii=False))
  return
 saved=read(Path(a.workdir)/"Boke-010D4-Director.json")
 if saved.get("schema")!=director["schema"] or saved.get("source_sha256")!=director["source_sha256"] or saved.get("prior_audited_turns")!=director["prior_audited_turns"]:
  raise ValueError("Director plan stale or changed")
 print(json.dumps({"status":"010D4_PREVIEW","stage":"oral","model":"muse-wonder-1.0",
   "meta_calls_if_authorized":1,"actual_meta_calls":0,"audio_authorized":False}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Meta authorization required")
 if not (os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta key missing")
 if out.exists():raise SystemExit("Candidate exists; no overwrite")
 src,sha=source_info(packets)
 claims=validate_claims(read(a.claims),src)
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT"},f)
 try:
  result,usage=call("muse-wonder-1.0",a.effort,SYSTEM,{"director":director,
   "scientific_source":src,"claims":claims},out)
  validate_candidate(result,claims)
 except Exception as exc:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","error_type":type(exc).__name__,
   "error":str(exc)[:350]}),encoding="utf-8")
  raise SystemExit("STOP_NO_RETRY; inspect raw and journal")
 item={**result,"schema":"TERRA_COUNCIL_010D4_ORAL_V1",
  "status":"ORAL_HUMAN_REVIEW_REQUIRED","source_sha256":sha,
  "spoken_sha256":hashlib.sha256(result["spoken_text"].encode("utf-8")).hexdigest(),
  "model":"muse-wonder-1.0","usage":usage,
  "scientific_approval":False,"audio_authorized":False,"decision_authorized":False}
 out.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"status":item["status"],"stage":"oral",
  "covered_ids":len(item["covered_claim_ids"]),"audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
