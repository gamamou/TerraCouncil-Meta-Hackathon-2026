"""Read-only pinpoint audit of speech blockers for a private Boké trace.

Prints bounded contexts for human/AI inspection but NEVER sends data anywhere.
Use locally only. Do not commit output or secrets. Existing scientific records
are unchanged.
"""
import json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dynamic_narration import build_dynamic_oral
from terra_french_numbers_001 import expand_unambiguous_numbers
from terra_identifier_speech_001 import normalize_identifiers
from scientific_pronunciation import spoken_pronunciation
def main(path):
    trace=json.loads(Path(path).read_text(encoding="utf-8"))
    draft=build_dynamic_oral(trace)
    for t in draft["turns"]:
        n=t["turn"];original=t["text_to_review"]
        print("\nTURN",n,"ORIGINAL CHARS",len(original))
        try:
            spoken=spoken_pronunciation(original)
            print("READY",len(spoken["spoken_text"]))
            continue
        except ValueError as e: print("BLOCKED",str(e))
        # Reproduce token context only, not entire intervention.
        matches=[]
        for m in re.finditer(r"\S*_\S*|\d+\s*[/–−-]\s*\d+",original):
            left=max(0,m.start()-45);right=min(len(original),m.end()+45)
            matches.append(original[left:right].replace("\n"," "))
        for i,fragment in enumerate(matches[:20],1):
            print("CONTEXT",i,repr(fragment))
        print("MATCH COUNT",len(matches))
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("python inspect_voice_blockers.py SESSION_JSON")
    main(sys.argv[1])
