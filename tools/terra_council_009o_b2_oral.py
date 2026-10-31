"""009O-B2 — controlled oral rewrite of ONE scientific intervention.

One optional Muse call. Keeps scientific source unchanged and audio disabled.
"""
import argparse,json,os,sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from meta_scientific_dialogue_004 import meta_call

DIRECTOR="""Tu es directeur de conversation scientifique, PAS lecteur de rapport.
Adapte UNE intervention deja produite en francais oral naturel.
Conserve le sens, les positions, les recommandations, les reserves, les
limites des donnees et leur statut exploratoire. N'ajoute AUCUN fait,
desaccord, resultat, promesse, approbation ou conclusion. Ne transforme
pas une incertitude en certitude. Ne lis jamais les coordonnees de l'AOI,
les identifiants FSDC, ni les chiffres sous forme de longues listes.
Remplace les tableaux de pourcentages non essentiels par une expression
fidele telle que 'premieres observations cartographiques', tout en
conservant dans la source la valeur exacte. Garde seulement un chiffre
s'il est indispensable au raisonnement; ne l'arrondis pas arbitrairement.
Prefere des phrases courtes, des transitions orales et une question
claire pour la prochaine prise de parole si elle est deja implicite.
Pas de mise en scene inventee. Ne donne pas de nouvelles citations.
Retourne uniquement JSON strict avec:
{"role":"ROLE","phase":"PHASE","spoken_text":"TEXTE"}."""

def validate(source,number):
 if source.get("schema")!="TERRA_COUNCIL_009O_ORAL_PACKETS_V1" or source.get("audio_authorized") is not False:
  raise ValueError("Invalid 009O-A source")
 if len(source.get("turns",[]))!=19 or number!=1:
  raise ValueError("B2 pilot limited to chair opening")
 t=source["turns"][0]
 if (t.get("speaker"),t.get("phase"))!=("scientific_chair","opening"):
  raise ValueError("Expected chair opening")
 return t

def review(candidate,t):
 if not isinstance(candidate,dict) or (candidate.get("role"),candidate.get("phase"))!=(t["speaker"],t["phase"]):
  raise ValueError("Role or phase mismatch")
 text=candidate.get("spoken_text")
 if not isinstance(text,str) or not text.strip():raise ValueError("Empty oral script")
 flags=[]
 if re.search(r"\[\s*-?\d+\.?\d*\s*,\s*-?\d",text):
  flags.append("COORDINATES_STILL_SPOKEN")
 if re.search(r"\b(?:AOI|FSDC)\b",text,re.I):flags.append("OPAQUE_TECHNICAL_TERMS")
 if len(text.split())>=len(t["scientific_source_text"].split()):
  flags.append("NOT_SHORTER_THAN_ORIGINAL")
 for phrase in ("non valid","aucune autorisation"):
  if phrase not in text.casefold():flags.append("CHECK_MISSING_"+phrase.replace(" ","_"))
 return flags

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--packets",required=True)
 p.add_argument("--output",required=True)
 p.add_argument("--turn",type=int,default=1)
 p.add_argument("--execute",action="store_true")
 p.add_argument("--authorize-meta",action="store_true")
 a=p.parse_args()
 source=json.loads(Path(a.packets).read_text(encoding="utf-8-sig"))
 t=validate(source,a.turn)
 print(json.dumps({"status":"B2_PREVIEW","turn":1,"meta_calls":0,"elevenlabs_calls":0}),flush=True)
 if not a.execute:return
 if not a.authorize_meta:raise SystemExit("Explicit Meta authorization required")
 if not (os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")):raise SystemExit("Meta key missing")
 out=Path(a.output)
 if out.exists():raise SystemExit("Output already exists; do not retry")
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open("x",encoding="utf-8") as f:json.dump({"status":"CALL_IN_FLIGHT"},f)
 try:
  response=meta_call("muse-wonder-1.0",DIRECTOR,{"role":t["speaker"],"phase":t["phase"],
    "scientific_source_text":t["scientific_source_text"],
    "source_evidence_ids":t.get("source_evidence_ids",[])})
  raw=out.with_name(out.stem+"-raw.json")
  with raw.open("x",encoding="utf-8") as f:json.dump(response,f,ensure_ascii=False,indent=2)
  flags=review(response,t)
 except Exception as exc:
  out.write_text(json.dumps({"status":"STOP_NO_RETRY","error_type":type(exc).__name__,
    "error":str(exc)[:300]},ensure_ascii=False),encoding="utf-8")
  raise SystemExit("Stopped; inspect stored raw before any retry")
 result={"schema":"TERRA_COUNCIL_009O_B2_V1",
  "status":"EDITORIAL_AND_SCIENTIFIC_REVIEW_REQUIRED",
  "role":t["speaker"],"phase":t["phase"],
  "source_text":t["scientific_source_text"],
  "spoken_text":response["spoken_text"],
  "source_evidence_ids":t.get("source_evidence_ids",[]),
  "review_flags":flags,"audio_authorized":False,"elevenlabs_calls":0}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"status":result["status"],"review_flags":flags,"audio_authorized":False},ensure_ascii=False))
if __name__=="__main__":main()
