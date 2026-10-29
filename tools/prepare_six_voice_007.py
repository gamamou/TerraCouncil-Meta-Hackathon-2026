"""TERRA-VOICE-007: prepare six-voice dialogue batches; NO network calls."""
import argparse,json,re,hashlib
from pathlib import Path

def prepare(source,voices,limit=1850):
    turns=source.get("turns",[])
    if source.get("schema")!="TERRA_VOICE_DIALOGUE_004_META_RECONSTRUCTION" or len(turns)!=6:
        raise ValueError("Six-turn 004 draft required")
    if source.get("status")=="BLOCKED_REVIEW_REQUIRED":
        raise ValueError("Source is blocked")
    if [x.get("turn") for x in turns]!=list(range(1,7)):
        raise ValueError("Turn order invalid")
    mapped=json.loads(Path(voices).read_text(encoding="utf-8-sig"))
    roles=[x["role"] for x in turns]
    if len(set(roles))!=6:raise ValueError("Expected six unique roles")
    ids=[mapped.get(r) for r in roles]
    if not all(ids) or len(set(ids))!=6:raise ValueError("Six distinct voice IDs required")
    batches=[];current=[];count=0
    for t in turns:
        raw=t["spoken_text"]
        if not raw or re.search(r"FAITH-[A-Z0-9_-]+|BOKE-[A-Z0-9_-]+|\bAOI\b|\bUTC\b",raw):
            raise ValueError("Empty or technical speech")
        line={"turn":t["turn"],"role":t["role"],"voice_id":mapped[t["role"]],"text":raw}
        if len(raw)>limit:raise ValueError("Oversized turn; needs scientific review")
        if current and count+len(raw)>limit:
            batches.append(current);current=[];count=0
        current.append(line);count+=len(raw)
    if current:batches.append(current)
    return {"schema":"TERRA_VOICE_007_REVIEW_ONLY",
      "status":"REVIEW_REQUIRED_NOT_SENT","tts_authorized":False,
      "session_id":source["session_id"],"model_id":"eleven_v4",
      "language_code":"fr","batches":[
       {"batch":i,"characters":sum(len(x["text"]) for x in rows),
        "inputs":[{"text":x["text"],"voice_id":x["voice_id"]} for x in rows],
        "turns":[x["turn"] for x in rows]} for i,rows in enumerate(batches,1)],
      "six_roles":roles,"unique_voice_count":6,"meta_calls":0,"elevenlabs_calls":0,
      "disclaimer":"EDITORIAL_RECONSTRUCTION_NOT_VERBATIM"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--voices",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    raw=Path(a.input).read_bytes()
    source=json.loads(raw.decode("utf-8-sig"))
    result=prepare(source,a.voices)
    result["source_sha256"]=hashlib.sha256(raw).hexdigest()
    dest=Path(a.output)
    if dest.exists():raise SystemExit("Output already exists: no overwrite")
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":result["status"],"voices":6,
      "batches":len(result["batches"]),"characters":[x["characters"] for x in result["batches"]],
      "meta_calls":0,"elevenlabs_calls":0},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
