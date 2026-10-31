"""TERRA-VOICE-AUTO pronunciation blocker inventory for an existing verified HACK016 trace.

Does not print source text, numeric values, or source identifiers. No external calls.
Use after check_boke_voice_ready.py reports REVIEW_REQUIRED.
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from dynamic_narration import build_dynamic_oral
from scientific_pronunciation import TOKEN_RULES, UNSAFE, ENGLISH, NUMBER, MAX_TURN
from terra_voice_approval_002 import digest

SESSION="HACK016-20261029T001224-8479e1c5"
def diagnose(path):
    trace=json.loads(Path(path).read_text(encoding="utf-8"))
    if trace.get("run_id")!=SESSION:
        raise ValueError("Wrong session")
    draft=build_dynamic_oral(trace)
    results=[]
    for turn in draft["turns"]:
        text=turn["text_to_review"]
        normalized=text
        matched=[]
        for pattern,replacement,name in TOKEN_RULES:
            normalized,n=pattern.subn(replacement,normalized)
            if n: matched.append({"category":name,"occurrences":n})
        symbols=collections.Counter()
        for match in UNSAFE.finditer(normalized):
            token=match.group()
            if token.lower().startswith(("http","www")): category="URL"
            elif token=="\\":category="BACKSLASH"
            elif token=="|":category="PIPE"
            elif token=="*":category="ASTERISK"
            elif token=="_":category="UNDERSCORE"
            elif token in "<>":category="ANGLE_BRACKET"
            elif token in "{}":category="BRACE"
            elif token=="#":category="HASH"
            elif token=="@":category="AT_SIGN"
            else:category="OTHER_UNSAFE"
            symbols[category]+=1
        numbers=re.findall(r"\d+(?:[.,]\d+)?",normalized)
        results.append({
            "turn":turn["turn"],
            "number_tokens":len(numbers),
            "decimal_tokens":sum("." in n or "," in n for n in numbers),
            "negative_signs":normalized.count("−"),
            "percent_signs":normalized.count("%"),
            "slash_signs":normalized.count("/"),
            "unsafe_symbol_types":dict(symbols),
            "english_warning":bool(ENGLISH.search(normalized)),
            "too_long":len(normalized)>MAX_TURN,
            "known_normalizations":matched
        })
    return {"session_id":SESSION,"status":"TOKEN_DIAGNOSTIC_ONLY",
            "private_text_values_exposed":False,"provider_calls":0,"turns":results}

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python tools/check_boke_voice_tokens.py PRIVATE_SESSION_JSON")
    print(json.dumps(diagnose(sys.argv[1]),ensure_ascii=False,indent=2))
