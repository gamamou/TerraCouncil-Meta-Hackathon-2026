"""009O-D — Context-aware scientific oral director: offline plan and QA.

This tool neither generates dialogue nor calls APIs. It prepares grounded,
speaker-specific guidance for the next oral adaptation. Source remains immutable.
"""
import argparse,collections,hashlib,json,re
from pathlib import Path

DOMAIN={
 "scientific_chair":"Facilite, questionne et synthétise; n'attribue pas d'autorisation.",
 "mining":"Géologie, hydrogéologie, géotechnique et géochimie; limites de faisabilité.",
 "environment":"Eau, biodiversité, saisons, relevés et effets environnementaux à investiguer.",
 "esg":"Gouvernance des preuves, transparence et limites des conclusions ESG.",
 "communities":"Consultation, données humaines et risques de confondre population et exposition.",
 "agriculture":"Usages des terres, systèmes agricoles et précautions sur les observations satellitaires."
}
STOP={"avec","avant","pour","dans","mais","cette","comme","nous","leur","tout","sont","sans","avoir","plus","moins","entre","donnees","terrain","source","observations","notre","votre","celles","cette","toutes","aucune","aucun","expert","science","scientifique"}
def words(s):
 return set(x for x in re.findall(r"[a-zà-ÿ]{5,}",s.casefold()) if x not in STOP)
def overlap(a,b):
 x,y=words(a),words(b)
 return round(len(x&y)/max(1,min(len(x),len(y))),3)
def plan(packets,journal):
 if packets.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or len(packets.get("turns",[]))!=19:
  raise ValueError("009O-A 19-turn source required")
 if journal.get("schema")!="TERRA_COUNCIL_009O_C_V1" or journal.get("status") not in ("PARTIAL_REVIEW_REQUIRED","COMPLETE_HUMAN_REVIEW_REQUIRED"):
  raise ValueError("Expected completed or partial 009O-C journal")
 accepted=journal.get("turns",[])
 if len(accepted)<3 or len(accepted)>19:raise ValueError("Invalid journal length")
 flags=[]
 for i,t in enumerate(accepted):
  source=packets["turns"][i]
  if t.get("turn")!=i+1 or t.get("speaker")!=source.get("speaker") or t.get("source_text")!=source.get("scientific_source_text"):
   raise ValueError("Source-journal mismatch")
  if t.get("review_flags"):flags.append({"turn":i+1,"kind":"PRIOR_QA_FLAGS","flags":t["review_flags"]})
  if i and overlap(t.get("spoken_text",""),accepted[i-1].get("spoken_text",""))>=0.57:
   flags.append({"turn":i+1,"kind":"LEXICAL_OVERLAP_REVIEW","prior":i,"score":overlap(t["spoken_text"],accepted[i-1]["spoken_text"])})
 next_i=len(accepted)
 out={"schema":"TERRA_COUNCIL_009O_D_CONTEXT_PLAN_V1",
  "status":"CONTEXT_AND_SCIENTIFIC_REVIEW_REQUIRED",
  "source_turns":19,"oral_turns_preserved":next_i,"next_turn":next_i+1 if next_i<19 else None,
  "flags":flags,"audio_authorized":False,"meta_calls":0,"elevenlabs_calls":0,
  "semantic_equivalence_verified":False}
 if next_i<19:
  target=packets["turns"][next_i]
  context=[{"turn":x["turn"],"speaker":x["speaker"],
            "spoken_excerpt":x["spoken_text"][:350]} for x in accepted[-3:]]
  out["next_turn_context"]={"turn":target["turn"],"speaker":target["speaker"],"phase":target["phase"],
   "immutable_scientific_source":target["scientific_source_text"],
   "source_evidence_ids":target.get("source_evidence_ids",[]),
   "prior_spoken_context":context,"distinctive_domain_focus":DOMAIN.get(target["speaker"],"Préserver la spécialité de cet intervenant."),
   "director_rules":[
     "Ne reformule que la position du locuteur dans son texte scientifique original.",
     "Utilise les trois interventions précédentes uniquement pour éviter les répétitions et assurer une transition justifiée.",
     "Ne fabrique ni accord, ni désaccord, ni question nouvelle, ni nouvelle affirmation.",
     "Conserve les réserves et limites scientifiques, sans lire de coordonnées ou identifiants techniques.",
     "Ne confonds pas indicateurs démographiques, personnes exposées, conformité, autorisation ou causalité.",
     "Si une réserve essentielle est déjà énoncée, ne la répète que si elle est indispensable à l'argument de ce locuteur.",
     "Une revue sémantique humaine reste obligatoire avant toute synthèse vocale."]}
 return out

def main():
 p=argparse.ArgumentParser()
 for name in ("packets","journal","output"):p.add_argument("--"+name,required=True)
 a=p.parse_args()
 packets=json.loads(Path(a.packets).read_text(encoding="utf-8-sig"))
 journal=json.loads(Path(a.journal).read_text(encoding="utf-8-sig"))
 result=plan(packets,journal)
 result["journal_sha256"]=hashlib.sha256(Path(a.journal).read_bytes()).hexdigest()
 with Path(a.output).open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print(json.dumps({"status":result["status"],"preserved":result["oral_turns_preserved"],
  "next_turn":result["next_turn"],"flags":result["flags"],"meta_calls":0,"elevenlabs_calls":0},ensure_ascii=False))
if __name__=="__main__":main()
