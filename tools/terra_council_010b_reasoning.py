"""010B: Muse reasoning and FSDC evidence-grounded single-call benchmark.

Offline preview by default. Live requires explicit approval; never overrides files.
Scientific claims remain SCREENED_NOT_FIELD_VALIDATED.
"""
import argparse,json,os,hashlib,urllib.request
from pathlib import Path

API="https://api.meta.ai/v1/chat/completions"
EFFORT={"minimal","low","medium","high","xhigh","max"}
MODELS={"muse-wonder-1.0","muse-spark-1.3"}
SYSTEM="""Tu es un auditeur scientifique du programme FAITH.
Tu dois raisonner UNIQUEMENT avec les preuves FSDC fournies et leurs limites.
N'invente aucun fait local, impact, causalite, conformite ni autorisation.
Les sources restent SCREENED_NOT_FIELD_VALIDATED. Ne transforme pas une somme
raster de population en recensement ou nombre de personnes affectees.
Identifie les hypotheses de travail, les lacunes et les verifications de terrain.
Cite les evidence_id des donnees utilisees. Une proposition purement
methodologique peut n'avoir aucune reference empirique.
Retourne JSON strict: {"question":"...","findings":[{"statement":"...",
"evidence_ids":["..."],"limitations":"..."}],
"priority_investigations":["..."],"decision_authorized":false}."""
def evidence_for(manifest):
 if manifest.get("schema")!="TERRA_COUNCIL_009F_EVIDENCE_V1" or manifest.get("decision_authorized") is not False:
  raise ValueError("Invalid FSDC manifest")
 claims=manifest.get("claims",[])
 allowed=[{"evidence_id":c["evidence_id"],"finding":c["finding"],
   "limitations":c.get("limitations"),"method":c.get("method")}
  for c in claims if c.get("admissibility")=="ADMISSIBLE_FOR_EXPLORATORY_DEBATE"
  and c.get("original_validation_status")=="SCREENED_NOT_FIELD_VALIDATED"]
 if not allowed or len(set(c["evidence_id"] for c in allowed))!=len(allowed):
  raise ValueError("No unique admissible evidence")
 return allowed
def check(output,allowed):
 if not isinstance(output,dict) or output.get("decision_authorized") is not False:
  raise ValueError("Decision guard failed")
 findings=output.get("findings")
 if not isinstance(findings,list):raise ValueError("Invalid findings")
 ids={x["evidence_id"] for x in allowed}
 for item in findings:
  if not isinstance(item,dict) or not isinstance(item.get("statement"),str):raise ValueError("Invalid finding")
  refs=item.get("evidence_ids")
  if not isinstance(refs,list) or not set(refs).issubset(ids):raise ValueError("Unsupported reference ID")
 return True
def payload(model,effort,question,evidence):
 if model not in MODELS or effort not in EFFORT:raise ValueError("Unsupported model/effort")
 return {"model":model,"reasoning_effort":effort,"temperature":0.2,
  "max_tokens":6500,"messages":[{"role":"system","content":SYSTEM},
   {"role":"user","content":json.dumps({"question":question,"evidence":evidence},ensure_ascii=False)}]}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--manifest",required=True);p.add_argument("--output",required=True)
 p.add_argument("--model",choices=sorted(MODELS),default="muse-spark-1.3")
 p.add_argument("--effort",choices=sorted(EFFORT),default="high")
 p.add_argument("--execute",action="store_true");p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args();raw=Path(a.manifest).read_bytes();m=json.loads(raw.decode("utf-8-sig"))
 ev=evidence_for(m);request=payload(a.model,a.effort,m["question"],ev)
 print(json.dumps({"status":"010B_PREVIEW","model":a.model,"effort":a.effort,
   "evidence_count":len(ev),"meta_calls":0,"audio_calls":0}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit Meta approval required")
 key=os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY") or os.getenv("MODEL_API_KEY")
 if not key:raise SystemExit("Meta API key not set")
 target=Path(a.output)
 if target.exists():raise SystemExit("Output exists; no retry")
 target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT"},f)
 try:
  req=urllib.request.Request(API,method="POST",
   data=json.dumps(request,ensure_ascii=False).encode("utf-8"),
   headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
  with urllib.request.urlopen(req,timeout=150) as response:reply=json.load(response)
  rawpath=target.with_name(target.stem+"-raw.json")
  with rawpath.open("x",encoding="utf-8") as f:json.dump(reply,f,ensure_ascii=False,indent=2)
  body=reply["choices"][0]["message"]["content"]
  if isinstance(body,list):body="".join(x.get("text","") for x in body if isinstance(x,dict))
  answer=json.loads(body.strip().removeprefix("`"*3+"json").removesuffix("`"*3).strip())
  check(answer,ev)
 except Exception as e:
  target.write_text(json.dumps({"status":"STOP_NO_RETRY","error_type":type(e).__name__,
    "error":str(e)[:300]}),encoding="utf-8")
  raise SystemExit("Stop: inspect response and attempt journal")
 result={"schema":"TERRA_COUNCIL_010B_REASONING_V1","status":"SCIENTIFIC_REVIEW_REQUIRED",
  "model":a.model,"effort":a.effort,"source_sha256":hashlib.sha256(raw).hexdigest(),
  "findings":answer["findings"],"priority_investigations":answer.get("priority_investigations",[]),
  "decision_authorized":False,"audio_authorized":False,"scientific_approval":False,
  "usage":reply.get("usage"),"meta_calls":1}
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"status":result["status"],"model":a.model,"effort":a.effort,
   "findings":len(result["findings"]),"audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
