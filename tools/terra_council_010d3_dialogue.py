"""010D3 — Sequential multi-expert scientific-to-oral engine (turns 1..3).

Stages: extract -> oral -> audit for each turn. Prior audited oral turns
are context, not fresh evidence. No audio, no scientific signoff, no retry.
"""
import argparse,hashlib,json,os
from pathlib import Path
from terra_council_010d_pipeline import (read,EXTRACT,AUDIT,call,
    validate_claims,verify_audit)

ROLES={"chair":"president","president":"president","mining":"mining",
       "environment":"environment","water_climate":"environment"}
ROLE_PROMPTS={
 "president":"""Tu es le President scientifique, facilitateur impartial.
Tu poses une question concrete aux experts. Ne monopolise pas leurs analyses,
ne donne ni conclusion prematuree ni constat de conformite. Tu exposes ce
que les preuves permettent et ne permettent pas. Une ouverture naturelle,
courte, qui appelle une vraie discussion.""",
 "mining":"""Tu es expert Mines. Apporte les besoins specifiques a la geometrie
de l'emprise, a l'exploitation et aux risques techniques. Ne repete pas les
chiffres d'occupation du sol juste presentes par le President. Ne pretends
pas disposer de donnees sur le gisement ou les operations absentes du texte.
Relie ta contribution a une question precise du President.""",
 "environment":"""Tu es expert Environnement. Apporte la dimension habitats,
eau et variabilite spatiale ou saisonniere, en restant strictement dans
les constats du texte et les limites des sources. Ne convertis jamais
WorldCover en inventaire de biodiversite, ni WorldPop en impact minier.
Reagis au raisonnement minier seulement si une proposition precedente
le permet, sinon explique ton angle complementaire sans faux desaccord."""
}
ORAL_TEMPLATE="""Tu es realisateur de dialogues scientifiques francophones, pas lecteur
de rapport. Recompose librement l'intervention dans un style oral naturel,
entre 65 et 135 mots. Respecte chaque MUST_KEEP, ne prononce pas les
METADATA_ONLY inutilement. Tu ne modifies pas les conclusions, les
conditions, les incertitudes ni le niveau de validation. Aucune observation
terrain, causalite, autorisation ou impact additionnel. Evite la structure
"ensuite, puis, enfin" monotone et les enchainements de listes.
Les paroles precedentes sont un CONTEXTE CONVERSATIONNEL, jamais une preuve
nouvelle. Fais une transition ou une reponse specifique uniquement si
justifiee par les paroles exactes. Ne repete pas leurs statistiques.
{role_prompt}
Retourne JSON strict:
{{"role":"{role}","spoken_text":"texte oral en francais",
"covered_claim_ids":["C01"],"metadata_omitted_claim_ids":["C04"],
"context_reference":"courte description de la reference reelle aux paroles precedentes, ou 'aucune'"}}."""
def packet_source(packets,turn):
 if packets.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or len(packets.get("turns",[]))!=19:
  raise ValueError("009O packet source invalid")
 t=packets["turns"][turn-1]
 if t.get("turn")!=turn:raise ValueError("Packet turn mismatch")
 original_role=t.get("speaker")
 role=ROLES.get(original_role)
 if not role:raise ValueError("Unexpected role for turn %d: %s"%(turn,original_role))
 src=t.get("scientific_source_text")
 if not isinstance(src,str) or not src.strip():raise ValueError("Empty scientific source")
 return role,src,hashlib.sha256(src.encode("utf-8")).hexdigest()
def path(workdir,turn,stage):
 return Path(workdir)/f"Boke-010D3-T{turn:02d}-{stage}.json"
def previous_context(workdir,turn):
 turns=[]
 for i in range(1,turn):
  file=path(workdir,i,"oral")
  auditfile=path(workdir,i,"audit")
  if not file.exists() or not auditfile.exists():
   raise ValueError("Previous turn requires oral plus semantic audit")
  oral,audit=read(file),read(auditfile)
  if oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or audit.get("status")!="SEMANTIC_HUMAN_REVIEW_REQUIRED":
   raise ValueError("Prior turn not audited")
  if oral.get("source_sha256")!=audit.get("source_sha256"):
   raise ValueError("Prior audit source mismatch")
  if audit.get("oral_sha256")!=hashlib.sha256(oral["spoken_text"].encode("utf-8")).hexdigest():
   raise ValueError("Previous audit refers to different oral text")
  turns.append({"turn":i,"role":oral["role"],"spoken_text":oral["spoken_text"]})
 return turns
