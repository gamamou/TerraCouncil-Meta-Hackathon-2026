"""009O-D2: one context-guided Muse oral candidate, without modifying council journal."""
import argparse,hashlib,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from meta_scientific_dialogue_004 import meta_call
from terra_council_009o_c_council import check_candidate
RULES="""Tu es le directeur oral, pas un expert qui invente du contenu.
Reformule UNE intervention deja ecrite. Conserve exactement les conclusions,
les incertitudes, les preuves et les limites de sa source scientifique.
Fais ressortir l'apport distinctif REEL de la discipline seulement s'il est
present dans le texte source. Les interventions precedentes servent uniquement
a eviter les repetitions et a introduire des transitions factuellement
justifiees. Ne fabrique ni accord, ni contradiction, ni question, ni resultat.
Ne lis ni coordonnees ni identifiants techniques. Evite de reciter des listes.
Ne retire pas une reserve scientifique essentielle pour raccourcir.
Retourne uniquement un objet JSON strict:
{"role":"ROLE","phase":"PHASE","spoken_text":"TEXTE ORAL"}."""
def load_and_verify(context_path,journal_path,packets_path):
 ctx=json.loads(context_path.read_text(encoding="utf-8-sig"))
 raw=journal_path.read_bytes()
 journal=json.loads(raw.decode("utf-8-sig"))
 packets=json.loads(packets_path.read_text(encoding="utf-8-sig"))
 if ctx.get("schema")!="TERRA_COUNCIL_009O_D_CONTEXT_PLAN_V1":raise ValueError("Bad context")
 if ctx.get("journal_sha256")!=hashlib.sha256(raw).hexdigest():raise ValueError("Context stale: journal changed")
 if ctx.get("next_turn")!=4 or len(journal.get("turns",[]))!=3:raise ValueError("Pilot must start at turn 4")
 if packets.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or len(packets.get("turns",[]))!=19:raise ValueError("Bad source")
 target=packets["turns"][3]
 planned=ctx["next_turn_context"]
 if (planned["immutable_scientific_source"]!=target["scientific_source_text"] or planned["speaker"]!=target["speaker"] or planned["phase"]!=target["phase"]):raise ValueError("Context and source mismatch")
 return planned,target
def main():
 p=argparse.ArgumentParser()
 for k in ("context","journal","packets","output"):p.add_argument("--"+k,required=True)
 p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 planned,item=load_and_verify(Path(a.context),Path(a.journal),Path(a.packets))
 out=Path(a.output)
 print(json.dumps({"status":"D2_PREVIEW","turn":4,"speaker":item["speaker"],
  "planned_meta_calls":1 if a.execute else 0,"elevenlabs_calls":0}),flush=True)
 if not a.execute:return
 if out.exists():raise SystemExit("Output exists; no automatic retry")
 if not a.authorize_meta:raise SystemExit("Explicit Meta authorization required")
 if not (os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta key missing")
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT","turn":4},f)
 try:
  response=meta_call("muse-wonder-1.0",RULES,{"role":item["speaker"],"phase":item["phase"],
    "source_text":item["scientific_source_text"],
    "distinctive_focus":planned["distinctive_domain_focus"],
    "preceding_turns":planned["prior_spoken_context"]})
  raw=out.with_name(out.stem+"-raw.json")
  with raw.open("x",encoding="utf-8") as f:json.dump(response,f,ensure_ascii=False,indent=2)
  entry=check_candidate(item,response)
 except Exception as e:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","turn":4,
    "error_type":type(e).__name__,"error":str(e)[:300]},ensure_ascii=False),encoding="utf-8")
  raise SystemExit("Stopped; inspect journal and raw before any retry")
 entry.update({"schema":"TERRA_COUNCIL_009O_D2_V1",
  "status":"SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED",
  "audio_authorized":False,"semantic_equivalence_verified":False,
  "journal_integrated":False,"elevenlabs_calls":0})
 out.write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"status":entry["status"],"turn":4,
  "review_flags":entry["review_flags"],"journal_integrated":False,
  "audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
