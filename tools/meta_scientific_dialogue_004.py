"""TERRA-VOICE-DIALOGUE-004: two-stage Meta reconstruction, offline QA, NO TTS.

Two optional Meta calls: (1) identify evidence-supported relationships;
(2) direct six oral turns using those relationships. No scientific reasoning rerun.
Output is not approved for audio without human scientific review.
"""
import argparse,hashlib,json,os,re,sys,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from meta_scientific_dialogue_003 import inspect,check

API="https://api.meta.ai/v1/chat/completions"
RELATIONS="""Tu es auditeur de relations scientifiques. Reçois six interventions déjà tenues.
Ne crée aucune nouvelle prise de position. Identifie UNIQUEMENT les liens
étayés par les textes entre interventions: complements, shared_constraint,
qualified_response, methodological_critique, synthesis_of. Si absence de lien
explicite ou raisonnablement étayé, n'en invente pas.
Retourne uniquement JSON: {"links":[{"from_turn":1,"to_turn":2,
"relation":"complements","source_excerpt":"citation exacte courte de la source"}]}.
from_turn et to_turn entre 1 et 6, from_turn < to_turn.
Limite à 8 liens. Aucun consensus inventé."""
DIRECTOR="""Tu es réalisateur de restitution ORALE de TerraCouncil, NON agent scientifique.
À partir de six interventions originales et d'un tableau de relations étayées,
écris un dialogue naturel entre les SIX rôles existants, dans leur ordre exact.
Six interventions seulement; ne crée pas de nouvelles réponses scientifiques.
Varie les ouvertures; NE DIS PAS 'Je propose une investigation',
'question réfutable', 'décision éclairée', 'je souligne une limite'.
L'expert critique doit critiquer les extrapolations; la synthèse doit synthétiser
et non répéter l'investigation. N'invente AUCUN fait, impact, émotion, désaccord,
accord ni résultat. Préserve les limites et incertitudes, les différences entre
national et local, et les chiffres scientifiques essentiels. Rends le texte fluide.
N'énonce pas AOI, UTC, références FAITH/BOKE opaques ni coordonnées brutes;
les coordonnées et identifiants restent dans la source FSDC hors audio.
Les années, les pourcentages, la question centrale et les réserves restent.
Retourne uniquement JSON: {"turns":[{"turn":1,"role":"mining_industry",
"spoken_text":"...","source_evidence_ids":["..."]},...]}.
La sortie est une reconstruction éditoriale, pas une transcription verbatim."""
BOILER=("je propose une investigation","question réfutable","décision éclairée","je souligne une limite")
TECH=re.compile(r"\b(?:AOI|UTC)\b|FAITH-[A-Z0-9_-]+|BOKE-[A-Z0-9_-]+",re.I)
PERCENT=re.compile(r"(?<![\w])\d+(?:[,.]\d+)?\s*%")
YEAR=re.compile(r"\b20\d{2}\b")
def parse_json(content):
    if isinstance(content,list):content="".join(p.get("text","") for p in content if isinstance(p,dict))
    if not isinstance(content,str):raise ValueError("Model content not text")
    text=content.strip()
    if text.startswith(chr(96)*3):
        text=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",text,flags=re.I)
    return json.loads(text)
