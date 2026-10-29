"""TERRA-VOICE-DIALOGUE-001 — local editorial preview; no LLM, TTS or network.

Keep scientific original verbatim and immutable. The natural dialogue is a
DRAFT that needs semantic review, never silently authorizes paid synthesis.
"""
import hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_narration import build_dynamic_oral

ROLE_INTROS={
 "mining_industry":"Pour les activités minières, je commencerais par cette question.",
 "environment_climate":"Du point de vue du climat et des milieux naturels, voici le point essentiel.",
 "agriculture_land":"Pour les terres agricoles, il faut aussi regarder les impacts de terrain.",
 "energy_infrastructure":"J'ajouterais la dimension énergétique et les infrastructures.",
 "scientific_critic":"Je souhaite nuancer ces propositions sur le plan scientifique.",
 "final_synthesis":"Pour conclure notre échange, je retiens les priorités suivantes."
}
# No reference IDs dropped automatically. Contextual redaction requires independent validation.
def dialogue_preview(trace):
    draft=build_dynamic_oral(trace)
    records=[]
    for t in draft["turns"]:
        original=t["text_to_review"]
        # Strip only the syntactic boilerplate created by dynamic_narration.
        prefix="Je propose une investigation : "
        if original.startswith(prefix):
            body=original[len(prefix):]
        else:
            body=original
        lead=ROLE_INTROS.get(t["speaker"])
        if lead is None: raise ValueError("Unrecognized role; needs editorial mapping")
        oral=lead+"\n\n"+body
        # The copied body is preserved to avoid changing quantitative claims.
        if body not in original:
            raise ValueError("Source content changed")
        flags=[]
        if re.search(r"\bAOI\b|\bUTC\b|[A-Z]{2,}[-_][A-Z0-9_-]{8,}",oral):
            flags.append("TECHNICAL_REFERENCE_NEEDS_ORAL_REVIEW")
        if "Je souligne une limite :" in oral:
            flags.append("LIMITATION_TRANSITION_REQUIRES_REVIEW")
        records.append({
            "turn":t["turn"],"role":t["speaker"],
            "source_model":t["source_model"],"source_evidence_ids":t["source_evidence_ids"],
            "source_sha256":hashlib.sha256(original.encode("utf-8")).hexdigest(),
            "original_text":original,"draft_spoken_text":oral,
            "editorial_review_required":True,"review_flags":flags
        })
    return {"schema":"TERRA_VOICE_DIALOGUE_001_DRAFT",
            "session_id":draft["session_id"],
            "evidence_sha256":draft["evidence_sha256"],
            "status":"EDITORIAL_DRAFT_REVIEW_REQUIRED",
            "source_semantic_validation":"NOT_ASSESSED",
            "tts_authorized":False,"provider_calls":0,"turns":records}

def write_preview(trace,out):
    result=dialogue_preview(trace)
    path=Path(out)
    if path.exists():raise ValueError("Preview already exists; do not overwrite")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("Usage: preview_boke_dialogue.py SESSION_JSON OUTPUT_JSON")
    trace=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    x=write_preview(trace,sys.argv[2])
    print(json.dumps({"status":x["status"],"turns":len(x["turns"]),
                      "requires_review":True,"elevenlabs_calls":0},ensure_ascii=False))
