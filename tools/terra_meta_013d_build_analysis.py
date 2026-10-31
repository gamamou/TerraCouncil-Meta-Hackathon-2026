"""013D: derive a reproducible Analysis Record and readable Brief from 013C + FSDC.
No model calls. No automated scientific approval or invented recommendations.
"""
import argparse,hashlib,html,json
from pathlib import Path
from verification import gate_evidence

def fingerprint(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode("utf-8")).hexdigest()
def build(run,evidence):
 if run.get("status")!="FINISHED_PROVISIONAL_HUMAN_REVIEW":
  raise ValueError("A completed 013C live run is required")
 result=run.get("result") or {}
 if result.get("status")!="PROVISIONAL_HUMAN_REVIEW" or not result.get("decision"):
  raise ValueError("No completed provisional decision")
 details=run.get("details") or {}
 gate=gate_evidence(evidence,"mining","Boké, Guinea")
 if details.get("evidence_sha256")!=gate["evidence_sha256"]:
  raise ValueError("FSDC evidence fingerprint mismatch")
 refs={r["evidence_id"]:r for r in gate["evidence"]}
 findings={}
 for event in result.get("steps",[]):
  action=event.get("action",{}); check=event.get("verification",{})
  if action.get("tool")=="record_finding" and check.get("ok"):
   ids=action.get("evidence_ids",[])
   if len(ids)!=1 or ids[0] not in refs or action.get("summary")!=refs[ids[0]]["finding"]:
    raise ValueError("Accepted finding does not match FSDC")
   findings[check["finding_id"]]={"id":check["finding_id"],"evidence_id":ids[0],"finding":refs[ids[0]]["finding"]}
 selected=result["decision"].get("finding_ids",[])
 if not selected or any(x not in findings for x in selected):
  raise ValueError("Decision references missing findings")
 consult=result.get("consultations",[])
 record={"schema":"TERRA_META_013D_ANALYSIS_RECORD_V1","analysis_id":"AN-"+fingerprint([details,result])[:16],
  "question":details.get("question"),"evidence_sha256":gate["evidence_sha256"],
  "evidence":[{"id":r["evidence_id"],"dataset":r["dataset"],"source":r["source"],
     "validation_status":r["validation_status"],"finding":r["finding"]} for r in gate["evidence"]],
  "findings":[findings[x] for x in selected],"consultations":consult,
  "model_actions":result.get("steps",[]),
  "decision":{"summary":result["decision"]["summary"],"status":"PROVISIONAL_REQUIRES_HUMAN_REVIEW"},
  "limitations":["Source identities and exact findings checked; interpretations not independently verified.",
    "Pilot AOI is not equivalent to an administrative prefecture.","No field validation or demonstrated mining causation."],
  "decision_passport":None,"passport_reason":"No approved formal decision/action recorded; analysis alone does not create a Passport.",
  "audio_eligible":False,"audio_reason":"Fewer than two documented scientific contributing agents.",
  "validation":"STRUCTURAL_ONLY_HUMAN_REVIEW_REQUIRED"}
 return record
def render(record):
 esc=html.escape
 findings="".join("<li><strong>"+esc(x["evidence_id"])+"</strong>: "+esc(x["finding"])+"</li>" for x in record["findings"])
 sources="".join("<li>"+esc(e["id"])+" — "+esc(e["dataset"])+" ("+esc(e["validation_status"])+")</li>" for e in record["evidence"])
 limits="".join("<li>"+esc(x)+"</li>" for x in record["limitations"])
 return """<!doctype html><html lang="fr"><meta charset="utf-8"><title>TerraCouncil Scientific Brief</title>
<style>body{font:16px/1.6 Segoe UI,Arial;max-width:850px;margin:55px auto;padding:0 24px;color:#173047}
h1,h2{color:#113e54}header{border-bottom:3px solid #1b7e84}aside{border-left:4px solid #ce932c;padding:10px 16px;background:#fff8e9}
section{margin:30px 0}footer{font-size:12px;color:#556}@media print{body{margin:25px auto}}</style>
<header><h1>TerraCouncil — Scientific Brief</h1><p>Analyse """+esc(record["analysis_id"])+""" · Exploration scientifique, revue humaine requise</p></header>
<section><h2>Question</h2><p>"""+esc(record["question"] or "")+"""</p></section>
<section><h2>Observations FSDC</h2><ul>"""+findings+"""</ul></section>
<section><h2>Synthèse provisoire</h2><p>"""+esc(record["decision"]["summary"])+"""</p></section>
<section><h2>Sources</h2><ul>"""+sources+"""</ul></section>
<section><h2>Limites et vérification</h2><ul>"""+limits+"""</ul></section>
<aside>Ce document ne prouve ni impact minier, ni exposition humaine, ni validation scientifique de terrain.
Aucun Decision Passport créé : aucune décision formelle approuvée dans cette analyse.</aside>
<footer>TerraCouncil / FAITH · Rapport dérivé de la trace de modèles et des observations FSDC, sans nouvel appel IA.</footer></html>"""
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--run",required=True);p.add_argument("--evidence",required=True);p.add_argument("--output-dir",required=True)
 a=p.parse_args()
 run=json.loads(Path(a.run).read_text(encoding="utf-8-sig"))
 evidence=json.loads(Path(a.evidence).read_text(encoding="utf-8-sig"))
 record=build(run,evidence)
 folder=Path(a.output_dir);folder.mkdir(parents=True,exist_ok=True)
 target=folder/"Boke-013D-Analysis-Record.json";brief=folder/"Boke-013D-Scientific-Brief.html"
 with target.open("x",encoding="utf8") as f:json.dump(record,f,ensure_ascii=False,indent=2)
 with brief.open("x",encoding="utf8") as f:f.write(render(record))
 print("ANALYSIS_RECORD_READY",target)
 print("SCIENTIFIC_BRIEF_READY",brief)
 print("PASSPORT_NOT_CREATED_ANALYSIS_ONLY")
if __name__=="__main__":main()
