"""010D: source-locked scientific claim extraction, oral adaptation and audit.

Each stage is one explicitly approved Meta request. No retries or audio.
This is a 010D pilot for the ESG turn 4, not a completed scientific validation.
"""
import argparse,hashlib,json,os,re,urllib.request
from pathlib import Path
from meta_scientific_dialogue_004 import parse_json

API="https://api.meta.ai/v1/chat/completions"
SCHEMA="TERRA_COUNCIL_010D_V1"
EXTRACT="""Tu es analyste de fidelite scientifique, non orateur.
Pour l'intervention fournie, extrais les propositions distinctes qui devront
survivre a la narration orale. Ne cree aucune information nouvelle.
Chaque proposition contient une courte source_quote COPIEE EXACTEMENT du texte
original, un meaning fidele, importance parmi MUST_KEEP, MAY_SUMMARIZE,
METADATA_ONLY et un identifiant C01, C02...
MUST_KEEP: conclusions, distinctions de preuves, limites, garanties critiques.
MAY_SUMMARIZE: details explicatifs non indispensables a prononcer mot pour mot.
METADATA_ONLY: valeurs, coordonnees et identifiants precis a conserver en
provenance sans obligation de lecture a voix haute.
Une assertion numerique peut avoir sa proposition conceptuelle MUST_KEEP et
sa valeur exacte METADATA_ONLY. Ne pas transformer une classe WorldCover
en biodiversite observee ou WorldPop en personnes affectees.
Retourne JSON strict: {"claims":[{"claim_id":"C01","source_quote":"...",
"meaning":"...","importance":"MUST_KEEP","spoken_requirement":"..."}]}."""
ORAL="""Tu es realisateur de dialogue scientifique, pas lecteur de rapport.
Recompose une intervention ORALE CONVERSATIONNELLE a partir des propositions
extraites et du texte original. Ce n'est PAS une paraphrase phrase par phrase.
Preserve toutes les propositions MUST_KEEP. MAY_SUMMARIZE peut etre condense.
METADATA_ONLY reste dans le dossier FSDC et ne doit pas etre lu tel quel.
N'invente ni faits, ni donnees, ni accords, ni contradictions, ni autorisations.
Ne change ni le niveau de preuve, ni la position de l'expert. Retenir que
les donnees sont exploratoires non validees sur le terrain. Pas de chiffres
techniques non necessaires, pas d'AOI ou codes FSDC prononces.
Texte de 75 a 135 mots environ; ton naturel de conseil scientifique.
Retourne JSON strict: {"role":"esg","spoken_text":"...",
"covered_claim_ids":["C01"],"metadata_omitted_claim_ids":["C02"]}.
Liste exclusivement les identifiants des propositions effectivement couvertes
ou maintenues hors de la narration."""
AUDIT="""Tu es auditeur semantique critique. Compare EXACTEMENT chaque proposition
du manifeste avec le nouveau texte oral. Juge le sens, pas les mots exacts.
N'accorde pas PRESERVED si la qualification, la portee, la condition ou le
niveau de preuve a change. Les valeurs numeriques classees METADATA_ONLY
peuvent etre omises oralement si le sens qualitatif MUST_KEEP est preserve.
Identifie toute invention, contradiction, perte de reserve ou generalisation
non justifiee. N'approuve pas le texte de ta propre autorite.
Retourne JSON strict {"assessments":[{"claim_id":"C01",
"verdict":"PRESERVED","reason":"..."}],
"unsupported_additions":[],"critical_omissions":[],
"numerical_mutations":[],"overall":"REVIEW_REQUIRED"}.
Verdicts possibles PRESERVED, PARTIAL, OMITTED, CONTRADICTED, METADATA_OMITTED.
Inclus exactement tous les claim_id une fois."""
def read(path):
 return json.loads(Path(path).read_text(encoding="utf-8-sig"))
def stagepath(root,stage):
 return root / ("Boke-010D-ESG-"+stage+".json")
def source_info(packets):
 if packets.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or len(packets.get("turns",[]))!=19:
  raise ValueError("009O-A source required")
 t=packets["turns"][3]
 if (t.get("turn"),t.get("speaker"))!=(4,"esg"):raise ValueError("Expected ESG turn 4")
 src=t["scientific_source_text"]
 return src,hashlib.sha256(src.encode("utf-8")).hexdigest()
def validate_claims(cla,src):
 items=cla.get("claims") if isinstance(cla,dict) else None
 if not isinstance(items,list) or not 4<=len(items)<=24:raise ValueError("Claims must contain 4..24 entries")
 allowed={"MUST_KEEP","MAY_SUMMARIZE","METADATA_ONLY"}
 ids=set()
 for c in items:
  if not isinstance(c,dict):raise ValueError("Invalid claim")
  key=c.get("claim_id");quote=c.get("source_quote")
  if not isinstance(key,str) or not re.fullmatch(r"C\d{2}",key) or key in ids:
   raise ValueError("Invalid claim IDs")
  ids.add(key)
  if not isinstance(quote,str) or not quote.strip() or quote not in src:raise ValueError("Quote not in source")
  if c.get("importance") not in allowed or not isinstance(c.get("meaning"),str) or not c["meaning"].strip():
   raise ValueError("Invalid claim meaning")
 if not any(x["importance"]=="MUST_KEEP" for x in items):raise ValueError("Missing essential claims")
 return items
