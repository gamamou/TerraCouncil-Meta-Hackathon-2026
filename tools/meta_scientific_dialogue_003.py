"""Meta scientific dialogue director. No ElevenLabs. Human review required."""
import argparse,hashlib,json,os,re,urllib.request,urllib.error
from pathlib import Path
API="https://api.meta.ai/v1/chat/completions"
INSTRUCTION="""Tu reconstruis des interventions scientifiques en dialogue oral naturel en français.
Conserve rigoureusement les six rôles et leur ordre, hypothèses, incertitudes,
chiffres essentiels, conclusions, limites et distinction local/national.
Tu peux ajouter des transitions seulement si elles sont justifiées par les
interventions. N'invente jamais faits, décisions, objections ni consensus.
Ne lis pas les identifiants de preuves; remplace AOI par périmètre étudié.
Retourne exclusivement un JSON objet {"turns":[{"turn":1,"role":"...",
"spoken_text":"...","source_evidence_ids":[]}]} avec six interventions."""
N=re.compile(r"(?<!\w)\d+(?:[,.]\d+)?\s*%?")
T=re.compile(r"\b(?:AOI|UTC)\b|FAITH-[A-Z0-9_-]+|BOKE-[A-Z0-9_-]+")
def inspect(d):
    turns=d.get("turns",[])
    if d.get("schema")!="TERRA_VOICE_DIALOGUE_001_DRAFT" or len(turns)!=6:raise ValueError("Expected six-turn 001 draft")
    if [t.get("turn") for t in turns]!=[1,2,3,4,5,6]:raise ValueError("Incorrect order")
    if len({t.get("role") for t in turns})!=6:raise ValueError("Duplicate roles")
    return turns
def check(source,proposal):
    dest=proposal.get("turns",[]) if isinstance(proposal,dict) else []
    if not isinstance(dest,list) or len(dest)!=6:return ["WRONG_TURN_COUNT"]
    issues=[]
    for a,b in zip(source,dest):
        i=a["turn"];spoken=b.get("spoken_text")
        if b.get("turn")!=i or b.get("role")!=a["role"]:issues.append(f"TURN_{i}_IDENTITY")
        if b.get("source_evidence_ids")!=a["source_evidence_ids"]:issues.append(f"TURN_{i}_EVIDENCE")
        if not isinstance(spoken,str) or not spoken.strip():issues.append(f"TURN_{i}_EMPTY");continue
        if T.search(spoken):issues.append(f"TURN_{i}_TECHNICAL_SPEECH")
        if len(spoken)>2200:issues.append(f"TURN_{i}_LONG")
        before=set(N.findall(a["original_text"]));after=set(N.findall(spoken))
        if before-after:issues.append(f"TURN_{i}_NUMBERS_OMITTED")
        if after-before:issues.append(f"TURN_{i}_NUMBERS_ADDED")
    return issues
def run():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    p.add_argument("--model",default="muse-wonder-1.0")
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument("--preview",action="store_true");mode.add_argument("--generate",action="store_true")
    a=p.parse_args();raw=Path(a.input).read_bytes();src=json.loads(raw.decode("utf-8-sig"));original=inspect(src)
    dest=Path(a.output)
    if dest.exists():raise SystemExit("Output exists: will not overwrite")
    if a.preview:
        print(json.dumps({"status":"SOURCE_READY","turns":6,"sha256":hashlib.sha256(raw).hexdigest(),"meta_calls":0,"elevenlabs_calls":0},indent=2));return
    key=os.getenv("META_API_KEY") or os.getenv("META_AI_API_KEY")
    if not key:raise SystemExit("META_API_KEY missing")
    clean=[{k:t[k] for k in ("turn","role","original_text","source_evidence_ids")} for t in original]
    payload={"model":a.model,"temperature":0.25,"messages":[{"role":"system","content":INSTRUCTION},{"role":"user","content":json.dumps(clean,ensure_ascii=False)}]}
    req=urllib.request.Request(API,method="POST",data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=120) as response:answer=json.load(response)
    except urllib.error.HTTPError as e:raise SystemExit(f"Meta HTTP {e.code}; not sending to ElevenLabs") from None
    content=answer["choices"][0]["message"]["content"]
    if isinstance(content,list):content="".join(x.get("text","") for x in content)
    content=content.strip()
    if content.startswith(chr(96)*3):
        content=re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$","",content,flags=re.I)
    try:proposal=json.loads(content)
    except json.JSONDecodeError:raise SystemExit("Response not JSON; no output") from None
    problems=check(original,proposal)
    out={"schema":"TERRA_VOICE_DIALOGUE_003_META_DRAFT","source_sha256":hashlib.sha256(raw).hexdigest(),"session_id":src["session_id"],"model":a.model,
      "status":"BLOCKED_REVIEW_REQUIRED" if problems else "EDITORIAL_REVIEW_REQUIRED","issues":problems,"tts_authorized":False,"human_approval":False,
      "reconstruction_type":"EDITORIAL_NOT_VERBATIM","turns":proposal.get("turns",[])}
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":out["status"],"issues":problems,"output":str(dest),"elevenlabs_calls":0},ensure_ascii=False,indent=2))
if __name__=="__main__":run()
