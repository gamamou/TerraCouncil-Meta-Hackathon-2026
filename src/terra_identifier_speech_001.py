"""Pronounce only simple underscore-separated alphabetical identifiers.

Keep original scientific text unchanged outside the oral render.
Reject identifiers containing numbers, repeated underscores or risky symbols.
"""
import re
TOKEN=re.compile(r"(?<![\w])([A-Za-zÀ-ÿ]+(?:_[A-Za-zÀ-ÿ]+)+)(?![\w])")
ANY_UNDERSCORE=re.compile(r"\S*_\S*")
def normalize_identifiers(text):
    if not isinstance(text,str):raise ValueError("Invalid text")
    audit=[]
    def replace(m):
        original=m.group(1)
        parts=original.split("_")
        if not all(2<=len(p)<=40 for p in parts):
            raise ValueError("Ambiguous underscore identifier")
        spoken=" ".join(parts)
        audit.append({"original_sha_only":True,"spoken":"UNDERSCORE_AS_PAUSE","occurrences":1})
        return spoken
    rendered=TOKEN.sub(replace,text)
    if ANY_UNDERSCORE.search(rendered):
        raise ValueError("Unsafe technical identifier requires review")
    return rendered,audit