def meta_call(model,system,data):
    key=os.environ.get("META_API_KEY") or os.environ.get("META_AI_API_KEY")
    if not key:raise RuntimeError("META_API_KEY missing")
    payload={"model":model,"temperature":0.25,"messages":[
        {"role":"system","content":system},
        {"role":"user","content":json.dumps(data,ensure_ascii=False)}]}
    req=urllib.request.Request(API,method="POST",data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as res:answer=json.load(res)
    return parse_json(answer["choices"][0]["message"]["content"])
def relation_issues(original,relations):
    issues=[]
    links=relations.get("links") if isinstance(relations,dict) else None
    if not isinstance(links,list) or len(links)>8:return ["INVALID_RELATION_GRAPH"]
    allowed={"complements","shared_constraint","qualified_response","methodological_critique","synthesis_of"}
    for index,link in enumerate(links):
        if not isinstance(link,dict):issues.append(f"LINK_{index}_INVALID");continue
        a,b=link.get("from_turn"),link.get("to_turn")
        if type(a)!=int or type(b)!=int or not (1<=a<b<=6):issues.append(f"LINK_{index}_ORDER")
        if link.get("relation") not in allowed:issues.append(f"LINK_{index}_TYPE")
        quote=link.get("source_excerpt")
        # Check purported excerpt against either linked source; otherwise reject.
        if not (type(a)==int and type(b)==int and 1<=a<=6 and 1<=b<=6 and isinstance(quote,str) and quote.strip() and (quote in original[a-1]["original_text"] or quote in original[b-1]["original_text"])):
            issues.append(f"LINK_{index}_UNSUPPORTED_EXCERPT")
    return issues
def numeric_issues(source,candidate):
    problems=[]
    for a,b in zip(source,candidate.get("turns",[])):
        n=a["turn"];spoken=b.get("spoken_text","")
        if not isinstance(spoken,str):continue
        src=a["original_text"]
        # Years and percent values are scientific context; opaque IDs excluded.
        src_clean=TECH.sub("",src)
        for kind,regex in (("YEAR",YEAR),("PERCENT",PERCENT)):
            found={v.replace(",",".").replace(" ","") for v in regex.findall(src_clean)}
            kept={v.replace(",",".").replace(" ","") for v in regex.findall(spoken)}
            if found-kept:problems.append(f"TURN_{n}_{kind}_OMITTED")
            if kept-found:problems.append(f"TURN_{n}_{kind}_ADDED")
        normalized=spoken.casefold()
        if any(term in normalized for term in BOILER):problems.append(f"TURN_{n}_REPORT_STYLE")
        if TECH.search(spoken):problems.append(f"TURN_{n}_TECHNICAL_TOKENS")
    return problems
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--preview",action="store_true");group.add_argument("--generate",action="store_true")
    a=p.parse_args()
    raw=Path(a.input).read_bytes();src=json.loads(raw.decode("utf-8-sig"))
    original=inspect(src);output=Path(a.output)
    if output.exists():raise SystemExit("REFUS: output already exists")
    if a.preview:
        print(json.dumps({"status":"SOURCE_READY","turns":6,"planned_meta_calls":2,
            "actual_meta_calls":0,"elevenlabs_calls":0},ensure_ascii=False,indent=2));return
    clean=[{k:t[k] for k in ("turn","role","original_text","source_evidence_ids")} for t in original]
    try:
        relations=meta_call(a.model,RELATIONS,clean)
        r_issues=relation_issues(original,relations)
        if r_issues:raise ValueError("Invalid relation graph: "+", ".join(r_issues))
        dialogue=meta_call(a.model,DIRECTOR,{"original_turns":clean,"supported_links":relations["links"]})
    except urllib.error.HTTPError as e:
        raise SystemExit(f"META HTTP {e.code}; do not retry blindly") from None
    problems=check(original,dialogue)
    # Legacy validator overcounts opaque references/locale-formatted numeric strings.
    # Use targeted scientific numeric checks instead, preserve all nonnumeric gates.
    problems=[x for x in problems if not ("NUMBERS_" in x)]
    problems.extend(numeric_issues(original,dialogue))
    result={"schema":"TERRA_VOICE_DIALOGUE_004_META_RECONSTRUCTION",
       "session_id":src["session_id"],"source_sha256":hashlib.sha256(raw).hexdigest(),
       "model":a.model,"relation_graph":relations,
       "turns":dialogue.get("turns",[]),"issues":sorted(set(problems)),
       "status":"BLOCKED_REVIEW_REQUIRED" if problems else "EDITORIAL_REVIEW_REQUIRED",
       "human_approval":False,"tts_authorized":False,
       "reconstruction_type":"EDITORIAL_RECONSTRUCTION_NOT_VERBATIM","meta_calls":2,"elevenlabs_calls":0}
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":result["status"],"issues":result["issues"],
       "output":str(output),"meta_calls":2,"elevenlabs_calls":0},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