def validate_oral(data,role,claims):
 if not isinstance(data,dict) or data.get("role")!=role:raise ValueError("Role mismatch")
 speech=data.get("spoken_text")
 if not isinstance(speech,str) or not speech.strip() or len(speech.split())>160:
  raise ValueError("Invalid oral length")
 ids={c["claim_id"] for c in claims}
 for k in ("covered_claim_ids","metadata_omitted_claim_ids"):
  values=data.get(k)
  if not isinstance(values,list) or len(set(values))!=len(values) or not set(values).issubset(ids):
   raise ValueError("Invalid claim declaration")
 if not isinstance(data.get("context_reference"),str):raise ValueError("Context description missing")
 return True
def validated_claims(workdir,turn,src,sha):
 data=read(path(workdir,turn,"extract"))
 if data.get("status")!="CLAIMS_HUMAN_REVIEW_REQUIRED" or data.get("source_sha256")!=sha:
  raise ValueError("Missing/stale extraction")
 return validate_claims(data,src)
def main():
 p=argparse.ArgumentParser()
 for n in ("packets","workdir"):p.add_argument("--"+n,required=True)
 p.add_argument("--turn",type=int,choices=(1,2,3),required=True)
 p.add_argument("--stage",choices=("extract","oral","audit"),required=True)
 p.add_argument("--effort",default="high",choices=("minimal","low","medium","high","xhigh","max"))
 p.add_argument("--execute",action="store_true");p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 role,src,sha=packet_source(read(a.packets),a.turn)
 out=path(a.workdir,a.turn,a.stage)
 if a.stage=="extract":
  system=EXTRACT;data={"source":src,"role":role}
 else:
  claims=validated_claims(a.workdir,a.turn,src,sha)
  if a.stage=="oral":
   context=previous_context(a.workdir,a.turn)
   system=ORAL_TEMPLATE.format(role=role,role_prompt=ROLE_PROMPTS[role])
   data={"source":src,"claims":claims,"role":role,
     "prior_audited_turns":context,
     "instruction":"N'invente pas d'accord, de question ou de reponse dans les paroles precedentes."}
  else:
   oral=read(path(a.workdir,a.turn,"oral"))
   if oral.get("source_sha256")!=sha or oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED":
    raise ValueError("Missing/stale oral turn")
   validate_oral(oral,role,claims)
   system=AUDIT
   data={"source":src,"claims":claims,"spoken_text":oral["spoken_text"]}
 model="muse-spark-1.3" if a.stage=="audit" else "muse-wonder-1.0"
 print(json.dumps({"status":"010D3_PREVIEW","turn":a.turn,"stage":a.stage,
  "role":role,"model":model,"calls_if_authorized":1,"actual_calls":0,
  "audio_authorized":False}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit Meta authorization required")
 if not(os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):
  raise SystemExit("Meta key missing")
 if out.exists():raise SystemExit("Output already exists; no overwrites")
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT","turn":a.turn,"stage":a.stage},f)
 try:
  result,usage=call(model,a.effort,system,data,out)
  if a.stage=="extract":
   extracted=validate_claims(result,src)
   item={"claims":extracted,"status":"CLAIMS_HUMAN_REVIEW_REQUIRED"}
  elif a.stage=="oral":
   validate_oral(result,role,claims)
   item={"spoken_text":result["spoken_text"],"role":role,
    "covered_claim_ids":result["covered_claim_ids"],
    "metadata_omitted_claim_ids":result["metadata_omitted_claim_ids"],
    "context_reference":result["context_reference"],"status":"ORAL_HUMAN_REVIEW_REQUIRED"}
  else:
   verify_audit(result,claims)
   item={**result,"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED",
    "oral_sha256":hashlib.sha256(oral["spoken_text"].encode("utf-8")).hexdigest()}
 except Exception as exc:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","turn":a.turn,
   "stage":a.stage,"error_type":type(exc).__name__,
   "error":str(exc)[:300]}),encoding="utf-8")
  raise SystemExit("Stopped; inspect journal and raw. Never retry automatically.")
 item.update({"schema":"TERRA_COUNCIL_010D3_V1","turn":a.turn,"stage":a.stage,
  "model":model,"source_sha256":sha,"usage":usage,
  "scientific_approval":False,"audio_authorized":False,"decision_authorized":False})
 out.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"status":item["status"],"turn":a.turn,"role":role,
  "stage":a.stage,"audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
