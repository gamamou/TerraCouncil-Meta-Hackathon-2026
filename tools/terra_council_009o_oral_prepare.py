"""009O-A: prepare oral-director source packets from completed council.

Offline only. No generated dialogue, Meta calls, or TTS.
"""
import argparse,hashlib,json
from pathlib import Path
def prepare(debate,audit):
    turns=debate.get("turns",[])
    if len(turns)!=19 or debate.get("status")!="SCIENTIFIC_AND_EDITORIAL_REVIEW_REQUIRED":
        raise ValueError("Completed 009M-R5 debate required")
    if audit.get("schema")!="TERRA_COUNCIL_009N_AUDIT_V1" or audit.get("issues")!=[]:
        raise ValueError("Successful 009N structural audit required")
    if audit.get("status")!="HUMAN_SCIENTIFIC_REVIEW_REQUIRED":
        raise ValueError("Expected scientific review gate")
    packets=[]
    for i,t in enumerate(turns,1):
        if not t.get("text") or not t.get("role"):
            raise ValueError("Missing source speech")
        packets.append({"turn":i,"speaker":t["role"],"phase":t["phase"],
            "scientific_source_text":t["text"],
            "source_evidence_ids":t.get("evidence_ids",[]),
            "original_review_status":t.get("review_status"),
            "oral_goal":"Rendre naturel et concis sans ajouter de fait ou de position"})
    return {"schema":"TERRA_COUNCIL_009O_ORAL_PACKETS_V1",
      "status":"ORAL_DIRECTOR_INPUT_REVIEW_REQUIRED",
      "turns":packets,"source_turn_count":19,
      "scientific_review_flags":audit.get("review_flags",[]),
      "oral_rules":[
        "Meta generates oral adaptation; never pre-assign generated statements to agents",
        "Keep exact speaker, turn order, argument, scientific uncertainty and evidence links",
        "No invented disagreement, data, project decision, ESG compliance or causal impact",
        "Avoid excessive jargon and repeated raster statistics in the spoken text",
        "Keep the FSDC evidence trace separate from spoken text",
        "Human scientific and editorial approval required before ElevenLabs"],
      "meta_calls":0,"elevenlabs_calls":0,
      "audio_authorized":False,"decision_authorized":False}
def main():
    p=argparse.ArgumentParser()
    for k in ("debate","audit","output"):p.add_argument("--"+k,required=True)
    a=p.parse_args()
    raw=Path(a.debate).read_bytes()
    audit_raw=Path(a.audit).read_bytes()
    record=prepare(json.loads(raw.decode("utf-8-sig")),
      json.loads(audit_raw.decode("utf-8-sig")))
    record["source_sha256"]=hashlib.sha256(raw).hexdigest()
    if record["source_sha256"]!=json.loads(audit_raw.decode("utf-8-sig")).get("source_sha256"):
        raise ValueError("009N audit does not match the dialogue bytes")
    output=Path(a.output)
    with output.open("x",encoding="utf-8") as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
    print(json.dumps({"status":record["status"],"turns":19,
       "meta_calls":0,"elevenlabs_calls":0,"output":str(output)},ensure_ascii=False))
if __name__=="__main__":main()
