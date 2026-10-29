"""TERRA-VOICE-DIALOGUE-006 — preview a grounded two-voice Eleven v4 request.

No provider network call. No audio costs. No change to original science.
Pair mining (1) and critic (5) is explicitly an EDITORIAL MONTAGE,
not the actual chronological debate. Human review before any API request.
"""
import argparse,hashlib,json,re
from pathlib import Path

def make_preview(source,voices):
    turns=source.get("turns",[])
    if source.get("schema")!="TERRA_VOICE_DIALOGUE_004_META_RECONSTRUCTION" or len(turns)!=6:
        raise ValueError("Expected verified-format 004 draft")
    if source.get("status")=="BLOCKED_REVIEW_REQUIRED":
        raise ValueError("004 is blocked")
    mapping=json.loads(Path(voices).read_text(encoding="utf-8-sig"))
    a,b=turns[0],turns[4]
    if a.get("role")!="mining_industry" or b.get("role")!="scientific_critic":
        raise ValueError("Role order changed")
    if not mapping.get(a["role"]) or not mapping.get(b["role"]) or mapping[a["role"]]==mapping[b["role"]]:
        raise ValueError("Two different configured voices required")
    # Do not rewrite source: voice direction is a separate reviewable prefix.
    # v4 supports audio tags but may vary in following them.
    inputs=[{"text":a["spoken_text"],"voice_id":mapping[a["role"]]},
            {"text":"[firmly] "+b["spoken_text"],"voice_id":mapping[b["role"]]}]
    total=sum(len(x["text"]) for x in inputs)
    if total>2000:raise ValueError("Two turns exceed 2000 characters; shorten only after editorial review")
    if any(re.search(r"FAITH-[A-Z0-9_-]+|BOKE-[A-Z0-9_-]+|\\bAOI\\b|\\bUTC\\b",x["text"]) for x in inputs):
        raise ValueError("Unspoken technical tokens in preview")
    return {"schema":"TERRA_VOICE_DIALOGUE_006_REVIEW_ONLY",
      "session_id":source["session_id"],
      "source_role_turns":[1,5],"montage_not_original_sequence":True,
      "scientific_fidelity":"SOURCE_004_TEXT_NOT_FIELD_VALIDATED",
      "review_required":True,"tts_authorized":False,
      "model_id":"eleven_v4","language_code":"fr",
      "apply_text_normalization":"auto","endpoint":"/v1/text-to-dialogue/with-timestamps",
      "total_characters":total,"inputs":inputs}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--voices",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    raw=Path(a.input).read_bytes();data=json.loads(raw.decode("utf-8-sig"))
    preview=make_preview(data,a.voices)
    preview["source_file_sha256"]=hashlib.sha256(raw).hexdigest()
    output=Path(a.output)
    if output.exists():raise SystemExit("Output exists; refusing to overwrite")
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x",encoding="utf-8") as f:json.dump(preview,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":"REVIEW_ONLY_NOT_SENT","characters":preview["total_characters"],
      "voices":2,"elevenlabs_calls":0,"meta_calls":0,
      "output":str(output)},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