def verify_oral(oral,claims):
 if not isinstance(oral,dict) or oral.get("role")!="esg" or not isinstance(oral.get("spoken_text"),str) or not oral["spoken_text"].strip():
  raise ValueError("Invalid ESG oral candidate")
 ids={x["claim_id"] for x in claims}
 for key in ("covered_claim_ids","metadata_omitted_claim_ids"):
  values=oral.get(key)
  if not isinstance(values,list) or not set(values).issubset(ids):raise ValueError("Invalid claim mapping")
 return True
def verify_audit(audit,claims):
 if not isinstance(audit,dict):raise ValueError("Invalid audit")
 rows=audit.get("assessments")
 if not isinstance(rows,list) or len(rows)!=len(claims):raise ValueError("Incomplete audit")
 wanted={x["claim_id"] for x in claims}
 if {x.get("claim_id") for x in rows}!=wanted:raise ValueError("Audit missing claims")
 if len({x.get("claim_id") for x in rows})!=len(rows):raise ValueError("Duplicated claim")
 if any(x.get("verdict") not in {"PRESERVED","PARTIAL","OMITTED","CONTRADICTED","METADATA_OMITTED"} for x in rows):
  raise ValueError("Invalid verdict")
 return True
def call(model,effort,system,data,out):
 key=os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")
 if not key:raise SystemExit("META_API_KEY missing")
 payload={"model":model,"reasoning_effort":effort,"temperature":0.2,
  "max_tokens":6500,"messages":[{"role":"system","content":system},
   {"role":"user","content":json.dumps(data,ensure_ascii=False)}]}
 request=urllib.request.Request(API,method="POST",
  data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
  headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
 with urllib.request.urlopen(request,timeout=180) as response:raw=json.load(response)
 rawfile=out.with_name(out.stem+"-raw.json")
 with rawfile.open("x",encoding="utf-8") as f:json.dump(raw,f,ensure_ascii=False,indent=2)
 return parse_json(raw["choices"][0]["message"]["content"]),raw.get("usage")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--packets",required=True);p.add_argument("--workdir",required=True)
 p.add_argument("--stage",choices=("extract","oral","audit"),required=True)
 p.add_argument("--model",default=None);p.add_argument("--effort",default="high",
   choices=("minimal","low","medium","high","xhigh","max"))
 p.add_argument("--execute",action="store_true");p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args();src,sha=source_info(read(a.packets))
 root=Path(a.workdir);out=stagepath(root,a.stage)
 claimfile=stagepath(root,"extract");oralfile=stagepath(root,"oral")
 model=a.model or ("muse-spark-1.3" if a.stage=="audit" else "muse-wonder-1.0")
 claims=None;oral=None
 if a.stage in ("oral","audit"):
  extraction=read(claimfile)
  if extraction.get("status")!="CLAIMS_HUMAN_REVIEW_REQUIRED" or extraction.get("source_sha256")!=sha:
   raise ValueError("Extraction incomplete or stale")
  claims=validate_claims(extraction,src)
 if a.stage=="audit":
  oral=read(oralfile)
  if oral.get("status")!="ORAL_HUMAN_REVIEW_REQUIRED" or oral.get("source_sha256")!=sha:
   raise ValueError("Oral stage incomplete or stale")
  verify_oral(oral,claims)
 print(json.dumps({"status":"010D_PREVIEW","stage":a.stage,"model":model,"effort":a.effort,
   "calls_if_authorized":1,"actual_meta_calls":0,"audio_authorized":False}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit approval required")
 if out.exists():raise SystemExit("Stage file exists; inspect, do not retry")
 root.mkdir(parents=True,exist_ok=True)
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT","stage":a.stage},f)
 try:
  if a.stage=="extract":
   output,usage=call(model,a.effort,EXTRACT,{"source":src,"role":"esg"},out)
   entries=validate_claims(output,src)
   result={"claims":entries,"status":"CLAIMS_HUMAN_REVIEW_REQUIRED"}
  elif a.stage=="oral":
   output,usage=call(model,a.effort,ORAL,{"source":src,"claims":claims,"role":"esg"},out)
   verify_oral(output,claims)
   result={"role":"esg","spoken_text":output["spoken_text"],
    "covered_claim_ids":output["covered_claim_ids"],
    "metadata_omitted_claim_ids":output["metadata_omitted_claim_ids"],
    "status":"ORAL_HUMAN_REVIEW_REQUIRED"}
  else:
   output,usage=call(model,a.effort,AUDIT,{"source":src,"claims":claims,
    "spoken_text":oral["spoken_text"]},out)
   verify_audit(output,claims)
   result={**output,"status":"SEMANTIC_HUMAN_REVIEW_REQUIRED"}
 except Exception as e:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","stage":a.stage,
    "error_type":type(e).__name__,"error":str(e)[:350]}),encoding="utf-8")
  raise SystemExit("Stopped: inspect journal and raw, no automatic retry")
 result.update({"schema":SCHEMA,"stage":a.stage,"model":model,"effort":a.effort,
  "source_sha256":sha,"usage":usage,"scientific_approval":False,
  "audio_authorized":False,"decision_authorized":False})
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"status":result["status"],"stage":a.stage,"model":model,
   "source_sha256":sha,"audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
