"""HACK-016F: generate dynamic ElevenLabs payload from a verified council.

No API calls in this module. Approval is allowed only for unchanged extraction,
natural-French text, four-to-six verified turns and a separate user cost consent.
This is editorial fidelity, not independent validation of scientific conclusions.
"""
import hashlib
import json
import re
from dynamic_oral_audit import verify_oral
from dynamic_narration import build_dynamic_oral

BLOCKED=re.compile(r"[<>{}#@\\|*_]|https?://|www\.",re.I)
ENGLISH=re.compile(r"\b(the|should|with|without|evidence|missing|investigate|cannot|further|recommend|survey)\b",re.I)
DEFAULT_SPARK="TERRA_VOICE_SPARK"
DEFAULT_WONDER="TERRA_VOICE_WONDER"

def prepare_voice(trace,voice_spark,voice_wonder):
    draft=build_dynamic_oral(trace)
    checked=verify_oral(trace,draft)
    if checked["status"]!="EXACT_EXTRACTION_CHECK_PASSED":
        raise ValueError("Oral evidence fidelity requires review")
    turns=draft["turns"]
    if not 3<=len(turns)<=6:
        raise ValueError("Unsupported number of council interventions")
    if not voice_spark or not voice_wonder or voice_spark==voice_wonder:
        raise ValueError("Distinct configured voice IDs required")
    inputs=[]
    for turn in turns:
        message=turn["text_to_review"].strip()
        if not message or len(message)>1100 or BLOCKED.search(message) or ENGLISH.search(message):
            raise ValueError("Unreviewed language or technical speech content")
        if any(char.isdigit() for char in message):
            raise ValueError("Numbers need source-faithful oral normalization")
        inputs.append({"text":message,"voice_id":voice_wonder if turn["source_model"]=="muse-wonder-1.0" else voice_spark})
    if sum(len(v["text"]) for v in inputs)>2000:
        raise ValueError("Too many characters for one provider call")
    return {"session_id":trace["run_id"],"evidence_sha256":draft["evidence_sha256"],
            "script_sha256":checked["script_sha256"],
            "editorial_type":draft["type"],
            "turns":turns,"payload":{"inputs":inputs,"model_id":"eleven_v4","language_code":"fr"},
            "gate":"EXACT_EXTRACTION_CHECK_PASSED",
            "scientific_validation":"STRUCTURAL_ONLY_NOT_FIELD_VALIDATED",
            "requires_paid_consent":True}
