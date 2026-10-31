"""005: Meta-grounded multi-turn dialogue preview. NO ElevenLabs."""
import argparse,json,os,urllib.request
from pathlib import Path
PROMPT="""Recompose les SIX interventions en 8 à 14 prises de parole en français naturel.
Chaque segment reprend exclusivement le contenu scientifique du même expert,
sans inventer réponse, désaccord, résultat ni consensus. La critique précède
la synthèse. Retourne uniquement du JSON:
{"segments":[{"source_turn":1,"role":"mining_industry",
"spoken_text":"...","source_excerpt":"..."}]}.
source_excerpt doit être une citation EXACTE de 35 caractères ou plus du
spoken_text original correspondant au même source_turn.
Pas de références techniques prononcées. Conserve toutes les incertitudes."""
def validate(original,result):
    ss=result.get("segments",[]) if isinstance(result,dict) else []
    if not isinstance(ss,list) or not 8<=len(ss)<=14:return ["INVALID_SEGMENT_COUNT"]
    errors=[];roles=set()
    for i,s in enumerate(ss):
        n=s.get("source_turn")
        if type(n)!=int or n not in range(1,7):
            errors.append(f"{i}:SOURCE");continue
        base=original[n-1];roles.add(n)
        if s.get("role")!=base["role"]:errors.append(f"{i}:ROLE")
        q=s.get("source_excerpt")
        if not isinstance(q,str) or len(q)<35 or q not in base["spoken_text"]:
            errors.append(f"{i}:EXCERPT")
        if not isinstance(s.get("spoken_text"),str) or not s["spoken_text"].strip():
            errors.append(f"{i}:EMPTY")
    if roles!=set(range(1,7)):errors.append("MISSING_ROLE")
    return errors
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview",action="store_true")
    mode.add_argument("--generate",action="store_true")
    a=p.parse_args()
    source=json.loads(Path(a.input).read_text(encoding="utf-8-sig"))
    original=source.get("turns",[])
    if source.get("schema")!="TERRA_VOICE_DIALOGUE_004_META_RECONSTRUCTION" or len(original)!=6:
        raise SystemExit("Required: six-turn 004 source")
    out=Path(a.output)
    if out.exists():raise SystemExit("Output exists: refusing overwrite")
    if a.preview:
        print(json.dumps({"status":"SOURCE_READY","turns":6,"meta_calls":0,"elevenlabs_calls":0}));return
    key=os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")
    if not key:raise SystemExit("Missing Meta API key")
    body={"model":a.model,"messages":[{"role":"system","content":PROMPT},
        {"role":"user","content":json.dumps(original,ensure_ascii=False)}]}
    req=urllib.request.Request("https://api.meta.ai/v1/chat/completions",
        data=json.dumps(body,ensure_ascii=False).encode("utf-8"),method="POST",
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=120) as r:answer=json.load(r)
    response=answer["choices"][0]["message"]["content"]
    if not isinstance(response,str):raise SystemExit("Unexpected model format")
    proposed=json.loads(response)
    issues=validate(original,proposed)
    result={"schema":"TERRA_VOICE_DIALOGUE_005_DRAFT","session_id":source["session_id"],
        "status":"BLOCKED_REVIEW_REQUIRED" if issues else "EDITORIAL_REVIEW_REQUIRED",
        "issues":issues,"segments":proposed.get("segments",[]),
        "tts_authorized":False,"human_approval":False,
        "fidelity_validation":"STRUCTURAL_ONLY","elevenlabs_calls":0}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":result["status"],"issues":issues,
        "segments":len(result["segments"]),"elevenlabs_calls":0},ensure_ascii=False))
if __name__=="__main__":main()
